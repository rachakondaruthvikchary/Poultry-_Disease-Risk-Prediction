#!/usr/bin/env python3
from pathlib import Path

base = Path("AI/sample_data")
count = 0
for d in base.iterdir():
    if d.is_dir():
        for f in d.glob("synth_*.jpg"):
            f.unlink()
            count += 1

print(f"✅ Removed {count} corrupt synthetic images")
print("Dataset cleaned! Running training now...\n")

import subprocess
import sys
result = subprocess.run(
    [sys.executable, "AI/training/train_robust.py"],
    cwd=Path(__file__).parent
)
sys.exit(result.returncode)
