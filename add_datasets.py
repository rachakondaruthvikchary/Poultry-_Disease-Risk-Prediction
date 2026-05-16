#!/usr/bin/env python3
"""
Add Disease Dataset Utility
Easily add new disease images to training and reference folders
"""

import argparse
import shutil
import json
from pathlib import Path
from datetime import datetime

from AI.disease_names import CANONICAL_DISEASES, normalize_disease_name

def add_dataset(disease: str, source: str, mode: str = "both", copy: bool = True):
    """
    Add dataset images to disease folders
    
    Args:
        disease: Disease name (e.g., "Newcastle disease")
        source: Source folder path with images
        mode: "training", "reference", or "both"
        copy: If True, copy files; if False, just count
    """
    
    disease = normalize_disease_name(disease)
    if disease not in CANONICAL_DISEASES:
        print(f"❌ Error: Unsupported disease: {disease}")
        print(f"   Allowed: {', '.join(CANONICAL_DISEASES)}")
        return False

    base_path = Path(__file__).parent
    training_path = base_path / "AI" / "sample_data"
    reference_path = base_path / "Backend" / "disease_references"
    
    source_path = Path(source)
    
    if not source_path.exists():
        print(f"❌ Error: Source folder not found: {source}")
        return False
    
    # Get all image files
    image_extensions = ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']
    image_files = [f for f in source_path.iterdir() 
                   if f.is_file() and f.suffix in image_extensions]
    
    if not image_files:
        print(f"❌ Error: No images found in {source}")
        return False
    
    print(f"\n{'='*70}")
    print(f"📦 ADDING DISEASE DATA")
    print(f"{'='*70}")
    print(f"  Disease: {disease}")
    print(f"  Source: {source_path.name}")
    print(f"  Images: {len(image_files)}")
    print(f"  Mode: {mode}")
    print(f"  Action: {'Copy' if copy else 'Count only'}")
    print(f"{'='*70}\n")
    
    added_count = 0
    
    # Training data
    if mode in ["training", "both"]:
        train_folder = training_path / disease
        train_folder.mkdir(parents=True, exist_ok=True)
        
        print(f"🎓 Training Data ({train_folder}):")
        for img_file in image_files:
            if copy:
                shutil.copy2(img_file, train_folder / img_file.name)
                print(f"  ✅ {img_file.name}")
            added_count += 1
        print()
    
    # Reference data
    if mode in ["reference", "both"]:
        ref_folder = reference_path / disease
        ref_folder.mkdir(parents=True, exist_ok=True)
        
        print(f"🏥 Reference Data ({ref_folder}):")
        for img_file in image_files:
            if copy:
                shutil.copy2(img_file, ref_folder / img_file.name)
                print(f"  ✅ {img_file.name}")
        print()
    
    print(f"✅ Successfully added {len(image_files)} images to {disease} ({mode})")
    print(f"⏭️  Next: Retrain the model with: python AI/training/train_cnn.py\n")
    
    return True


def show_supported_diseases():
    """Display all supported diseases"""
    config_file = Path(__file__).parent / "disease_config.json"
    
    if not config_file.exists():
        print("❌ disease_config.json not found")
        return
    
    with open(config_file) as f:
        config = json.load(f)
    
    print("\n" + "="*70)
    print("📋 SUPPORTED DISEASES")
    print("="*70 + "\n")
    
    for disease, info in config["diseases"].items():
        training = "✅" if info["training"] else "❌"
        reference = "✅" if info["reference"] else "❌"
        priority = info["priority"]
        
        print(f"{disease}")
        print(f"  Training: {training}  Reference: {reference}  Priority: {priority}")
        print(f"  {info['description']}\n")
    
    summary = config["summary"]
    print("="*70)
    print(f"Total Diseases: {summary['total_diseases']}")
    print(f"Training Images: {summary['total_training_images']}")
    print(f"Reference Images: {summary['total_reference_images']}")
    print("="*70 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Add disease dataset images to PoultryGuardAI"
    )
    
    parser.add_argument(
        "--disease",
        type=str,
        required=True,
        help="Disease name (e.g., 'Newcastle disease' or 'Salmonellosis/Pullorum')"
    )
    
    parser.add_argument(
        "--source",
        type=str,
        required=True,
        help="Source folder containing images"
    )
    
    parser.add_argument(
        "--mode",
        type=str,
        choices=["training", "reference", "both"],
        default="both",
        help="Where to add images (default: both)"
    )
    
    parser.add_argument(
        "--count-only",
        action="store_true",
        help="Count images without copying"
    )
    
    parser.add_argument(
        "--list-diseases",
        action="store_true",
        help="Show all supported diseases"
    )
    
    args = parser.parse_args()
    
    if args.list_diseases:
        show_supported_diseases()
    else:
        add_dataset(
            disease=args.disease,
            source=args.source,
            mode=args.mode,
            copy=not args.count_only
        )
