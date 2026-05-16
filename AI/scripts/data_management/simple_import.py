#!/usr/bin/env python3
"""Simple import of incoming images using basic image similarity matching.
Uses PIL histograms to find nearest reference image and assign disease label.
"""
from pathlib import Path
import shutil
from PIL import Image
import numpy as np
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "Backend"
IN_DIR = PROJECT_ROOT / "AI" / "incoming_zip"
REF_DIR = BACKEND_ROOT / "disease_references"
OUT_DIR = PROJECT_ROOT / "AI" / "sample_data"

# Map reference disease folders to canonical names
REF_TO_CANONICAL = {
    "Avian Influenza": "Avian-Influenza",
    "Coccidiosis": "Coccidiosis",
    "Fowl Cholera": "Fowl-Cholera",
    "Fowl Pox": "Fowl-Pox",
    "Healthy": "Healthy",
    "Infectious Bronchitis": "Infectious-Bronchitis",
    "Infectious Bursal Disease": "Infectious-Bursal-Disease",
    "Infectious Coryza": "Infectious-Coryza",
    "Marek's Disease": "Mareks-Disease",
    "Mycoplasmosis-CRD": "Mycoplasmosis-CRD",
    "Newcastle disease": "Newcastle-Disease",
    "Salmonellosis-Pullorum": "Salmonellosis-Pullorum",
}

def histogram_distance(img1, img2):
    """Compute histogram similarity between two images."""
    try:
        img1 = img1.convert('RGB')
        img2 = img2.convert('RGB')
        h1 = np.array(img1.histogram())
        h2 = np.array(img2.histogram())
        return np.sqrt(np.sum((h1 - h2) ** 2))
    except:
        return float('inf')

def find_nearest_disease(img_path, ref_samples):
    """Find disease with minimum histogram distance to input image."""
    try:
        img = Image.open(img_path)
        best_disease = None
        best_dist = float('inf')
        for disease, ref_img in ref_samples.items():
            dist = histogram_distance(img, ref_img)
            if dist < best_dist:
                best_dist = dist
                best_disease = disease
        return best_disease, best_dist
    except Exception as e:
        print(f"  Error processing {img_path.name}: {e}")
        return None, float('inf')

# Load reference samples (one per disease)
ref_samples = {}
print("Loading reference samples...")
for ref_folder in sorted(REF_DIR.iterdir()):
    if not ref_folder.is_dir():
        continue
    ref_disease = ref_folder.name
    canonical = REF_TO_CANONICAL.get(ref_disease, ref_disease)
    
    # Get first valid image from folder
    for ref_img_path in sorted(ref_folder.glob("*")):
        if ref_img_path.suffix.lower() in {'.jpg','.jpeg','.png','.bmp','.webp'}:
            try:
                ref_img = Image.open(ref_img_path)
                ref_samples[canonical] = ref_img
                print(f"  {canonical}: {ref_img_path.name}")
                break
            except:
                pass
    if canonical not in ref_samples:
        print(f"  {canonical}: NO REFERENCE IMAGE FOUND")

# Import incoming images
in_images = sorted([p for p in IN_DIR.rglob("*") if p.is_file() and p.suffix.lower() in {'.jpg','.jpeg','.png','.bmp','.webp'}])
print(f"\nImporting {len(in_images)} incoming images...")

assigned = defaultdict(list)
unassigned = []

for idx, img_path in enumerate(in_images):
    disease, dist = find_nearest_disease(img_path, ref_samples)
    if disease is None:
        unassigned.append(img_path)
        print(f"[{idx+1}/{len(in_images)}] {img_path.name}: UNASSIGNED (error)")
        continue
    
    assigned[disease].append(img_path)
    dest_dir = OUT_DIR / disease
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / img_path.name
    
    # Avoid overwriting
    if dest_path.exists():
        stem = img_path.stem
        suffix = img_path.suffix
        counter = 1
        while dest_path.exists():
            dest_path = dest_dir / f"{stem}_{counter}{suffix}"
            counter += 1
    
    try:
        shutil.copy2(img_path, dest_path)
        print(f"[{idx+1}/{len(in_images)}] {img_path.name} -> {disease}/")
    except Exception as e:
        print(f"[{idx+1}/{len(in_images)}] {img_path.name}: COPY FAILED ({e})")

# Summary
print("\n" + "="*60)
print("IMPORT SUMMARY")
print("="*60)
for disease in sorted(assigned.keys()):
    print(f"{disease}: {len(assigned[disease])} images")
if unassigned:
    print(f"Unassigned: {len(unassigned)} images")
print("="*60)

# Verify dataset
print("\nDataset now contains:")
for disease_dir in sorted(OUT_DIR.iterdir()):
    if disease_dir.is_dir() and disease_dir.name != "Uncertain":
        count = len(list(disease_dir.glob("*.*")))
        print(f"  {disease_dir.name}: {count} images")
