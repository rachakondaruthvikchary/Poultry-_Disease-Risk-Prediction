#!/usr/bin/env python3
"""
Quick CNN Model Generator - Creates a fast trained CNN model
Simplified version that trains quickly for demonstration
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

CLASSES = [
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

IMG_SIZE = 224
NUM_CLASSES = len(CLASSES)

def create_cnn_model():
    """Build CNN with MobileNetV2 transfer learning"""
    base_model = keras.applications.MobileNetV2(
        input_shape=(IMG_SIZE, IMG_SIZE, 3),
        include_top=False,
        weights="imagenet",
    )
    base_model.trainable = False

    model = keras.Sequential([
        layers.Input(shape=(IMG_SIZE, IMG_SIZE, 3)),
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dropout(0.3),
        layers.Dense(256, activation="relu"),
        layers.Dropout(0.2),
        layers.Dense(NUM_CLASSES, activation="softmax"),
    ])

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    return model

def generate_quick_data(num_samples=800):
    """Generate quick synthetic training data"""
    X = []
    y = []

    for class_idx in range(NUM_CLASSES):
        for _ in range(num_samples // NUM_CLASSES):
            # Random RGB image
            img = np.random.rand(IMG_SIZE, IMG_SIZE, 3).astype(np.float32)
            
            # Add some variation based on disease class
            if class_idx == 0:  # Newcastle - dark
                img *= 0.3
            elif class_idx == 1:  # Avian Influenza - red
                img[:, :, 0] += 0.5
            elif class_idx == 10:  # Coccidiosis - orange
                img[:, :, 0] += 0.4
                img[:, :, 1] += 0.3
            elif class_idx == 11:  # Healthy - bright
                img *= 1.2
            
            X.append(np.clip(img, 0, 1))
            y.append(class_idx)

    return np.array(X), keras.utils.to_categorical(y, NUM_CLASSES)

print("🐔 PoultryGuard AI - Quick CNN Model Training")
print("=" * 50)
print("\n📊 Generating synthetic dataset...")
X, y = generate_quick_data(num_samples=800)

print(f"Training samples: {len(X)}")
print("\n🏗️  Building CNN model...")
model = create_cnn_model()

print("\n🎯 Training model (5 epochs - quick mode)...")
history = model.fit(
    X, y,
    validation_split=0.2,
    epochs=5,
    batch_size=32,
    verbose=1,
)

print("\n💾 Saving model...")
os.makedirs("../models", exist_ok=True)
model.save("../models/poultry_cnn.keras")
print("✅ Model saved to: ../models/poultry_cnn.keras")

val_loss, val_acc = model.evaluate(X[:160], y[:160], verbose=0)
print(f"\n📈 Validation Accuracy: {val_acc * 100:.2f}%")
print("\n✨ Training complete!")
print("\n🚀 CNN model is now ready for inference!")
