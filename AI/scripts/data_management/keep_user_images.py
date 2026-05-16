#!/usr/bin/env python3
"""Keep only user's images and add minimal Healthy class."""
from pathlib import Path
import shutil

SAMPLE_DATA = Path('C:/Users/DELL/Desktop/new project/PoultryGuardAI/AI/sample_data')
DISEASE_REFS = Path('C:/Users/DELL/Desktop/new project/PoultryGuardAI/Backend/disease_references')

print("Cleaning dataset...")
print()

# Remove all folders except Infectious-Bursal-Disease
for dir_path in SAMPLE_DATA.iterdir():
    if dir_path.is_dir() and dir_path.name != 'Infectious-Bursal-Disease':
        shutil.rmtree(dir_path)
        print(f"✓ Removed: {dir_path.name}")

# Create minimal Healthy class with reference images
healthy_src = DISEASE_REFS / 'Healthy'
healthy_dst = SAMPLE_DATA / 'Healthy'
healthy_dst.mkdir(exist_ok=True)

if healthy_src.exists():
    for i, img in enumerate(healthy_src.glob('*'), 1):
        if img.is_file() and i <= 3:  # Just 3 healthy images
            shutil.copy2(img, healthy_dst / img.name)

print(f"✓ Created: Healthy (with 3 reference images)")
print()
print("Final dataset:")
for d in sorted(SAMPLE_DATA.iterdir()):
    if d.is_dir():
        count = len(list(d.glob('*.*')))
        print(f"  {d.name}: {count} images")
