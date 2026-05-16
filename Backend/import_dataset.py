#!/usr/bin/env python3
"""
Dataset Import and Validation System
Helps users add new disease datasets and validates them
"""

import os
import shutil
import json
import shlex
from pathlib import Path
from datetime import datetime

class DatasetValidator:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.training_path = self.project_root / "AI" / "sample_data"
        self.reference_path = self.project_root / "Backend" / "disease_references"
        self.config_path = self.project_root / "disease_config.json"
        
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}
        
        # Load disease list from config with error handling
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            if 'diseases' not in self.config:
                raise KeyError("Config file missing 'diseases' key")
            self.valid_diseases = list(self.config['diseases'].keys())
        except FileNotFoundError:
            raise ValueError(f"Config file not found: {self.config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Config file is malformed JSON: {e}")
        except KeyError as e:
            raise ValueError(f"Invalid config structure: {e}")
    
    def validate_disease_name(self, disease_name):
        """Check if disease name is valid"""
        if disease_name not in self.valid_diseases:
            print(f"❌ Invalid disease name: '{disease_name}'")
            print(f"\nValid diseases:")
            for d in sorted(self.valid_diseases):
                print(f"   - {d}")
            return False
        return True
    
    def validate_image_directory(self, source_dir):
        """Validate source directory contains images"""
        source_path = Path(source_dir)
        
        if not source_path.exists():
            print(f"❌ Error: Directory not found: {source_dir}")
            return False
        
        if not source_path.is_dir():
            print(f"❌ Error: Path is not a directory: {source_dir}")
            return False
        
        # Find all images
        images = [f for f in source_path.rglob('*') 
                 if f.is_file() and f.suffix in self.image_extensions]
        
        if not images:
            print(f"❌ Error: No images found in {source_dir}")
            print(f"\nSupported formats: {', '.join(self.image_extensions)}")
            return False
        
        return images
    
    def import_images(self, disease_name, source_dir, mode="copy"):
        """Import images to disease training directory"""
        if not self.validate_disease_name(disease_name):
            return False
        
        images = self.validate_image_directory(source_dir)
        if not images:
            return False
        
        disease_dir = self.training_path / disease_name
        disease_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n{'='*70}")
        print(f"📥 IMPORTING IMAGES")
        print(f"{'='*70}")
        print(f"Disease: {disease_name}")
        print(f"Source: {source_dir}")
        print(f"Images found: {len(images)}")
        print(f"Mode: {mode}")
        
        imported = 0
        skipped = 0
        errors = 0
        
        for i, image_file in enumerate(images, 1):
            try:
                dest_file = disease_dir / image_file.name
                
                # Check for duplicates
                if dest_file.exists():
                    print(f"⊘ [{i}/{len(images)}] Skipping (exists): {image_file.name}")
                    skipped += 1
                    continue
                
                if mode == "copy":
                    shutil.copy2(image_file, dest_file)
                elif mode == "move":
                    shutil.move(str(image_file), str(dest_file))
                else:
                    print(f"✗ [{i}/{len(images)}] Error: Unsupported mode '{mode}' for {image_file.name}")
                    errors += 1
                    continue
                
                if (i % 50) == 0 or i == len(images):
                    print(f"✓ [{i}/{len(images)}] Imported: {image_file.name}")
                
                imported += 1
            
            except Exception as e:
                print(f"✗ [{i}/{len(images)}] Error importing {image_file.name}: {e}")
                errors += 1
        
        print(f"\n{'─'*70}")
        print(f"✅ Import complete!")
        print(f"   Imported: {imported}")
        print(f"   Skipped: {skipped}")
        print(f"   Errors: {errors}")
        
        return imported > 0
    
    def validate_dataset(self, disease_name):
        """Validate dataset integrity"""
        if not self.validate_disease_name(disease_name):
            return False
        
        disease_dir = self.training_path / disease_name
        
        if not disease_dir.exists():
            print(f"⚠️  Disease directory not found: {disease_dir}")
            return False
        
        images = [f for f in disease_dir.rglob('*')
                 if f.is_file() and f.suffix in self.image_extensions]
        
        print(f"\n{'='*70}")
        print(f"🔍 VALIDATING DATASET: {disease_name}")
        print(f"{'='*70}")
        print(f"Found images: {len(images)}")
        
        if len(images) == 0:
            print(f"⚠️  No images found in {disease_dir}")
            return False
        
        # Check image integrity
        tiny = 0
        huge = 0
        
        for image_file in images:
            size = image_file.stat().st_size
            
            # Check if file is too small (corrupted)
            if size < 1024:  # Less than 1KB
                print(f"⚠️  Tiny file (corrupted?): {image_file.name} ({size} bytes)")
                tiny += 1
            
            # Check if file is too large
            if size > 10 * 1024 * 1024:  # More than 10MB
                print(f"⚠️  Large file: {image_file.name} ({size/(1024*1024):.2f} MB)")
                huge += 1
        
        print(f"\n{'─'*70}")
        print(f"✅ Validation complete!")
        print(f"   Total images: {len(images)}")
        print(f"   Corrupted/tiny: {tiny}")
        print(f"   Too large: {huge}")
        print(f"   Status: {'✅ VALID' if (tiny + huge) == 0 else '⚠️  NEEDS ATTENTION'}")
        
        return True
    
    def list_diseases_needing_images(self):
        """Show which diseases need image data"""
        print(f"\n{'='*70}")
        print(f"📊 DATASET STATUS")
        print(f"{'='*70}\n")
        
        print("✅ DISEASES WITH TRAINING IMAGES:")
        for disease, config in self.config['diseases'].items():
            count = config.get('training_images', 0)
            if count > 0:
                priority = config.get('priority', 'UNKNOWN')
                print(f"   ✓ {disease:35} {count:5} images  [{priority}]")
        
        print(f"\n❌ DISEASES NEEDING IMAGES (PRIORITY ORDER):")
        
        # Group by priority
        priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2}
        needs_images = []
        
        for disease, config in self.config['diseases'].items():
            count = config.get('training_images', 0)
            if count == 0:
                priority = config.get('priority', 'UNKNOWN')
                needs_images.append((disease, priority))
        
        needs_images.sort(key=lambda x: priority_order.get(x[1], 999))
        
        for disease, priority in needs_images:
            print(f"   ✗ {disease:35} [PRIORITY: {priority}]")
        
        print(f"\n{'─'*70}")
        print(f"Coverage: {sum(1 for d in self.config['diseases'].values() if d.get('training_images', 0) > 0)}/{len(self.config['diseases'])} diseases")
    
    def generate_import_script(self, disease_name, source_dir):
        """Generate one-liner import command"""
        if not self.validate_disease_name(disease_name):
            return None
        
        safe_disease = shlex.quote(disease_name)
        safe_source = shlex.quote(source_dir)
        
        script = f'''
# Import images for {disease_name}
python Backend/import_dataset.py \\
    --disease {safe_disease} \\
    --source {safe_source} \\
    --mode copy \\
    --validate
'''
        return script


