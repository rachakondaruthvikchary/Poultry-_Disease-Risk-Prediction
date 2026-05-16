#!/usr/bin/env python3
"""
Setup Kaggle Poultry Diseases Dataset
Extracts and organizes the dataset for training
"""

import os
import shutil
import zipfile
from pathlib import Path

# Paths
import argparse

# Configurable paths
DOWNLOADS_ZIP = os.environ.get("DOWNLOADS_ZIP")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SAMPLE_DATA = PROJECT_ROOT / "AI" / "sample_data"

# Kaggle class mapping to our disease classes
CLASS_MAPPING = {
    "cocci": "Coccidiosis",
    "healthy": "Healthy",
    "ncd": "Newcastle disease",
    "salmo": "Salmonellosis-Pullorum"
}

def extract_zip(downloads_zip: str):
    """Extract the Kaggle dataset zip"""
    print("📦 Extracting Kaggle dataset...")
    if not downloads_zip:
        raise FileNotFoundError("No DOWNLOADS_ZIP provided. Set DOWNLOADS_ZIP env or pass --downloads-zip.")

    zip_path = Path(downloads_zip)
    if not zip_path.exists():
        raise FileNotFoundError(f"ZIP file not found: {zip_path}")

    extract_path = zip_path.parent / "poultry_dataset"
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

    print(f"✅ Extracted to: {extract_path}")
    return extract_path

def organize_dataset(extract_path):
    """Organize extracted images into disease folders"""
    print("\n📁 Organizing dataset into disease folders...")
    
    # Create disease folders if they don't exist
    for disease in CLASS_MAPPING.values():
        disease_folder = SAMPLE_DATA / disease
        disease_folder.mkdir(parents=True, exist_ok=True)
    
    # Find the extracted folder structure
    extracted_dir = extract_path
    
    # Look for the actual data folders
    for kaggle_class, disease_name in CLASS_MAPPING.items():
        source_folder = None
        
        # Search for the class folder
        for item in extracted_dir.rglob("*"):
            if item.is_dir() and item.name == kaggle_class:
                source_folder = item
                break
        
        if source_folder and source_folder.exists():
            dest_folder = SAMPLE_DATA / disease_name
            image_files = list(source_folder.glob("*.jpg")) + list(source_folder.glob("*.jpeg")) + list(source_folder.glob("*.png"))
            
            print(f"\n  📸 {disease_name}: Found {len(image_files)} images")
            
            successful_copies = 0
            for image_file in image_files:
                try:
                    shutil.copy2(image_file, dest_folder / image_file.name)
                    successful_copies += 1
                except Exception as e:
                    print(f"    ⚠️  Failed to copy {image_file.name}: {e}")
            
            print(f"    ✅ Copied {successful_copies} images to {disease_name}/")
        else:
            print(f"  ⚠️  Could not find {kaggle_class} folder")

def count_images():
    """Count total images in sample_data"""
    print("\n📊 Dataset Summary:")
    total = 0
    
    for disease_folder in SAMPLE_DATA.iterdir():
        if disease_folder.is_dir():
            image_count = (len(list(disease_folder.glob("*.jpg"))) +
                         len(list(disease_folder.glob("*.jpeg"))) +
                         len(list(disease_folder.glob("*.png"))))
            total += image_count
            print(f"  {disease_folder.name}: {image_count} images")
    
    print(f"\n✅ Total images: {total}")
    return total

if __name__ == "__main__":
    print("=" * 60)
    print("🐔 PoultryGuardAI - Kaggle Dataset Setup")
    print("=" * 60)
    
    parser = argparse.ArgumentParser(description="Setup Kaggle poultry dataset")
    parser.add_argument("--downloads-zip", dest="downloads_zip", help="Path to the downloaded ZIP file (overrides DOWNLOADS_ZIP env)")
    args = parser.parse_args()

    downloads_zip = args.downloads_zip or DOWNLOADS_ZIP or (Path.home() / "Downloads" / "archive.zip")

    try:
        # Extract
        extract_path = extract_zip(str(downloads_zip))
        
        # Organize
        organize_dataset(extract_path)
        
        # Summary
        count_images()
        
        print("\n" + "=" * 60)
        print("✅ Setup complete! Ready for training.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
