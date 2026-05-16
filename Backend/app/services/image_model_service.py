from pathlib import Path
from io import BytesIO
import json
from threading import Lock

import numpy as np
from PIL import Image

from app.core.config import settings

try:
    import tensorflow as tf
except Exception:
    tf = None


DEFAULT_DISEASE_LABELS = [
    "Newcastle-Disease",
    "Avian-Influenza",
    "Infectious-Bursal-Disease",
    "Marek-Disease",
    "Fowl-Pox",
    "Infectious-Bronchitis",
    "Salmonellosis-Pullorum",
    "Fowl-Cholera",
    "Mycoplasmosis-CRD",
    "Infectious-Coryza",
    "Coccidiosis",
    "Healthy",
]

SUGGESTED_ACTIONS = {
    "Newcastle-Disease": "Isolate affected birds immediately. Ensure vaccination of healthy flock. Contact veterinarian urgently.",
    "Avian-Influenza": "EMERGENCY: Quarantine entire flock. Notify authorities immediately. Implement strict biosecurity measures.",
    "Infectious-Bursal-Disease": "Boost immunity with vitamins. Isolate affected birds. Consult veterinarian for treatment.",
    "Marek-Disease": "Remove paralyzed birds. Maintain strict hygiene. Vaccination prevents spread to young birds.",
    "Fowl-Pox": "Isolate affected birds. Apply iodine to lesions. Ensure clean water and nutrition.",
    "Infectious-Bronchitis": "Provide warm environment. Ensure clean air. Supplement with electrolytes.",
    "Salmonellosis-Pullorum": "Remove sick birds. Sanitize environment thoroughly. Start antibiotic treatment if needed.",
    "Fowl-Cholera": "Isolate affected birds urgently. Sanitize water systems. Give antibiotics as prescribed.",
    "Mycoplasmosis-CRD": "Improve ventilation. Isolate affected birds. Treat with appropriate antibiotics.",
    "Infectious-Coryza": "Isolate affected birds. Ensure clean water and proper nutrition. Use antibiotics if severe.",
    "Coccidiosis": "Start anticoccidial treatment immediately. Sanitize litter and water systems thoroughly.",
    "Healthy": "Continue routine monitoring and maintain current hygiene practices.",
}


def _normalize_disease_label(name: str) -> str:
    normalized = name.strip().lower().replace("_", " ").replace("-", " ").replace("/", " ").replace("(", " ").replace(")", " ")
    normalized = " ".join(normalized.split())
    aliases = {
        "newcastle disease": "Newcastle-Disease",
        "newcastle-disease": "Newcastle-Disease",
        "avian influenza": "Avian-Influenza",
        "avian-influenza": "Avian-Influenza",
        "infectious bursal disease": "Infectious-Bursal-Disease",
        "infectious-bursal-disease": "Infectious-Bursal-Disease",
        "marek disease": "Marek-Disease",
        "marek's disease": "Marek-Disease",
        "marek-disease": "Marek-Disease",
        "fowl pox": "Fowl-Pox",
        "fowl-pox": "Fowl-Pox",
        "infectious bronchitis": "Infectious-Bronchitis",
        "infectious-bronchitis": "Infectious-Bronchitis",
        "salmonellosis pullorum": "Salmonellosis-Pullorum",
        "salmonellosis/pullorum": "Salmonellosis-Pullorum",
        "salmonellosis-pullorum": "Salmonellosis-Pullorum",
        "fowl cholera": "Fowl-Cholera",
        "fowl-cholera": "Fowl-Cholera",
        "mycoplasmosis crd": "Mycoplasmosis-CRD",
        "mycoplasmosis (crd)": "Mycoplasmosis-CRD",
        "mycoplasmosis-crd": "Mycoplasmosis-CRD",
        "infectious coryza": "Infectious-Coryza",
        "infectious-coryza": "Infectious-Coryza",
        "coccidiosis": "Coccidiosis",
        "healthy": "Healthy",
    }
    return aliases.get(normalized, name.strip())

UNCERTAIN_THRESHOLD = 0.35
CNN_CONFIDENT_THRESHOLD = 0.55
CNN_TOP2_MARGIN_THRESHOLD = 0.10
REFERENCE_CONFIDENT_THRESHOLD = 0.85


