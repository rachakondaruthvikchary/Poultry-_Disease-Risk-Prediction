#!/usr/bin/env python3
"""
Quick setup script to create all disease folders
"""
import os
from pathlib import Path

from AI.disease_names import CANONICAL_DISEASES

base = Path(__file__).resolve().parent
train_base = base / "AI" / "sample_data"
ref_base = base / "Backend" / "disease_references"

diseases = CANONICAL_DISEASES

print("📁 Creating disease folders...\n")

for disease in diseases:
    train_path = train_base / disease
    ref_path = ref_base / disease
    
    train_path.mkdir(parents=True, exist_ok=True)
    ref_path.mkdir(parents=True, exist_ok=True)
    
    print(f"✅ {disease}")

print("\n📊 Training folders:")
for folder in sorted(train_base.iterdir()):
    if folder.is_dir():
        print(f"  • {folder.name}")

print("\n🏥 Reference folders:")
for folder in sorted(ref_base.iterdir()):
    if folder.is_dir():
        print(f"  • {folder.name}")

print(f"\n🎉 All {len(diseases)} diseases set up successfully!")
