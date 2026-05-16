import os
import numpy as np
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# Risk Prediction with Isolation Forest (Anomaly Detection)
# Features: temperature, humidity, feed_intake, water_intake, activity_level, mortality_rate, bird_age


def generate_baseline_data(num_samples=1000):
    """Generate normal farm data for unsupervised anomaly training"""
    rng = np.random.default_rng(42)

    temperature = rng.normal(30, 2, num_samples)
    humidity = rng.normal(60, 8, num_samples)
    feed_intake = rng.normal(120, 20, num_samples)
    water_intake = rng.normal(180, 25, num_samples)
    activity_level = rng.normal(75, 10, num_samples)
    mortality_rate = rng.normal(1.0, 0.6, num_samples)
    bird_age = rng.normal(28, 10, num_samples)

    data = np.column_stack(
        [
            temperature,
            humidity,
            feed_intake,
            water_intake,
            activity_level,
            mortality_rate,
            bird_age,
        ]
    )

    return data


def train():
    print("🐔 PoultryGuard AI - Risk Model Training")
    print("=" * 50)

    print("\n📊 Generating baseline farm data...")
    baseline_data = generate_baseline_data(num_samples=1500)
    print(f"Baseline samples: {baseline_data.shape[0]}")
    print(f"Features: {baseline_data.shape[1]}")

    print("\n🔧 Normalizing features...")
    scaler = StandardScaler()
    normalized_data = scaler.fit_transform(baseline_data)

    print("\n🏗️  Training Isolation Forest...")
    model = IsolationForest(
        contamination=0.12,
        random_state=42,
        n_estimators=100,
        max_samples="auto",
    )
    model.fit(normalized_data)

    print("\n💾 Saving model and scaler...")
    os.makedirs("../models", exist_ok=True)
    joblib.dump(model, "../models/isolation_forest.pkl")
    joblib.dump(scaler, "../models/risk_scaler.pkl")

    print("✅ Model saved to: ../models/isolation_forest.pkl")
    print("✅ Scaler saved to: ../models/risk_scaler.pkl")

    print("\n🧪 Testing with sample data...")
    test_normal = np.array([[30, 60, 120, 180, 75, 1.0, 28]])
    test_anomaly = np.array([[45, 90, 50, 80, 30, 8.0, 28]])

    test_normal_scaled = scaler.transform(test_normal)
    test_anomaly_scaled = scaler.transform(test_anomaly)

    score_normal = model.decision_function(test_normal_scaled)[0]
    score_anomaly = model.decision_function(test_anomaly_scaled)[0]

    print(f"Normal score: {score_normal:.4f} (higher is more normal)")
    print(f"Anomaly score: {score_anomaly:.4f} (lower means anomaly)")

    print("\n✨ Training complete!")


if __name__ == "__main__":
    train()