def _risk_from_prediction(disease: str, confidence: float) -> str:
    critical_diseases = {"Avian-Influenza", "Newcastle-Disease"}
    high_diseases = {"Fowl-Cholera", "Salmonellosis-Pullorum", "Mycoplasmosis-CRD"}
    medium_diseases = {
        "Infectious-Bursal-Disease",
        "Infectious-Bronchitis",
        "Infectious-Coryza",
        "Marek-Disease",
        "Fowl-Pox",
        "Coccidiosis",
    }

    if disease in critical_diseases:
        return "Critical" if confidence >= 0.72 else "High"

    if disease in high_diseases:
        return "High" if confidence >= 0.72 else "Medium"

    if disease in medium_diseases:
        return "High" if confidence >= 0.82 else "Medium"

    if disease in ("Healthy", "Uncertain", "Uncertain prediction"):
        return "Low"

    if confidence >= 0.85:
        return "Critical"
    if confidence >= 0.70:
        return "High"
    if confidence >= 0.45:
        return "Medium"
    return "Low"


def _calibrate_confidence(raw_confidence: float, match_type: str, top2_margin: float | None = None) -> float:
    raw_confidence = max(0.0, min(1.0, float(raw_confidence)))

    if match_type == "image_reference":
        calibrated = 0.55 + max(0.0, raw_confidence - 0.85) * (0.25 / 0.15)
        return round(min(0.82, max(0.55, calibrated)), 4)

    if match_type.startswith("cnn"):
        margin = max(0.0, min(0.3, float(top2_margin or 0.0)))
        calibrated = 0.40 + (raw_confidence * 0.45) + (margin * 0.15)
        return round(min(0.89, max(0.35, calibrated)), 4)

    if match_type == "feature_based":
        calibrated = 0.40 + (raw_confidence * 0.45)
        return round(min(0.88, max(0.30, calibrated)), 4)

    return round(raw_confidence, 4)


def _preprocess_image(file_bytes: bytes) -> np.ndarray:
    img = Image.open(BytesIO(file_bytes)).convert("RGB").resize((224, 224), Image.LANCZOS)
    return np.array(img, dtype=np.float32) / 255.0


def _load_label_metadata(model_path: Path) -> dict:
    metadata_path = model_path.with_name(f"{model_path.stem}_labels.json")
    if not metadata_path.exists():
        return {
            "labels": DEFAULT_DISEASE_LABELS,
            "input_range": "0_255",
        }

    try:
        with metadata_path.open("r", encoding="utf-8") as handle:
            metadata = json.load(handle)
    except Exception:
        return {
            "labels": DEFAULT_DISEASE_LABELS,
            "input_range": "0_255",
        }

    labels = metadata.get("labels") or metadata.get("class_names") or DEFAULT_DISEASE_LABELS
    labels = [_normalize_disease_label(label) for label in labels]
    return {
        **metadata,
        "labels": labels,
        "input_range": metadata.get("input_range", "0_1"),
    }


def _feature_based_predict(image_array: np.ndarray, labels: list[str]) -> np.ndarray:
    n = len(labels)
    canonical_index = {name: i for i, name in enumerate(labels)}
    probs = np.full(n, 0.01, dtype=np.float64)

    red_mean = float(np.mean(image_array[:, :, 0]))
    green_mean = float(np.mean(image_array[:, :, 1]))
    blue_mean = float(np.mean(image_array[:, :, 2]))
    mean = float(np.mean(image_array))

    grayscale = np.mean(image_array, axis=2)
    contrast = float(np.std(grayscale))
    edges_h = np.abs(grayscale[1:, :] - grayscale[:-1, :])
    edges_v = np.abs(grayscale[:, 1:] - grayscale[:, :-1])
    edge_density = float(np.mean(np.concatenate([edges_h.flatten(), edges_v.flatten()])))

    redness = red_mean - green_mean
    yellowness = (red_mean + green_mean) - blue_mean

    def boost(label: str, value: float) -> None:
        idx = canonical_index.get(label)
        if idx is not None:
            probs[idx] += value

    if mean < 0.25 and edge_density < 0.08:
        boost("Newcastle-Disease", 0.35)
    if redness > 0.25 and contrast > 0.15:
        boost("Avian-Influenza", 0.40)
    if 0.55 < mean < 0.70 and contrast < 0.10:
        boost("Infectious-Bursal-Disease", 0.30)
    if 0.30 < mean < 0.45 and contrast > 0.08:
        boost("Marek-Disease", 0.25)
    if mean > 0.80 and edge_density < 0.05:
        boost("Fowl-Pox", 0.35)
    if red_mean > 0.50 and green_mean < 0.45 and edge_density > 0.06:
        boost("Infectious-Bronchitis", 0.28)
    if redness > 0.30 and mean > 0.50:
        boost("Salmonellosis-Pullorum", 0.32)
    if 0.35 < mean < 0.55 and edge_density > 0.10:
        boost("Fowl-Cholera", 0.30)
    if mean > 0.85 and edge_density > 0.06:
        boost("Mycoplasmosis-CRD", 0.28)
    if yellowness > 0.10 and edge_density > 0.08:
        boost("Infectious-Coryza", 0.25)
    if yellowness > 0.35 and blue_mean < 0.30 and edge_density > 0.08:
        boost("Coccidiosis", 0.38)
    if 0.60 < mean < 0.80 and redness < 0.15 and 0.05 < contrast < 0.15:
        boost("Healthy", 0.30)

    return probs / probs.sum()


