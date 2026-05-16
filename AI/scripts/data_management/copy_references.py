#!/usr/bin/env python3
"""Copy reference images from Backend/disease_references to AI/sample_data
to populate all disease classes for training.
"""
from pathlib import Path
import shutil

BACKEND_ROOT = Path(__file__).resolve().parents[1] / "Backend"
OUT_DIR = Path(__file__).resolve().parents[1] / "AI" / "sample_data"

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

print("Copying reference images from Backend/disease_references...")
print("="*60)

total_copied = 0

for ref_folder in sorted(BACKEND_ROOT.joinpath("disease_references").iterdir()):
    if not ref_folder.is_dir():
        continue
    
    ref_disease = ref_folder.name
    canonical = REF_TO_CANONICAL.get(ref_disease, ref_disease)
    dest_dir = OUT_DIR / canonical
    
    # Count existing
    existing_count = len(list(dest_dir.glob("*.*"))) if dest_dir.exists() else 0
    
    # Copy all images from reference
    images = [p for p in ref_folder.glob("*") if p.is_file() and p.suffix.lower() in {'.jpg','.jpeg','.png','.bmp','.webp'}]
    
    dest_dir.mkdir(parents=True, exist_ok=True)
    copied_count = 0
    
    for src_img in images:
        dest_path = dest_dir / src_img.name
        if not dest_path.exists():
            try:
                shutil.copy2(src_img, dest_path)
                copied_count += 1
                total_copied += 1
            except Exception as e:
                print(f"  ERROR copying {src_img.name}: {e}")
    
    final_count = len(list(dest_dir.glob("*.*")))
    print(f"{canonical:30s}: {final_count:3d} images ({copied_count} new)")

print("="*60)
print(f"Total copied: {total_copied}")
print("\nFinal dataset composition:")
for disease_dir in sorted(OUT_DIR.iterdir()):
    if disease_dir.is_dir():
        count = len(list(disease_dir.glob("*.*")))
        if count > 0:
            print(f"  {disease_dir.name:35s}: {count:4d} images")
