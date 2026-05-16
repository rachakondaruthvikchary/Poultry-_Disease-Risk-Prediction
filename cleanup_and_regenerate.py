#!/usr/bin/env python3
"""Clean and regenerate synthetic dataset"""
import shutil
from pathlib import Path

base_dir = Path(__file__).parent / "sample_data"

# Remove synthetic images from all folders
for disease_dir in base_dir.iterdir():
    if disease_dir.is_dir():
        for synth_file in disease_dir.glob("synth_*.jpg"):
            synth_file.unlink()
            print(f"Removed: {synth_file.name}")

print("✅ Cleaned all corrupt synthetic images")
print("\nNow regenerating...")

# Regenerate
import subprocess
import sys
result = subprocess.run(
    [sys.executable, "AI/generate_training_dataset.py"],
    cwd=Path(__file__).parent
)
sys.exit(result.returncode)
