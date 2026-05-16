from pathlib import Path

import numpy as np
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


class StructuredRiskPredictor:
    def __init__(self, model_path: str = "../AI/models/isolation_forest.pkl", scaler_path: str = "../AI/models/risk_scaler.pkl"):
        self.model_path = Path(model_path)
        self.scaler_path = Path(scaler_path)
        self.model = None
        self.scaler = None

        if self.model_path.exists() and self.scaler_path.exists():
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
        else:
            self._bootstrap_default_model()

    def _bootstrap_default_model(self):
        rng = np.random.default_rng(42)
        baseline = np.column_stack(
            [
                rng.normal(30, 2, 1000),
                rng.normal(60, 8, 1000),
                rng.normal(120, 20, 1000),
                rng.normal(180, 25, 1000),
                rng.normal(75, 10, 1000),
                rng.normal(1.0, 0.6, 1000),
                rng.normal(28, 10, 1000),
            ]
        )
        self.scaler = StandardScaler()
        normalized = self.scaler.fit_transform(baseline)
        self.model = IsolationForest(contamination=0.12, random_state=42)
        self.model.fit(normalized)

    def predict(self, features: list[float]) -> dict:
        row = np.array(features, dtype=np.float32).reshape(1, -1)
        transformed = self.scaler.transform(row)
        raw = float(self.model.decision_function(transformed)[0])
        risk_score = max(0.0, min(1.0, (0.18 - raw) * 3.0))

        if risk_score < 0.25:
            category = "Low"
        elif risk_score < 0.5:
            category = "Medium"
        elif risk_score < 0.75:
            category = "High"
        else:
            category = "Critical"

        return {"risk_score": round(risk_score, 4), "risk_category": category}


risk_predictor = StructuredRiskPredictor()
