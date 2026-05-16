#!/usr/bin/env python3
"""
Fast CNN trainer for all 12 diseases - streamlined for speed
Trains MobileNetV2 on balanced dataset with all disease classes
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from pathlib import Path
import json
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from datetime import datetime

print(f"⏱️  Starting training at {datetime.now().strftime('%H:%M:%S')}")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "AI" / "sample_data"
MODEL_PATH = PROJECT_ROOT / "AI" / "models" / "poultry_cnn.keras"

# Get all disease folders
disease_folders = sorted([d for d in DATA_DIR.iterdir() if d.is_dir()])
class_names = [d.name for d in disease_folders]

IMAGE_EXTENSIONS = ("*.jpg", "*.jpeg", "*.png", "*.webp")


def count_images(folder: Path) -> int:
    return sum(len(list(folder.glob(pattern))) for pattern in IMAGE_EXTENSIONS)


print(f"📊 Training classes: {len(class_names)}")
for disease in class_names:
    image_count = count_images(DATA_DIR / disease)
    print(f"   - {disease}: {image_count} images")

# Build dataset
print("\n🔄 Building training datasets...")
train_ds = keras.utils.image_dataset_from_directory(
    DATA_DIR,
    labels="inferred",
    label_mode="categorical",
    class_names=class_names,
    image_size=(224, 224),
    batch_size=32,
    shuffle=True,
    seed=42,
    validation_split=0.2,
    subset="training",
)

val_ds = keras.utils.image_dataset_from_directory(
    DATA_DIR,
    labels="inferred",
    label_mode="categorical",
    class_names=class_names,
    image_size=(224, 224),
    batch_size=32,
    shuffle=False,
    seed=42,
    validation_split=0.2,
    subset="validation",
)

# Prefetch for speed
autotune = tf.data.AUTOTUNE
train_ds = train_ds.prefetch(autotune)
val_ds = val_ds.prefetch(autotune)

# Build model
print("\n🏗️  Building CNN model...")
inputs = keras.Input(shape=(224, 224, 3))
x = layers.RandomFlip("horizontal")(inputs)
x = layers.RandomRotation(0.08)(x)
x = layers.RandomZoom(0.10)(x)
x = layers.Rescaling(1 / 127.5, offset=-1)(x)

base_model = keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights="imagenet",
)
base_model.trainable = False

x = base_model(x, training=False)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.30)(x)
x = layers.Dense(256, activation="relu")(x)
x = layers.Dropout(0.20)(x)
outputs = layers.Dense(len(class_names), activation="softmax")(x)

model = keras.Model(inputs, outputs)
model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss="categorical_crossentropy",
    metrics=["accuracy"],
)

# Initial training (frozen base)
print("\n🎯 Training classifier head (5 epochs)...")
model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=5,
    verbose=1,
    callbacks=[
        keras.callbacks.EarlyStopping(monitor="val_loss", patience=3, restore_best_weights=True)
    ]
)

# Fine-tune
print("\n🔧 Fine-tuning base model...")
base_model.trainable = True
for layer in base_model.layers[:-30]:
    layer.trainable = False
for layer in base_model.layers:
    if isinstance(layer, layers.BatchNormalization):
        layer.trainable = False

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.0001),
    loss="categorical_crossentropy",
    metrics=["accuracy"],
)

print("🎯 Fine-tuning (10 epochs)...")
history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=10,
    verbose=1,
    callbacks=[
        keras.callbacks.EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True)
    ]
)

# Save model
print("\n💾 Saving model...")
MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
model.save(MODEL_PATH)

# Save labels
labels_path = MODEL_PATH.with_name(f"{MODEL_PATH.stem}_labels.json")
labels_data = {
    "class_names": class_names,
    "labels": class_names,
    "input_range": "0_255",
    "training_date": datetime.now().isoformat(),
}
labels_path.write_text(json.dumps(labels_data, indent=2))

print(f"✅ Model saved to: {MODEL_PATH}")
print(f"✅ Labels saved to: {labels_path}")
print(f"\n📈 Final validation accuracy: {history.history['val_accuracy'][-1]:.2%}")
print(f"⏱️  Completed at {datetime.now().strftime('%H:%M:%S')}")
print("\n🚀 Model is ready for inference!")
