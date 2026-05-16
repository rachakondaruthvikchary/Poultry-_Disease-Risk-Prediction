#!/usr/bin/env python3
"""
Dataset Management and Validation System for PoultryGuardAI
Provides comprehensive dataset auditing, organization, and validation
"""

import os
import json
import shutil
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime

class DatasetManager:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.training_path = self.project_root / "AI" / "training" / "_prepared_data"
        self.reference_path = self.project_root / "Backend" / "disease_references"
        self.config_path = self.project_root / "disease_config.json"
        
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}
        self.disease_stats = defaultdict(lambda: {'images': 0, 'size_mb': 0, 'files': []})
    
    def audit_training_datasets(self):
        """Audit all training image datasets"""
        print("\n" + "="*70)
        print("TRAINING DATASET AUDIT")
        print("="*70)
        
        if not self.training_path.exists():
            print(f"[ERROR] Training path not found: {self.training_path}")
            return {}
        
        for disease_dir in sorted(self.training_path.iterdir()):
            if not disease_dir.is_dir():
                continue
                
            disease_name = disease_dir.name
            image_files = [
                f for f in disease_dir.rglob('*')
                if f.is_file() and f.suffix in self.image_extensions
            ]
            
            total_size = sum(f.stat().st_size for f in image_files) / (1024*1024)
            self.disease_stats[disease_name]['images'] = len(image_files)
            self.disease_stats[disease_name]['size_mb'] = round(total_size, 2)
            self.disease_stats[disease_name]['type'] = 'training'
            
            status = "[OK]" if len(image_files) > 0 else "[ERROR]"
            print(f"{status} {disease_name:30} | {len(image_files):5} images | {total_size:8.2f} MB")
        
        return dict(self.disease_stats)
    
    def audit_reference_data(self):
        """Audit reference data (CSV, TSV, and other reference files)"""
        print("\n" + "="*70)
        print("REFERENCE DATA AUDIT")
        print("="*70)
        if not self.reference_path.exists():
            print(f"[ERROR] Reference path not found: {self.reference_path}")
            return {}

        reference_stats = {}

        for disease_dir in sorted(self.reference_path.iterdir()):
            if not disease_dir.is_dir():
                continue
            
            disease_name = disease_dir.name
            
            # Count reference files
            csv_files = list(disease_dir.glob('*.csv')) + list(disease_dir.glob('*.tsv'))
            txt_files = list(disease_dir.glob('*.txt'))
            json_files = list(disease_dir.glob('*.json'))
            img_files = list(disease_dir.glob('*.jpg')) + list(disease_dir.glob('*.jpeg')) + list(disease_dir.glob('*.png'))
            
            total_files = len(csv_files) + len(txt_files) + len(json_files) + len(img_files)
            
            reference_stats[disease_name] = {
                'csv_files': len(csv_files),
                'txt_files': len(txt_files),
                'json_files': len(json_files),
                'img_files': len(img_files),
                'total_files': total_files,
                'files': [f.name for f in csv_files + txt_files + json_files + img_files]
            }
            
            status = "[OK]" if total_files > 0 else "[WAIT]"
            print(f"{status} {disease_name:30} | {total_files:3} reference files")
            
            if reference_stats[disease_name]['files']:
                for fname in reference_stats[disease_name]['files']:
                    print(f"   - {fname}")
        
        return reference_stats
    
    def generate_config_report(self):
        """Generate comprehensive config report"""
        print("\n" + "="*70)
        print("CONFIG STATUS REPORT")
        print("="*70)
        
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            diseases = config.get('diseases', {})
            summary = config.get('summary', {})
            
            print(f"\n[OK] Config file: {self.config_path}")
            print(f"   Total diseases: {len(diseases)}")
            print(f"   Config version: {summary.get('last_updated', 'unknown')}")
            
            print(f"\nDisease breakdown:")
            training_count = sum(1 for d in diseases.values() if d.get('training'))
            reference_count = sum(1 for d in diseases.values() if d.get('reference'))
            print(f"   - Training enabled: {training_count}/{len(diseases)}")
            print(f"   - Reference enabled: {reference_count}/{len(diseases)}")
            
            print(f"\nConfigured image counts:")
            total_training = sum(d.get('training_images', 0) for d in diseases.values())
            total_reference = sum(d.get('reference_images', 0) for d in diseases.values())
            print(f"   - Training images: {total_training}")
            print(f"   - Reference images: {total_reference}")
            
            return config
        
        except Exception as e:
            print(f"[ERROR] Error reading config: {e}")
            return None
    
    def update_config_with_actual_counts(self):
        """Update disease_config.json with actual image counts"""
        print("\n" + "="*70)
        print("UPDATING CONFIG WITH ACTUAL COUNTS")
        print("="*70)
        
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            updated = False
            
            diseases_cfg = config.get('diseases', {})
            for disease_name, stats in self.disease_stats.items():
                if disease_name in diseases_cfg:
                    old_count = diseases_cfg[disease_name].get('training_images', 0)
                    new_count = stats['images']

                    if old_count != new_count:
                        diseases_cfg[disease_name]['training_images'] = new_count
                        print(f"Update {disease_name}: {old_count} -> {new_count} images")
                        updated = True
                    
                    # Auto-enable training if images exist
                    if new_count > 0 and not diseases_cfg[disease_name].get('training'):
                        diseases_cfg[disease_name]['training'] = True
                        print(f"Enable training for {disease_name}")
                        updated = True

            # Update reference counts as well
            reference_stats = self.audit_reference_data()
            for disease_name, stats in reference_stats.items():
                if disease_name in diseases_cfg:
                    old_ref_count = diseases_cfg[disease_name].get('reference_images', 0)
                    new_ref_count = stats['img_files']
                    if old_ref_count != new_ref_count:
                        diseases_cfg[disease_name]['reference_images'] = new_ref_count
                        print(f"Update {disease_name} reference: {old_ref_count} -> {new_ref_count} images")
                        updated = True
            
            if updated:
                config['summary']['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                config['summary']['total_training_images'] = sum(
                    d.get('training_images', 0) for d in config['diseases'].values()
                )
                config['summary']['total_reference_images'] = sum(
                    d.get('reference_images', 0) for d in config['diseases'].values()
                )
                config['summary']['training_enabled'] = sum(
                    1 for d in config['diseases'].values() if d.get('training')
                )
                
                with open(self.config_path, 'w') as f:
                    json.dump(config, f, indent=2)
                
                print(f"\n[OK] Config updated successfully!")
                return True
            else:
                print(f"\n[OK] Config already up to date")
                return False
        
        except Exception as e:
            print(f"[ERROR] Error updating config: {e}")
            return False
    
    def generate_dataset_report(self):
        """Generate comprehensive dataset report"""
        print("\n" + "="*70)
        print("COMPLETE DATASET REPORT")
        print("="*70)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'project_root': str(self.project_root),
            'training_datasets': dict(self.disease_stats),
            'summary': {
                'total_diseases_configured': 0,
                'diseases_with_training_images': 0,
                'total_training_images': 0,
                'total_training_size_mb': 0,
                'diseases_without_images': []
            }
        }
        
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                report['total_diseases_configured'] = len(config.get('diseases', {}))
        except Exception as e:
            print(f"[WAIT] Could not read config at {self.config_path}: {e}")
        
        diseases_with_images = []
        diseases_without_images = []
        total_images = 0
        total_size = 0
        
        for disease, stats in self.disease_stats.items():
            if stats['images'] > 0:
                diseases_with_images.append(disease)
                total_images += stats['images']
                total_size += stats['size_mb']
            else:
                diseases_without_images.append(disease)
        
        report['summary']['diseases_with_training_images'] = len(diseases_with_images)
        report['summary']['total_training_images'] = total_images
        report['summary']['total_training_size_mb'] = round(total_size, 2)
        report['summary']['diseases_without_images'] = diseases_without_images
        
        print(f"\n[OK] Diseases with training images: {len(diseases_with_images)}/{report['total_diseases_configured']}")
        for disease in sorted(diseases_with_images):
            stats = self.disease_stats[disease]
            print(f"   [OK] {disease}: {stats['images']} images ({stats['size_mb']} MB)")
        
        print(f"\n[ERROR] Diseases WITHOUT training images: {len(diseases_without_images)}")
        for disease in sorted(diseases_without_images):
            print(f"   [ERROR] {disease}")
        
        print(f"\nTotal statistics:")
        print(f"   - Total training images: {total_images}")
        print(f"   - Total storage: {total_size:.2f} MB")
        print(f"   - Coverage: {len(diseases_with_images)}/{report['total_diseases_configured']} diseases")
        
        return report
    
    def run_full_audit(self):
        """Run complete audit and update config"""
        print("\nSTARTING COMPLETE DATASET AUDIT...\n")
        
        # 1. Audit training data
        training_stats = self.audit_training_datasets()
        
        # 2. Audit reference data  
        reference_stats = self.audit_reference_data()
        
        # 3. Check config
        config = self.generate_config_report()
        
        # 4. Update config with actual counts
        self.update_config_with_actual_counts()
        
        # 5. Generate final report
        report = self.generate_dataset_report()
        
        print("\n" + "="*70)
        print("AUDIT COMPLETE")
        print("="*70)
        
        return {
            'training': training_stats,
            'reference': reference_stats,
            'config': config,
            'report': report
        }


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent.parent
    manager = DatasetManager(project_root)
    audit_results = manager.run_full_audit()
