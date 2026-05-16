#!/usr/bin/env python3
"""
Disease Data Management System
Organize, validate, and manage disease training and reference data
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List

from AI.disease_names import normalize_disease_name

class DiseaseDataManager:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.training_path = self.base_path / "AI" / "sample_data"
        self.reference_path = self.base_path / "Backend" / "disease_references"
        
        # List of supported diseases
        self.diseases = {
            "Newcastle disease": {"training": True, "reference": True},
            "Salmonellosis-Pullorum": {"training": True, "reference": True},
            "Coccidiosis": {"training": True, "reference": True},
            "Healthy": {"training": True, "reference": True},
            "Avian Influenza": {"training": False, "reference": True},
            "Infectious Bursal Disease": {"training": False, "reference": True},
            "Marek's Disease": {"training": False, "reference": True},
            "Fowl Pox": {"training": False, "reference": True},
            "Infectious Bronchitis": {"training": False, "reference": True},
            "Fowl Cholera": {"training": False, "reference": True},
            "Mycoplasmosis-CRD": {"training": False, "reference": True},
            "Infectious Coryza": {"training": False, "reference": True},
        }
    
    def _glob_images(self, folder: Path) -> List[Path]:
        """Find all image files with case-insensitive extension matching"""
        if not folder.exists():
            return []
        
        images = []
        # Use case-insensitive glob patterns for common image formats
        for pattern in ["*.[jJ][pP][gG]", "*.[jJ][pP][eE][gG]", "*.[pP][nN][gG]"]:
            images.extend(folder.glob(pattern))
        
        return list(set(images))  # Remove duplicates if any
    
    def create_disease_folders(self):
        """Create all disease folders if they don't exist"""
        print("📁 Creating disease folders...\n")
        
        for disease, modes in self.diseases.items():
            if modes["training"]:
                train_folder = self.training_path / disease
                train_folder.mkdir(parents=True, exist_ok=True)
                print(f"  ✅ {disease} (Training)")
            
            if modes["reference"]:
                ref_folder = self.reference_path / disease
                ref_folder.mkdir(parents=True, exist_ok=True)
                print(f"  ✅ {disease} (Reference)")
    
    def count_images(self, disease: str, mode: str = "both") -> Dict[str, int]:
        """Count images in disease folders"""
        counts = {"training": 0, "reference": 0}
        
        if mode in ["training", "both"]:
            train_folder = self.training_path / disease
            counts["training"] = len(self._glob_images(train_folder))
        
        if mode in ["reference", "both"]:
            ref_folder = self.reference_path / disease
            counts["reference"] = len(self._glob_images(ref_folder))
        
        return counts
    
    def show_inventory(self):
        """Display current disease data inventory"""
        print("\n" + "="*70)
        print("📊 DISEASE DATA INVENTORY")
        print("="*70 + "\n")
        
        print("🎓 TRAINING DATA (AI/sample_data):")
        print("-" * 70)
        total_train = 0
        for disease in sorted(self.diseases.keys()):
            if self.diseases[disease]["training"]:
                counts = self.count_images(disease, "training")
                train_count = counts["training"]
                total_train += train_count
                status = "✅" if train_count > 0 else "⏳"
                print(f"  {status} {disease:<35} {train_count:>5} images")
        
        print(f"\n  Total Training Images: {total_train}\n")
        
        print("🏥 REFERENCE DATA (Backend/disease_references):")
        print("-" * 70)
        total_ref = 0
        for disease in sorted(self.diseases.keys()):
            if self.diseases[disease]["reference"]:
                counts = self.count_images(disease, "reference")
                ref_count = counts["reference"]
                total_ref += ref_count
                status = "✅" if ref_count > 0 else "⏳"
                print(f"  {status} {disease:<35} {ref_count:>5} images")
        
        print(f"\n  Total Reference Images: {total_ref}\n")
        print("="*70 + "\n")
    
    def add_images(self, source_folder: str, disease: str, mode: str = "both"):
        """Add images from source folder to disease folders"""
        source = Path(source_folder)
        
        if not source.exists():
            print(f"❌ Source folder not found: {source}")
            return
        
        disease = normalize_disease_name(disease)

        # Sanitize disease input: only allow known disease keys to prevent path traversal
        if disease not in self.diseases:
            print(f"❌ Unknown disease: {disease}. Allowed: {', '.join(self.diseases.keys())}")
            return

        image_files = self._glob_images(source)
        
        if not image_files:
            print(f"❌ No images found in {source}")
            return
        
        print(f"\n📁 Adding {len(image_files)} images for {disease}...\n")
        
        if mode in ["training", "both"]:
            train_folder = self.training_path / disease
            train_folder.mkdir(parents=True, exist_ok=True)
            for img in image_files:
                shutil.copy2(img, train_folder / img.name)
                print(f"  ✅ Training: {img.name}")
        
        if mode in ["reference", "both"]:
            ref_folder = self.reference_path / disease
            ref_folder.mkdir(parents=True, exist_ok=True)
            for img in image_files:
                shutil.copy2(img, ref_folder / img.name)
                print(f"  ✅ Reference: {img.name}")
        
        print(f"\n✅ Added {len(image_files)} images for {disease} ({mode})\n")


if __name__ == "__main__":
    manager = DiseaseDataManager()
    
    # Create folders
    manager.create_disease_folders()
    
    # Show inventory
    manager.show_inventory()
    
    print("\n💡 Usage Examples:")
    print("  manager.add_images('/path/to/newcastle', 'Newcastle disease', 'both')")
    print("  manager.show_inventory()")
