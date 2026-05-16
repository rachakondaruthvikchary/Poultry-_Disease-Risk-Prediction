#!/usr/bin/env python3
"""
Prepare a storage-light chicken face/head image dataset.

Examples:
  python AI/prepare_face_dataset.py --create-folders
  python AI/prepare_face_dataset.py --status
  python AI/prepare_face_dataset.py --disease "Fowl Pox" --source "D:\\datasets\\fowl_pox"
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from PIL import Image, ImageOps


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = PROJECT_ROOT / "AI" / "sample_data_face"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

FACE_DISEASES = [
    "Healthy",
    "Fowl Pox",
    "Infectious Coryza",
    "Mycoplasmosis-CRD",
    "Avian Influenza",
    "Fowl Cholera",
    "Infectious Bronchitis",
    "Marek's Disease",
    "Newcastle disease",
    "Infectious Bursal Disease",
    "Coccidiosis",
    "Salmonellosis-Pullorum",
]

ALIASES = {
    "healthy": "Healthy",
    "normal": "Healthy",
    "fowl pox": "Fowl Pox",
    "fowl-pox": "Fowl Pox",
    "fowlpox": "Fowl Pox",
    "coryza": "Infectious Coryza",
    "infectious coryza": "Infectious Coryza",
    "mycoplasmosis": "Mycoplasmosis-CRD",
    "mycoplasmosis-crd": "Mycoplasmosis-CRD",
    "crd": "Mycoplasmosis-CRD",
    "chronic respiratory disease": "Mycoplasmosis-CRD",
    "avian influenza": "Avian Influenza",
    "bird flu": "Avian Influenza",
    "fowl cholera": "Fowl Cholera",
    "infectious bronchitis": "Infectious Bronchitis",
    "mareks disease": "Marek's Disease",
    "marek's disease": "Marek's Disease",
    "newcastle": "Newcastle disease",
    "newcastle disease": "Newcastle disease",
    "infectious bursal disease": "Infectious Bursal Disease",
    "ibd": "Infectious Bursal Disease",
    "gumboro": "Infectious Bursal Disease",
    "coccidiosis": "Coccidiosis",
    "cocci": "Coccidiosis",
    "salmonella": "Salmonellosis-Pullorum",
    "salmonellosis": "Salmonellosis-Pullorum",
    "salmonellosis pullorum": "Salmonellosis-Pullorum",
    "salmonellosis-pullorum": "Salmonellosis-Pullorum",
    "pullorum": "Salmonellosis-Pullorum",
}


def normalize_disease(name: str) -> str:
    cleaned = name.strip().lower().replace("_", " ").replace("/", " ")
    return ALIASES.get(cleaned, name.strip())


def iter_images(source: Path) -> list[Path]:
    return [
        item
        for item in source.rglob("*")
        if item.is_file() and item.suffix.lower() in IMAGE_EXTENSIONS
    ]


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def existing_hashes(folder: Path) -> set[str]:
    hashes = set()
    for image in iter_images(folder):
        try:
            hashes.add(file_hash(image))
        except Exception:
            continue
    return hashes


def create_folders(data_dir: Path) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    for disease in FACE_DISEASES:
        folder = data_dir / disease
        folder.mkdir(parents=True, exist_ok=True)
        keep = folder / ".gitkeep"
        keep.touch(exist_ok=True)
    print(f"Created face dataset folders in: {data_dir}")


def status(data_dir: Path) -> None:
    create_folders(data_dir)
    print("\nFace dataset status:")
    total = 0
    for disease in FACE_DISEASES:
        folder = data_dir / disease
        count = len([p for p in iter_images(folder) if p.name != ".gitkeep"])
        total += count
        print(f"  {disease:28} {count:5} images")
    print(f"\nTotal: {total} images")


def save_resized_image(source: Path, destination: Path, max_size: int, quality: int) -> None:
    with Image.open(source) as image:
        image = ImageOps.exif_transpose(image).convert("RGB")
        image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        destination.parent.mkdir(parents=True, exist_ok=True)
        image.save(destination, format="JPEG", quality=quality, optimize=True)


def import_images(
    source: Path,
    disease: str,
    data_dir: Path,
    max_size: int,
    quality: int,
    limit: int | None,
) -> None:
    disease = normalize_disease(disease)
    if disease not in FACE_DISEASES:
        raise SystemExit(
            f"Unsupported face disease: {disease}\nAllowed: {', '.join(FACE_DISEASES)}"
        )
    if not source.exists() or not source.is_dir():
        raise SystemExit(f"Source folder not found: {source}")

    create_folders(data_dir)
    destination_dir = data_dir / disease
    seen_hashes = existing_hashes(destination_dir)
    images = iter_images(source)
    if limit:
        images = images[:limit]

    imported = 0
    skipped = 0
    failed = 0

    for index, image_path in enumerate(images, start=1):
        try:
            image_hash = file_hash(image_path)
            if image_hash in seen_hashes:
                skipped += 1
                continue

            safe_name = disease.lower().replace(" ", "_").replace("'", "")
            output_name = f"{safe_name}_{image_hash[:16]}.jpg"
            output_path = destination_dir / output_name
            save_resized_image(image_path, output_path, max_size=max_size, quality=quality)
            seen_hashes.add(image_hash)
            imported += 1

            if imported % 50 == 0:
                print(f"Imported {imported} images for {disease}...")
        except Exception as exc:
            failed += 1
            print(f"Failed [{index}/{len(images)}] {image_path.name}: {exc}")

    print(f"\nDisease: {disease}")
    print(f"Source images found: {len(images)}")
    print(f"Imported: {imported}")
    print(f"Skipped duplicates: {skipped}")
    print(f"Failed: {failed}")
    status(data_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare PoultryGuardAI face image dataset.")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--create-folders", action="store_true")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--disease", help="Disease/class name to import into")
    parser.add_argument("--source", type=Path, help="Folder containing images to import")
    parser.add_argument("--max-size", type=int, default=640)
    parser.add_argument("--quality", type=int, default=85)
    parser.add_argument("--limit", type=int, help="Optional max images to import")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data_dir = args.data_dir.resolve()

    if args.create_folders:
        create_folders(data_dir)

    if args.disease and args.source:
        import_images(
            source=args.source.resolve(),
            disease=args.disease,
            data_dir=data_dir,
            max_size=args.max_size,
            quality=args.quality,
            limit=args.limit,
        )
    elif args.status or not args.create_folders:
        status(data_dir)


if __name__ == "__main__":
    main()