def main():
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="PoultryGuardAI Dataset Manager")
    parser.add_argument("--disease", help="Disease name to import images for")
    parser.add_argument("--source", help="Source directory containing images")
    parser.add_argument("--validate", nargs="?", const=True, help="Validate dataset (optionally specify disease)")
    parser.add_argument("--mode", default="copy", choices=["copy", "move"], help="Import mode: copy or move")
    
    args = parser.parse_args()
    
    project_root = Path(__file__).parent.parent
    
    try:
        validator = DatasetValidator(project_root)
    except ValueError as e:
        print(f"❌ Error initializing validator: {e}")
        return
    
    print("\n🐔 PoultryGuardAI Dataset Manager\n")
    
    if args.disease and args.source:
        # Import mode
        validator.import_images(args.disease, args.source, mode=args.mode)
        if args.validate:
            validator.validate_dataset(args.disease)
    elif args.validate is True or (isinstance(args.validate, str) and args.validate):
        # Validate mode
        disease_to_validate = args.validate if isinstance(args.validate, str) else None
        if disease_to_validate:
            validator.validate_dataset(disease_to_validate)
        else:
            print("Error: --validate requires a disease name")
    else:
        # Show usage
        validator.list_diseases_needing_images()
        print(f"\n{'='*70}")
        print("📚 USAGE EXAMPLES")
        print(f"{'='*70}\n")
        print("1️⃣  Import images for a disease:")
        print("   python Backend/import_dataset.py --disease 'Newcastle disease' --source './data/newcastle'")
        print("\n2️⃣  Validate dataset:")
        print("   python Backend/import_dataset.py --validate 'Avian Influenza'")
        print("\n3️⃣  See full dataset audit:")
        print("   python AI/manage_datasets.py")


if __name__ == "__main__":
    main()
