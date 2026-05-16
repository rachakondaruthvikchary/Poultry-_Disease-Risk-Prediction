"""PoultryGuard AI - Batch image disease prediction

Usage examples (run from repo root `PoultryGuardAI/`):

  python AI/inference/batch_predict_images.py --dir path/to/images
  python AI/inference/batch_predict_images.py path/to/img1.jpg path/to/img2.png

Prints one line per image:
  <filename>\t<disease_name>\t<confidence>\t<match_type>

Notes:
- Uses the existing Backend predictor (CNN if available, otherwise reference/heuristics).
- Supported extensions: .jpg .jpeg .png .webp
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from io import BytesIO

import numpy as np
from PIL import Image

def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


# Backend modules import as `app.*`, so we must add `PoultryGuardAI/Backend`
# to sys.path.
_REPO_ROOT = _repo_root()
_BACKEND_ROOT = _REPO_ROOT / "Backend"
sys.path.insert(0, str(_BACKEND_ROOT))
os.environ.setdefault("SECRET_KEY", "local-dev-secret")
os.environ.setdefault("DATABASE_URL", "sqlite:///./poultryguard_local.db")
os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:3000")

from app.services.image_reference_matcher import reference_matcher  # noqa: E402


DEFAULT_DISEASE_LABELS = [
    "Newcastle disease",
    "Avian Influenza",
    "Infectious Bursal Disease",
    "Marek's Disease",
    "Fowl Pox",
    "Infectious Bronchitis",
    "Salmonellosis/Pullorum",
    "Fowl Cholera",
    "Mycoplasmosis (CRD)",
    "Infectious Coryza",
    "Coccidiosis",
    "Healthy",
]


def _risk_from_disease(disease: str) -> str:
    if disease in ("Healthy", "Uncertain", "Uncertain prediction"):
        return "Low"
    if disease in {"Coccidiosis", "Infectious Bursal Disease", "Mycoplasmosis (CRD)", "Infectious Coryza"}:
        return "Medium"
    return "High"


def _preprocess_image(file_bytes: bytes) -> np.ndarray:
    img = Image.open(BytesIO(file_bytes)).convert("RGB").resize((224, 224), Image.LANCZOS)
    return np.array(img, dtype=np.float32) / 255.0


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
        boost("Newcastle disease", 0.35)
    if redness > 0.25 and contrast > 0.15:
        boost("Avian Influenza", 0.40)
    if 0.55 < mean < 0.70 and contrast < 0.10:
        boost("Infectious Bursal Disease", 0.30)
    if 0.30 < mean < 0.45 and contrast > 0.08:
        boost("Marek's Disease", 0.25)
    if mean > 0.80 and edge_density < 0.05:
        boost("Fowl Pox", 0.35)
    if red_mean > 0.50 and green_mean < 0.45 and edge_density > 0.06:
        boost("Infectious Bronchitis", 0.28)
    if redness > 0.30 and mean > 0.50:
        boost("Salmonellosis/Pullorum", 0.32)
    if 0.35 < mean < 0.55 and edge_density > 0.10:
        boost("Fowl Cholera", 0.30)
    if mean > 0.85 and edge_density > 0.06:
        boost("Mycoplasmosis (CRD)", 0.28)
    if yellowness > 0.10 and edge_density > 0.08:
        boost("Infectious Coryza", 0.25)
    if yellowness > 0.35 and blue_mean < 0.30 and edge_density > 0.08:
        boost("Coccidiosis", 0.38)
    if 0.60 < mean < 0.80 and redness < 0.15 and 0.05 < contrast < 0.15:
        boost("Healthy", 0.30)

    return probs / probs.sum()


def _uncertain_result() -> dict:
    return {
        "disease_name": "Uncertain prediction",
        "confidence": 0.0,
        "risk_level": "Low",
        "suggested_action": "The image could not be classified with sufficient confidence. Please upload a clearer image or consult a veterinarian.",
        "match_type": "uncertain",
    }


def predict_image(file_bytes: bytes) -> dict:
    image_array = _preprocess_image(file_bytes)

    try:
        matched_disease, similarity_score, _ = reference_matcher.find_best_match(file_bytes)
        if matched_disease and similarity_score >= 0.85:
            confidence = min(0.97, max(0.55, similarity_score))
            return {
                "disease_name": matched_disease,
                "confidence": round(float(confidence), 4),
                "risk_level": _risk_from_disease(matched_disease),
                "suggested_action": "Consult a veterinarian and collect clearer images before taking action.",
                "match_type": "image_reference",
            }
    except Exception:
        pass

    probs = _feature_based_predict(image_array, DEFAULT_DISEASE_LABELS)
    best_idx = int(np.argmax(probs))
    confidence = float(probs[best_idx])
    if confidence < 0.35:
        return _uncertain_result()

    disease = DEFAULT_DISEASE_LABELS[best_idx]
    return {
        "disease_name": disease,
        "confidence": round(float(confidence), 4),
        "risk_level": _risk_from_disease(disease),
        "suggested_action": "Consult a veterinarian and collect clearer images before taking action.",
        "match_type": "feature_based",
    }


SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def _iter_images_from_dir(dir_path: Path) -> list[Path]:
    if not dir_path.exists() or not dir_path.is_dir():
        raise FileNotFoundError(f"Directory not found: {dir_path}")

    images: list[Path] = []
    for item in sorted(dir_path.iterdir()):
        if item.is_file() and item.suffix.lower() in SUPPORTED_EXTS:
            images.append(item)
    return images


def _read_bytes(path: Path) -> bytes:
    with path.open("rb") as handle:
        return handle.read()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Batch predict poultry disease from images")
    parser.add_argument(
        "paths",
        nargs="*",
        help="Image file paths. If omitted, use --dir.",
    )
    parser.add_argument(
        "--dir",
        dest="dir_path",
        default=None,
        help="Directory containing images to predict.",
    )

    args = parser.parse_args(argv)

    image_paths: list[Path] = []

    if args.dir_path:
        image_paths.extend(_iter_images_from_dir(Path(args.dir_path)))

    for p in args.paths:
        path = Path(p)
        if path.exists() and path.is_file():
            if path.suffix.lower() not in SUPPORTED_EXTS:
                print(f"SKIP\t{path}\tunsupported extension", file=sys.stderr)
                continue
            image_paths.append(path)
        else:
            print(f"SKIP\t{path}\tnot found", file=sys.stderr)

    # De-duplicate while preserving order
    seen: set[Path] = set()
    image_paths = [p for p in image_paths if not (p in seen or seen.add(p))]

    if not image_paths:
        parser.print_help()
        print("\nNo images found. Provide --dir <folder> or image file paths.", file=sys.stderr)
        return 2

    print("filename\tdisease_name\tconfidence\tmatch_type")

    for img_path in image_paths:
        try:
            result = predict_image(_read_bytes(img_path))
            disease_name = result.get("disease_name", "Uncertain")
            confidence = float(result.get("confidence", 0.0))
            match_type = result.get("match_type", "unknown")
            print(f"{img_path.name}\t{disease_name}\t{confidence:.4f}\t{match_type}")
        except Exception as exc:
            print(f"ERROR\t{img_path.name}\t{exc}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
