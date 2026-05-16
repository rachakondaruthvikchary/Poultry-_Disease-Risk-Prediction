#!/usr/bin/env python3
"""
Organize images into disease folders and train immediately
"""

import os
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "AI" / "sample_data"

# Map of disease names and image counts from user's latest upload
disease_structure = {
    "Newcastle-Disease": 4,
    "Avian-Influenza": 3,
    "Infectious-Bursal-Disease": 4,
    "Marek-Disease": 4,
    "Fowl-Pox": 4,
}

print("✅ Disease folders ready:")
for disease, count in disease_structure.items():
    folder = DATA_DIR / disease
    image_count = len(list(folder.glob("*.jpg"))) + len(list(folder.glob("*.png")))
    print(f"   {disease}: {image_count} images")

# Now start training
print("\n🚀 Starting training with all available images...")
os.chdir(PROJECT_ROOT / "AI" / "training")

import subprocess
result = subprocess.run(
    ["python", "train_fast.py"],
    capture_output=False
)

print("\n" + "="*60)
if result.returncode == 0:
    print("✅ TRAINING COMPLETED SUCCESSFULLY!")
else:
    print("❌ Training failed - check logs above")
print("="*60)
