"""
PoultryGuard AI - Inference Module
Demonstrates how to use the trained models for predictions.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from Backend.app.services.image_model_service import predictor
from Backend.app.services.risk_model_service import risk_predictor


def test_image_prediction():
    """Test image disease prediction with a sample"""
    print("🖼️  Testing Image Disease Prediction")
    print("=" * 50)
    
    # Create a dummy image (in production, load actual image)
    import numpy as np
    from PIL import Image
    from io import BytesIO
    
    dummy_img = Image.fromarray(
        (np.random.rand(224, 224, 3) * 255).astype(np.uint8)
    )
    buffer = BytesIO()
    dummy_img.save(buffer, format="JPEG")
    image_bytes = buffer.getvalue()
    
    result = predictor.predict(image_bytes)
    
    print(f"\n✅ Disease: {result['disease_name']}")
    print(f"📊 Confidence: {result['confidence'] * 100:.2f}%")
    print(f"⚠️  Risk Level: {result['risk_level']}")
    print(f"💡 Action: {result['suggested_action']}")


def test_risk_prediction():
    """Test structured risk prediction"""
    print("\n\n📊 Testing Structured Risk Prediction")
    print("=" * 50)
    
    # Normal farm conditions
    normal_features = [30, 60, 120, 180, 75, 1.0, 28]
    result_normal = risk_predictor.predict(normal_features)
    
    print(f"\n🟢 Normal Conditions:")
    print(f"   Risk Score: {result_normal['risk_score']:.4f}")
    print(f"   Category: {result_normal['risk_category']}")
    
    # Anomalous farm conditions
    anomaly_features = [45, 90, 50, 80, 30, 8.0, 28]
    result_anomaly = risk_predictor.predict(anomaly_features)
    
    print(f"\n🔴 Anomalous Conditions:")
    print(f"   Risk Score: {result_anomaly['risk_score']:.4f}")
    print(f"   Category: {result_anomaly['risk_category']}")


if __name__ == "__main__":
    print("🐔 PoultryGuard AI - Inference Test")
    print("=" * 50)
    print()
    
    test_image_prediction()
    test_risk_prediction()
    
    print("\n\n✨ All inference tests complete!")
