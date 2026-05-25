from pathlib import Path
import numpy as np

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    import joblib
    sklearn_available = True
except ImportError:
    sklearn_available = False
    joblib = None


class StructuredRiskPredictor:
    def __init__(self, model_path: str = "../AI/models/isolation_forest.pkl", scaler_path: str = "../AI/models/risk_scaler.pkl"):
        self.model_path = Path(model_path)
        self.scaler_path = Path(scaler_path)
        self.model = None
        self.scaler = None

        # Check for Netlify/Lambda environment and override paths
        import os
        if os.environ.get("NETLIFY") == "true" or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
            func_dir = Path(__file__).resolve().parent.parent
            self.model_path = func_dir / "models" / "isolation_forest.pkl"
            self.scaler_path = func_dir / "models" / "risk_scaler.pkl"

        if sklearn_available and self.model_path.exists() and self.scaler_path.exists():
            try:
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
            except Exception:
                self.model = None
                self.scaler = None

        if self.model is None or self.scaler is None:
            if sklearn_available:
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
        if self.model is not None and self.scaler is not None:
            row = np.array(features, dtype=np.float32).reshape(1, -1)
            transformed = self.scaler.transform(row)
            raw = float(self.model.decision_function(transformed)[0])
            risk_score = max(0.0, min(1.0, (0.18 - raw) * 3.0))
        else:
            # Fallback heuristic calculation when scikit-learn is not available
            # Features: [temperature, humidity, feed_intake, water_intake, activity_level, mortality_rate, bird_age]
            # Normal baseline from _bootstrap_default_model:
            # temperature: ~30 (normal range 26-34)
            # humidity: ~60 (normal range 44-76)
            # feed_intake: ~120 (normal range 80-160)
            # water_intake: ~180 (normal range 130-230)
            # activity_level: ~75 (normal range 55-95)
            # mortality_rate: ~1.0 (normal range 0.0-2.2)
            # bird_age: ~28 (normal range 8-48)
            
            temp, hum, feed, water, activity, mortality, age = features
            
            # Simple heuristic calculations for anomalies
            anomalies = 0.0
            
            # Mortality is the strongest indicator of risk
            if mortality > 2.0:
                anomalies += min(1.0, (mortality - 2.0) * 0.25) # high mortality
            elif mortality > 5.0:
                anomalies += 1.0 # critical mortality
                
            # Feed and water intake drop indicates illness
            if feed < 80:
                anomalies += 0.25
            if water < 130:
                anomalies += 0.25
                
            # Activity level drop
            if activity < 50:
                anomalies += 0.2
                
            # Extreme temp/humidity
            if temp < 20 or temp > 40:
                anomalies += 0.15
            if hum < 30 or hum > 85:
                anomalies += 0.1
                
            risk_score = min(1.0, anomalies)

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