class ImageDiseasePredictor:
    def __init__(self, model_path: str | None = None):
        self.model = None
        self.model_path = Path(model_path or settings.IMAGE_MODEL_PATH)
        self.metadata = _load_label_metadata(self.model_path)
        self.labels = list(self.metadata["labels"])

        self._model_loaded = False
        self._load_lock = Lock()

    def _ensure_model_loaded(self) -> None:
        if self._model_loaded:
            return

        with self._load_lock:
            if self._model_loaded:
                return

            if tf is not None and self.model_path.exists():
                try:
                    self.model = tf.keras.models.load_model(self.model_path)
                except Exception:
                    self.model = None

            self._model_loaded = True

    def _cnn_input(self, image_array: np.ndarray) -> np.ndarray:
        if self.metadata.get("input_range") == "0_255":
            image_array = image_array * 255.0
        return np.expand_dims(image_array, axis=0)

    def _result(self, disease: str, confidence: float, match_type: str) -> dict:
        display_confidence = _calibrate_confidence(confidence, match_type)
        return {
            "disease_name": disease,
            "confidence": display_confidence,
            "risk_level": _risk_from_prediction(disease, display_confidence),
            "suggested_action": SUGGESTED_ACTIONS.get(
                disease,
                "Consult a veterinarian and collect clearer images before taking action.",
            ),
            "match_type": match_type,
        }

    def _predict_with_cnn(self, image_array: np.ndarray) -> tuple[str, float, float] | None:
        self._ensure_model_loaded()
        if self.model is None:
            return None

        try:
            probs = self.model.predict(self._cnn_input(image_array), verbose=0)[0]
        except Exception:
            return None

        probs = np.array(probs, dtype=np.float64)
        if probs.size != len(self.labels) or probs.sum() <= 0:
            return None

        probs = probs / probs.sum()
        best_idx = int(np.argmax(probs))
        sorted_probs = np.sort(probs)
        top2_margin = float(sorted_probs[-1] - sorted_probs[-2]) if len(sorted_probs) > 1 else float(sorted_probs[-1])
        return self.labels[best_idx], float(probs[best_idx]), top2_margin

    def _predict_with_reference(self, file_bytes: bytes) -> dict | None:
        try:
            from app.services.image_reference_matcher import reference_matcher

            matched_disease, similarity_score, _ = reference_matcher.find_best_match(file_bytes)
        except Exception:
            return None

        if (
            matched_disease
            and matched_disease in DEFAULT_DISEASE_LABELS
            and similarity_score >= REFERENCE_CONFIDENT_THRESHOLD
        ):
            confidence = min(0.97, max(0.55, similarity_score))
            return self._result(matched_disease, confidence, "image_reference")

        return None

    def predict(self, file_bytes: bytes) -> dict:
        image_array = _preprocess_image(file_bytes)

        cnn_prediction = self._predict_with_cnn(image_array)
        if cnn_prediction is not None:
            disease, confidence, top2_margin = cnn_prediction
            if confidence >= CNN_CONFIDENT_THRESHOLD and top2_margin >= CNN_TOP2_MARGIN_THRESHOLD:
                return self._result(disease, confidence, "cnn")

        reference_prediction = self._predict_with_reference(file_bytes)
        if reference_prediction is not None:
            return reference_prediction

        if cnn_prediction is not None:
            disease, confidence, _ = cnn_prediction
            if confidence >= UNCERTAIN_THRESHOLD:
                return self._result(disease, confidence, "cnn_low_confidence")

        probs = _feature_based_predict(image_array, self.labels)
        best_idx = int(np.argmax(probs))
        confidence = float(probs[best_idx])
        if confidence < UNCERTAIN_THRESHOLD:
            return _uncertain_result()

        return self._result(self.labels[best_idx], confidence, "feature_based")


def _uncertain_result() -> dict:
    return {
        "disease_name": "Uncertain prediction",
        "confidence": 0.0,
        "risk_level": "Low",
        "suggested_action": "The image could not be classified with sufficient confidence. Please upload a clearer image or consult a veterinarian.",
        "match_type": "uncertain",
    }


predictor_instance: ImageDiseasePredictor | None = None
predictor_lock = Lock()


def get_predictor() -> ImageDiseasePredictor:
    global predictor_instance
    if predictor_instance is None:
        with predictor_lock:
            if predictor_instance is None:
                predictor_instance = ImageDiseasePredictor()
    return predictor_instance
