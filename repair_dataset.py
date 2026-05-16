#!/usr/bin/env python3
"""
Validate and repair all disease images in the dataset
Removes or re-encodes corrupt files
"""

from pathlib import Path
from PIL import Image
import io

DATA_DIR = Path(__file__).parent / "AI" / "sample_data"

print("🔍 Validating and repairing dataset...")
print("=" * 70)

total = 0
valid = 0
corrupt = 0
repaired = 0

for disease_dir in sorted(DATA_DIR.iterdir()):
    if not disease_dir.is_dir():
        continue
    
    disease_name = disease_dir.name
    disease_valid = 0
    disease_corrupt = 0
    
    for img_file in disease_dir.glob("*.jpg"):
        total += 1
        try:
            # Try to open and verify the image
            with Image.open(img_file) as img:
                # Verify it's a valid image
                if img.size[0] <= 0 or img.size[1] <= 0:
                    raise ValueError("Invalid dimensions")
                
                # Re-encode to ensure it's valid
                img_rgb = img.convert("RGB")
                
                # Save with strict quality check
                img_rgb.save(img_file, "JPEG", quality=95, optimize=False)
                valid += 1
                repaired += 1
                disease_valid += 1
                
        except Exception as e:
            disease_corrupt += 1
            corrupt += 1
            print(f"  ❌ Removing corrupt: {disease_dir.name}/{img_file.name}")
            try:
                img_file.unlink()
            except:
                pass
    
    if disease_valid + disease_corrupt > 0:
        print(f"✓ {disease_name}: {disease_valid} valid (repaired: {disease_valid})")

print("=" * 70)
print(f"\n📊 Validation Results:")
print(f"   Total files: {total}")
print(f"   Valid: {valid}")
print(f"   Corrupt (removed): {corrupt}")
print(f"   Repaired: {repaired}")

# Show final counts
print(f"\n📊 Final Dataset:")
for disease_dir in sorted(DATA_DIR.iterdir()):
    if disease_dir.is_dir():
        count = len(list(disease_dir.glob("*.jpg")))
        print(f"   - {disease_dir.name}: {count} images")

print("\n✅ Dataset repaired and ready for training!")
