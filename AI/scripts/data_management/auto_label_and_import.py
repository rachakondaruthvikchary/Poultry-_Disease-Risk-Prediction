#!/usr/bin/env python3
"""Auto-label incoming images using the feature-based predictor and copy them
into AI/sample_data/<canonical disease name>/ for training.

WARNING: Labels are heuristics (feature-based) and may be incorrect. Review
results in AI/sample_data before trusting them for final training.
"""
from __future__ import annotations
import sys
from pathlib import Path
import shutil

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
# Ensure Backend package is importable as 'app'
BACKEND_ROOT = PROJECT_ROOT / "Backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from Backend.app.services.image_model_service import ImageDiseasePredictor, DEFAULT_DISEASE_LABELS
from AI.disease_names import normalize_disease_name, CANONICAL_DISEASES

IN_DIR = PROJECT_ROOT / "AI" / "incoming_zip"
OUT_DIR = PROJECT_ROOT / "AI" / "sample_data"
UNLABELED_DIR = OUT_DIR / "Uncertain"

predictor = ImageDiseasePredictor()

images = [p for p in IN_DIR.rglob("*") if p.is_file() and p.suffix.lower() in {'.jpg','.jpeg','.png','.webp','.bmp'}]
if not images:
    print("No images found in:", IN_DIR)
    raise SystemExit(1)

counts = {}
skipped = 0
for img in images:
    try:
        b = img.read_bytes()
        res = predictor.predict(b)
        label = res.get('disease_name', 'Uncertain prediction')
        conf = res.get('confidence', 0.0)
        # map display label to canonical folder name
        canonical = normalize_disease_name(label)
        if canonical not in CANONICAL_DISEASES:
            canonical = 'Uncertain'
        dest = OUT_DIR / canonical
        dest.mkdir(parents=True, exist_ok=True)
        # avoid name collisions
        out_name = f"{img.stem}_{img.stat().st_mtime_ns % 100000}.{img.suffix.lstrip('.')}"
        shutil.copy2(img, dest / out_name)
        counts[canonical] = counts.get(canonical, 0) + 1
        print(f"{img.name} -> {canonical} (conf={conf:.2f})")
    except Exception as exc:
        print(f"Failed to process {img}: {exc}")
        skipped += 1

print("\nSummary:")
for k, v in sorted(counts.items(), key=lambda t: -t[1]):
    print(f"  {k}: {v}")
if skipped:
    print(f"Skipped: {skipped}")

print("\nDone. Review AI/sample_data folders. Next: run the trainer if ready.")
