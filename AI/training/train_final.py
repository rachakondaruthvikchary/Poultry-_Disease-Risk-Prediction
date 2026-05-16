#!/usr/bin/env python3
"""
Memory-efficient trainer using generators
Trains on real Newcastle + Salmonellosis data only
Supports all 12 disease classes in model output
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from pathlib import Path
import json
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, preprocessing
from datetime import datetime

print(f"⏱️  Starting memory-efficient training at {datetime.now().strftime('%H:%M:%S')}")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "AI" / "sample_data"
MODEL_PATH = PROJECT_ROOT / "AI" / "models" / "poultry_cnn.keras"

ALL_DISEASES = [
    "Avian Influenza",
    "Coccidiosis",
    "Fowl Cholera",
    "Fowl Pox",
    "Healthy",
    "Infectious Bronchitis",
    "Infectious Bursal Disease",
    "Infectious Coryza",
    "Marek's Disease",
    "Mycoplasmosis-CRD",
    "Newcastle disease",
    "Salmonellosis-Pullorum",
]

print(f"\n📊 Real data available:")
print(f"   ✓ Newcastle disease")
print(f"   ✓ Salmonellosis-Pullorum")
print(f"   ⚠️  Other 10: will use reference matcher + heuristics in inference")

# Use ImageDataGenerator for memory-efficient training
print("\n🔄 Building data generators (memory-efficient)...")

train_datagen = preprocessing.image_dataset_from_directory(
    DATA_DIR,
    labels="inferred",
    label_mode="int",
    class_names=["Newcastle disease", "Salmonellosis-Pullorum"],  # Only real data classes
    image_size=(224, 224),
    batch_size=16,
    shuffle=True,
    seed=42,
    validation_split=0.15,
    subset="training",
    interpolation="bilinear",
)

val_datagen = preprocessing.image_dataset_from_directory(
    DATA_DIR,
    labels="inferred",
    label_mode="int",
    class_names=["Newcastle disease", "Salmonellosis-Pullorum"],
    image_size=(224, 224),
    batch_size=16,
    shuffle=False,
    seed=42,
    validation_split=0.15,
    subset="validation",
    interpolation="bilinear",
)

# Apply augmentation
def augment(image, label):
    image = tf.image.random_flip_left_right(image)
    image = tf.image.random_brightness(image, 0.2)
    image = tf.image.random_contrast(image, 0.8, 1.2)
    image = tf.image.random_hue(image, 0.1)
    return image, label

train_datagen = train_datagen.map(augment).prefetch(tf.data.AUTOTUNE)
val_datagen = val_datagen.prefetch(tf.data.AUTOTUNE)

# Build model for 12 classes (even though training on 2)
print("\n🏗️  Building CNN model...")
inputs = keras.Input(shape=(224, 224, 3))

base_model = keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights="imagenet",
)
base_model.trainable = False

x = base_model(inputs, training=False)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.40)(x)
x = layers.Dense(512, activation="relu")(x)
x = layers.Dropout(0.30)(x)
x = layers.Dense(256, activation="relu")(x)
x = layers.Dropout(0.20)(x)
outputs = layers.Dense(len(ALL_DISEASES), activation="softmax")(x)

model = keras.Model(inputs, outputs)

# Compile
model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"],
)

# Phase 1: Train classifier head
print("\n🎯 Phase 1: Training classifier head (10 epochs)...")
h1 = model.fit(
    train_datagen,
    validation_data=val_datagen,
    epochs=10,
    verbose=1,
    callbacks=[
        keras.callbacks.EarlyStopping(monitor="val_loss", patience=3, restore_best_weights=True)
    ]
)

# Phase 2: Fine-tune
print("\n🔧 Phase 2: Fine-tuning...")
base_model.trainable = True
for layer in base_model.layers[:-50]:
    layer.trainable = False
for layer in base_model.layers:
    if isinstance(layer, layers.BatchNormalization):
        layer.trainable = False

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.00005),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"],
)

print("🎯 Fine-tuning (8 epochs)...")
h2 = model.fit(
    train_datagen,
    validation_data=val_datagen,
    epochs=8,
    verbose=1,
    callbacks=[
        keras.callbacks.EarlyStopping(monitor="val_loss", patience=4, restore_best_weights=True)
    ]
)

# Save
print("\n💾 Saving model...")
MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
model.save(MODEL_PATH)

labels_path = MODEL_PATH.with_name(f"{MODEL_PATH.stem}_labels.json")
labels_data = {
    "class_names": ALL_DISEASES,
    "training_date": datetime.now().isoformat(),
    "trained_on": ["Newcastle disease", "Salmonellosis-Pullorum"],
    "note": "Trained on 2 real classes; inference uses multi-tier approach for all 12 diseases"
}
labels_path.write_text(json.dumps(labels_data, indent=2))

print(f"✅ Model saved to: {MODEL_PATH}")
print(f"✅ Labels saved to: {labels_path}")

print(f"\n📈 Training complete!")
print(f"⏱️  Finished at {datetime.now().strftime('%H:%M:%S')}")
print("\n🚀 Model ready for inference with all 12 disease names!")
