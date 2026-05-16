#!/usr/bin/env python3
"""
Train the image disease model from real folders in AI/sample_data.

Expected structure:
AI/sample_data/
  Coccidiosis/
  Healthy/
  Newcastle disease/
  Salmonellosis-Pullorum/

The script trains only folders that actually contain enough images and writes:
  AI/models/poultry_cnn.keras
  AI/models/poultry_cnn_labels.json
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime
import shutil
import tempfile
import sys
from pathlib import Path

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from PIL import Image, ImageFile

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from AI.disease_names import display_label as canonical_display_label


ImageFile.LOAD_TRUNCATED_IMAGES = True


DEFAULT_DATA_DIR = PROJECT_ROOT / "AI" / "sample_data"
DEFAULT_MODEL_PATH = PROJECT_ROOT / "AI" / "models" / "poultry_cnn.keras"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif"}

def display_label(folder_name: str) -> str:
    return canonical_display_label(folder_name)


def count_images(folder: Path) -> int:
    return sum(
        1
        for item in folder.rglob("*")
        if item.is_file() and item.suffix.lower() in IMAGE_EXTENSIONS
    )


def _is_valid_image(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size == 0:
        return False

    try:
        with Image.open(path) as image:
            image.load()
        return True
    except Exception:
        return False


def sanitize_dataset(data_dir: Path, class_names: list[str]) -> Path:
    temp_dir = Path(tempfile.mkdtemp(prefix="poultryguard_clean_"))
    total_classes = len(class_names)
    for class_idx, class_name in enumerate(class_names, 1):
        source_folder = data_dir / class_name
        target_folder = temp_dir / class_name
        target_folder.mkdir(parents=True, exist_ok=True)
        
        images = [p for p in source_folder.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS]
        total_images = len(images)
        
        print(f"Sanitizing {class_name} [{class_idx}/{total_classes}] ({total_images} images)...", end="", flush=True)
        
        count = 0
        for image_path in images:
            if _is_valid_image(image_path):
                try:
                    with Image.open(image_path) as image:
                        image = image.convert("RGB")
                        output_path = target_folder / f"{image_path.stem}.jpg"
                        image.save(output_path, format="JPEG", quality=85, optimize=False)
                    count += 1
                except Exception:
                    continue
        print(f" OK ({count} saved)")

    return temp_dir


def discover_classes(data_dir: Path, min_images: int) -> tuple[list[str], dict[str, int]]:
    counts = {
        folder.name: count_images(folder)
        for folder in data_dir.iterdir()
        if folder.is_dir()
    }
    class_names = sorted(name for name, count in counts.items() if count >= min_images)
    return class_names, counts


def build_datasets(
    data_dir: Path,
    class_names: list[str],
    image_size: int,
    batch_size: int,
    validation_split: float,
    seed: int,
) -> tuple[tf.data.Dataset, tf.data.Dataset]:
    train_ds = keras.utils.image_dataset_from_directory(
        data_dir,
        labels="inferred",
        label_mode="categorical",
        class_names=class_names,
        image_size=(image_size, image_size),
        batch_size=batch_size,
        shuffle=True,
        seed=seed,
        validation_split=validation_split,
        subset="training",
    )
    val_ds = keras.utils.image_dataset_from_directory(
        data_dir,
        labels="inferred",
        label_mode="categorical",
        class_names=class_names,
        image_size=(image_size, image_size),
        batch_size=batch_size,
        shuffle=True,
        seed=seed,
        validation_split=validation_split,
        subset="validation",
    )

    autotune = tf.data.AUTOTUNE
    return train_ds.prefetch(autotune), val_ds.prefetch(autotune)


def build_model(num_classes: int, image_size: int, weights: str | None) -> keras.Model:
    inputs = keras.Input(shape=(image_size, image_size, 3))
    x = layers.RandomFlip("horizontal")(inputs)
    x = layers.RandomRotation(0.08)(x)
    x = layers.RandomZoom(0.10)(x)
    x = layers.RandomContrast(0.10)(x)
    x = layers.Rescaling(1 / 127.5, offset=-1)(x)

    try:
        base_model = keras.applications.MobileNetV2(
            input_shape=(image_size, image_size, 3),
            include_top=False,
            weights=weights,
        )
    except Exception:
        print("Warning: could not load pretrained weights; falling back to random initialization.")
        base_model = keras.applications.MobileNetV2(
            input_shape=(image_size, image_size, 3),
            include_top=False,
            weights=None,
        )
    base_model.trainable = False

    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.30)(x)
    x = layers.Dense(256, activation="relu")(x)
    x = layers.Dropout(0.20)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)

    model = keras.Model(inputs, outputs)
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def class_weights(class_names: list[str], counts: dict[str, int]) -> dict[int, float]:
    selected_counts = Counter({name: counts[name] for name in class_names})
    total = sum(selected_counts.values())
    return {
        idx: total / (len(class_names) * selected_counts[name])
        for idx, name in enumerate(class_names)
    }


def fine_tune_model(model: keras.Model, unfreeze_last: int, learning_rate: float) -> None:
    base_model = next(
        layer for layer in model.layers if isinstance(layer, keras.Model) and layer.name.startswith("mobilenetv2")
    )
    base_model.trainable = True

    for layer in base_model.layers[:-unfreeze_last]:
        layer.trainable = False
    for layer in base_model.layers:
        if isinstance(layer, layers.BatchNormalization):
            layer.trainable = False

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )


def save_metadata(model_path: Path, class_names: list[str], counts: dict[str, int], args: argparse.Namespace) -> None:
    labels_path = model_path.with_name(f"{model_path.stem}_labels.json")
    metadata = {
        "labels": [display_label(name) for name in class_names],
        "folder_class_names": class_names,
        "class_counts": {name: counts[name] for name in class_names},
        "image_size": args.image_size,
        "input_range": "0_255",
        "architecture": "MobileNetV2",
        "trained_at": datetime.now().isoformat(timespec="seconds"),
    }
    labels_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Saved labels metadata: {labels_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train PoultryGuardAI CNN from real images.")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--model-path", type=Path, default=DEFAULT_MODEL_PATH)
    parser.add_argument("--min-images", type=int, default=3)
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--fine-tune-epochs", type=int, default=8)
    parser.add_argument("--unfreeze-last", type=int, default=30)
    parser.add_argument("--validation-split", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--weights",
        choices=["imagenet", "none"],
        default="imagenet",
        help="Use 'none' only when ImageNet weights cannot be downloaded.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data_dir = args.data_dir.resolve()
    model_path = args.model_path.resolve()
    model_path.parent.mkdir(parents=True, exist_ok=True)

    class_names, counts = discover_classes(data_dir, args.min_images)
    if len(class_names) < 2:
        raise SystemExit(
            f"Need at least 2 classes with {args.min_images}+ images in {data_dir}. "
            "Add more labeled folders before training."
        )

    print("Training classes:")
    for name in class_names:
        print(f"  - {display_label(name)} ({counts[name]} images)")

    clean_data_dir = sanitize_dataset(data_dir, class_names)
    print(f"\nSanitized dataset copied to: {clean_data_dir}")

    train_ds, val_ds = build_datasets(
        data_dir=clean_data_dir,
        class_names=class_names,
        image_size=args.image_size,
        batch_size=args.batch_size,
        validation_split=args.validation_split,
        seed=args.seed,
    )

    weights = None if args.weights == "none" else args.weights
    model = build_model(len(class_names), args.image_size, weights)

    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor="val_accuracy",
            patience=5,
            restore_best_weights=True,
        ),
        keras.callbacks.ModelCheckpoint(
            filepath=model_path,
            monitor="val_accuracy",
            save_best_only=True,
        ),
    ]

    print("\nTraining classifier head...")
    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=args.epochs,
        class_weight=class_weights(class_names, counts),
        callbacks=callbacks,
    )

    if args.fine_tune_epochs > 0:
        print("\nFine-tuning last MobileNetV2 layers...")
        fine_tune_model(model, args.unfreeze_last, learning_rate=1e-5)
        model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=args.fine_tune_epochs,
            class_weight=class_weights(class_names, counts),
            callbacks=callbacks,
        )

    loss, accuracy = model.evaluate(val_ds, verbose=0)
    model.save(model_path)
    save_metadata(model_path, class_names, counts, args)

    print(f"\nValidation accuracy: {accuracy * 100:.2f}%")
    print(f"Validation loss: {loss:.4f}")
    print(f"Saved model: {model_path}")


if __name__ == "__main__":
    main()
