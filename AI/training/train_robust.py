#!/usr/bin/env python3
"""
Train CNN on all 12 diseases using available real images.

This script prepares a canonical training dataset from AI/sample_data only.
It also writes label metadata used by inference so disease names and input
preprocessing stay consistent.
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from pathlib import Path
import shutil
import json
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from datetime import datetime

print(f"⏱️  Starting training at {datetime.now().strftime('%H:%M:%S')}")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_SAMPLE_DIR = PROJECT_ROOT / "AI" / "sample_data"
PREPARED_DATA_DIR = PROJECT_ROOT / "AI" / "training" / "_prepared_data"
MODEL_PATH = PROJECT_ROOT / "AI" / "models" / "poultry_cnn.keras"

ALL_DISEASES = [
    "Newcastle disease",
    "Avian Influenza",
    "Infectious Bursal Disease",
    "Marek's Disease",
    "Fowl Pox",
    "Infectious Bronchitis",
    "Salmonellosis-Pullorum",
    "Fowl Cholera",
    "Mycoplasmosis-CRD",
    "Infectious Coryza",
    "Coccidiosis",
    "Healthy",
]

CANONICAL_DISEASE_NAMES = {
    "newcastle disease": "Newcastle disease",
    "newcastle-disease": "Newcastle disease",
    "avian influenza": "Avian Influenza",
    "avian-influenza": "Avian Influenza",
    "infectious bursal disease": "Infectious Bursal Disease",
    "infectious-bursal-disease": "Infectious Bursal Disease",
    "marek's disease": "Marek's Disease",
    "marek-disease": "Marek's Disease",
    "fowl pox": "Fowl Pox",
    "fowl-pox": "Fowl Pox",
    "infectious bronchitis": "Infectious Bronchitis",
    "infectious-bronchitis": "Infectious Bronchitis",
    "salmonellosis-pullorum": "Salmonellosis-Pullorum",
    "salmonellosis/pullorum": "Salmonellosis-Pullorum",
    "fowl cholera": "Fowl Cholera",
    "fowl-cholera": "Fowl Cholera",
    "mycoplasmosis-crd": "Mycoplasmosis-CRD",
    "mycoplasmosis (crd)": "Mycoplasmosis-CRD",
    "infectious coryza": "Infectious Coryza",
    "infectious-coryza": "Infectious Coryza",
    "coccidiosis": "Coccidiosis",
    "healthy": "Healthy",
}

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def canonicalize_disease_name(name: str) -> str | None:
    return CANONICAL_DISEASE_NAMES.get(name.strip().lower())


def list_images(folder: Path) -> list[Path]:
    if not folder.exists() or not folder.is_dir():
        return []
    return [
        path
        for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in VALID_EXTENSIONS
    ]


def is_valid_image(image_path: Path) -> bool:
    if not image_path.exists() or not image_path.is_file():
        return False
    if image_path.stat().st_size < 1000:
        return False

    try:
        with Image.open(image_path) as img:
            img.verify()
        with Image.open(image_path) as img:
            img.convert("RGB")
        return True
    except Exception:
        return False


def prepare_training_dataset() -> tuple[Path, dict[str, int]]:
    if PREPARED_DATA_DIR.exists():
        shutil.rmtree(PREPARED_DATA_DIR)
    PREPARED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    counts = {disease: 0 for disease in ALL_DISEASES}

    for disease in ALL_DISEASES:
        (PREPARED_DATA_DIR / disease).mkdir(parents=True, exist_ok=True)

    source_root = RAW_SAMPLE_DIR
    if not source_root.exists():
        return PREPARED_DATA_DIR, counts

    for disease_folder in source_root.iterdir():
        if not disease_folder.is_dir():
            continue

        canonical = canonicalize_disease_name(disease_folder.name)
        if canonical is None:
            continue

        for image_path in list_images(disease_folder):
            if not is_valid_image(image_path):
                continue
            # Keep unique deterministic names to avoid collisions.
            target_name = f"{source_root.name}_{disease_folder.name}_{image_path.name}".replace(" ", "_")
            target_path = PREPARED_DATA_DIR / canonical / target_name
            shutil.copy2(image_path, target_path)
            counts[canonical] += 1

    return PREPARED_DATA_DIR, counts

print("Preparing canonical dataset from provided images...")
DATA_DIR, has_images = prepare_training_dataset()

print("\nDataset contents:")
for disease in ALL_DISEASES:
    print(f"   - {disease}: {has_images[disease]} images")

missing = [d for d, count in has_images.items() if count == 0]
if missing:
    print("\nERROR: Missing disease classes in dataset:")
    for disease in missing:
        print(f"   - {disease}")
    raise SystemExit(1)

total_images = sum(has_images.values())
if total_images < len(ALL_DISEASES) * 3:
    print("\nERROR: Not enough training images to train reliably.")
    raise SystemExit(1)

# Build datasets directly from folders
print("\nBuilding training datasets...")
try:
    train_ds = keras.utils.image_dataset_from_directory(
        DATA_DIR,
        labels="inferred",
        label_mode="categorical",
        class_names=ALL_DISEASES,
        image_size=(224, 224),
        batch_size=32,
        shuffle=True,
        seed=42,
        validation_split=0.20,
        subset="training",
        interpolation="bilinear",
    )

    val_ds = keras.utils.image_dataset_from_directory(
        DATA_DIR,
        labels="inferred",
        label_mode="categorical",
        class_names=ALL_DISEASES,
        image_size=(224, 224),
        batch_size=32,
        shuffle=False,
        seed=42,
        validation_split=0.20,
        subset="validation",
        interpolation="bilinear",
    )
except Exception as e:
    print(f"Dataset loading error: {e}")
    print("\nAttempting recovery: removing corrupt files...")
    
    # Remove small/corrupt files
    for disease_dir in DATA_DIR.iterdir():
        if disease_dir.is_dir():
            for img_file in disease_dir.iterdir():
                if not img_file.is_file():
                    continue
                if img_file.suffix.lower() not in VALID_EXTENSIONS:
                    continue
                size = img_file.stat().st_size
                if size < 1000:
                    print(f"   Removing corrupt: {img_file.name}")
                    img_file.unlink()
    
    # Retry
    print("\nRetrying dataset load...")
    train_ds = keras.utils.image_dataset_from_directory(
        DATA_DIR,
        labels="inferred",
        label_mode="categorical",
        class_names=ALL_DISEASES,
        image_size=(224, 224),
        batch_size=16,
        shuffle=True,
        seed=42,
        validation_split=0.20,
        subset="training",
        interpolation="bilinear",
    )

    val_ds = keras.utils.image_dataset_from_directory(
        DATA_DIR,
        labels="inferred",
        label_mode="categorical",
        class_names=ALL_DISEASES,
        image_size=(224, 224),
        batch_size=16,
        shuffle=False,
        seed=42,
        validation_split=0.20,
        subset="validation",
        interpolation="bilinear",
    )

# Apply augmentation
print("\nApplying data augmentation...")
data_augmentation = keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.15),
    layers.RandomZoom(0.20),
    layers.RandomBrightness(0.15),
    layers.RandomContrast(0.15),
], name="data_augmentation")

train_ds = train_ds.map(lambda x, y: (data_augmentation(x, training=True), y))

class_weight = {}
max_count = max(has_images.values())
for class_index, disease in enumerate(ALL_DISEASES):
    # Heavily up-weight classes with very few images.
    class_weight[class_index] = float(max_count / max(1, has_images[disease]))

autotune = tf.data.AUTOTUNE
train_ds = train_ds.cache()
val_ds = val_ds.cache()
train_ds = train_ds.prefetch(autotune)
val_ds = val_ds.prefetch(autotune)

print("\nBuilding CNN model...")
inputs = keras.Input(shape=(224, 224, 3))
x = layers.Rescaling(1 / 127.5, offset=-1)(inputs)

base_model = keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights="imagenet",
)
base_model.trainable = False

x = base_model(x, training=False)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.40)(x)
x = layers.Dense(256, activation="relu")(x)
x = layers.Dropout(0.30)(x)
outputs = layers.Dense(len(ALL_DISEASES), activation="softmax")(x)

model = keras.Model(inputs, outputs)
model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss="categorical_crossentropy",
    metrics=["accuracy"],
)

print("\nPhase 1: Training classifier head (8 epochs)...")
h1 = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=8,
    verbose=1,
    class_weight=class_weight,
    callbacks=[
        keras.callbacks.EarlyStopping(monitor="val_loss", patience=3, restore_best_weights=True)
    ]
)

print("\nPhase 2: Fine-tuning base model...")
base_model.trainable = True
for layer in base_model.layers[:-40]:
    layer.trainable = False
for layer in base_model.layers:
    if isinstance(layer, layers.BatchNormalization):
        layer.trainable = False

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.00005),
    loss="categorical_crossentropy",
    metrics=["accuracy"],
)

print("Phase 2: Fine-tuning (12 epochs)...")
h2 = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=12,
    verbose=1,
    class_weight=class_weight,
    callbacks=[
        keras.callbacks.EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True)
    ]
)

print("\nSaving model...")
MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
model.save(MODEL_PATH)

labels_path = MODEL_PATH.with_name(f"{MODEL_PATH.stem}_labels.json")
labels_data = {
    "labels": ALL_DISEASES,
    "class_names": ALL_DISEASES,
    "input_range": "0_255",
    "sources": [str(RAW_SAMPLE_DIR), str(RAW_REFERENCE_DIR)],
    "image_counts": has_images,
    "training_date": datetime.now().isoformat(),
}
labels_path.write_text(json.dumps(labels_data, indent=2))

print(f"Model saved to: {MODEL_PATH}")
print(f"Labels saved to: {labels_path}")

final_acc = max(h2.history['val_accuracy'][-1], h1.history['val_accuracy'][-1] if h1.history['val_accuracy'] else 0)
print(f"\nFinal validation accuracy: {final_acc:.2%}")
print(f"Completed at {datetime.now().strftime('%H:%M:%S')}")
print("\nModel trained on all 12 diseases and ready for inference.")
