#!/usr/bin/env python3
"""
PoultryGuardAI Dataset Setup Verification
Complete system check and validation
"""

import os
import json
from pathlib import Path
from datetime import datetime

class SetupVerifier:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'checks': {},
            'summary': {},
            'status': 'UNKNOWN'
        }
    
    def check_directory_structure(self):
        """Verify all required directories exist"""
        print("\n" + "="*70)
        print("DIRECTORY STRUCTURE CHECK")
        print("="*70)
        
        required_dirs = [
            "AI/data",
            "AI/training/_prepared_data",
            "AI/inference",
            "Backend",
            "Backend/disease_references",
            "Database",
            "Frontend/src",
            "docs",
            "scripts"
        ]
        
        check_result = {'required': {}, 'status': 'PASS'}
        
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            exists = full_path.exists() and full_path.is_dir()
            status = "[OK]" if exists else "[ERROR]"
            print(f"{status} {dir_path}")
            check_result['required'][dir_path] = exists
            if not exists:
                check_result['status'] = 'FAIL'
        
        self.results['checks']['directory_structure'] = check_result
        return check_result['status'] == 'PASS'
    
    def check_disease_folders(self):
        """Verify all disease folders exist"""
        print("\n" + "="*70)
        print("DISEASE FOLDERS CHECK")
        print("="*70)
        
        diseases = [
            "Avian Influenza",
            "Coccidiosis",
            "Fowl Cholera",
            "Fowl Pox",
            "Healthy",
            "Infectious Bronchitis",
            "Infectious Bursal Disease",
            "Infectious Coryza",
            "Marek's Disease",
            "Mycoplasmosis-CRD",
            "Newcastle disease",
            "Salmonellosis-Pullorum"
        ]
        
        sample_data_path = self.project_root / "AI" / "training" / "_prepared_data"
        reference_path = self.project_root / "Backend" / "disease_references"
        
        check_result = {
            'sample_data': {},
            'reference': {},
            'status': 'PASS'
        }
        
        for disease in diseases:
            sample_dir = sample_data_path / disease
            ref_dir = reference_path / disease
            
            sample_exists = sample_dir.exists()
            ref_exists = ref_dir.exists()
            
            status_sample = "[OK]" if sample_exists else "[WAIT]"
            status_ref = "[OK]" if ref_exists else "[WAIT]"
            
            print(f"{status_sample} Sample: {disease:35} | {status_ref} Ref: {disease}")
            
            check_result['sample_data'][disease] = sample_exists
            check_result['reference'][disease] = ref_exists
        
        self.results['checks']['disease_folders'] = check_result
        return True
    
    def check_config_file(self):
        """Verify disease_config.json"""
        print("\n" + "="*70)
        print("CONFIGURATION FILE CHECK")
        print("="*70)
        
        config_path = self.project_root / "disease_config.json"
        check_result = {'status': 'FAIL', 'details': {}}
        
        if not config_path.exists():
            print(f"[ERROR] Config file not found: {config_path}")
            self.results['checks']['config'] = check_result
            return False
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            print(f"[OK] Config file found and valid JSON")
            
            diseases = config.get('diseases', {})
            print(f"[OK] Total diseases configured: {len(diseases)}")
            
            summary = config.get('summary', {})
            total_images = summary.get('total_training_images', 0)
            print(f"[OK] Total training images in config: {total_images}")
            
            check_result['status'] = 'PASS'
            check_result['diseases_count'] = len(diseases)
            check_result['total_training_images'] = total_images
            check_result['last_updated'] = summary.get('last_updated', 'unknown')
            
            print(f"[OK] Last updated: {check_result['last_updated']}")
            
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON in config: {e}")
        except Exception as e:
            print(f"[ERROR] Error reading config: {e}")
        
        self.results['checks']['config'] = check_result
        return check_result['status'] == 'PASS'
    
    def check_image_datasets(self):
        """Count images in each disease folder"""
        print("\n" + "="*70)
        print("IMAGE DATASETS CHECK")
        print("="*70)
        
        sample_data_path = self.project_root / "AI" / "training" / "_prepared_data"
        
        if not sample_data_path.exists() or not sample_data_path.is_dir():
            print(f"[ERROR] Sample data path not found: {sample_data_path}")
            check_result = {'datasets': {}, 'total_images': 0, 'status': 'FAIL'}
            self.results['checks']['images'] = check_result
            return False
        
        image_extensions = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}
        
        check_result = {'datasets': {}, 'total_images': 0, 'status': 'PASS'}
        
        for disease_dir in sorted(sample_data_path.iterdir()):
            if not disease_dir.is_dir():
                continue
            
            disease_name = disease_dir.name
            images = [f for f in disease_dir.rglob('*')
                     if f.is_file() and f.suffix in image_extensions]
            
            count = len(images)
            status = "[OK]" if count > 0 else "[ERROR]"
            
            print(f"{status} {disease_name:35} {count:5} images")
            
            check_result['datasets'][disease_name] = count
            check_result['total_images'] += count
        
        print(f"\n{'-'*70}")
        print(f"Total images across all diseases: {check_result['total_images']}")
        
        self.results['checks']['images'] = check_result
        return True
    
    def check_reference_data(self):
        """Check reference data files"""
        print("\n" + "="*70)
        print("REFERENCE DATA CHECK")
        print("="*70)
        
        reference_path = self.project_root / "Backend" / "disease_references"
        check_result = {'files': {}, 'status': 'PASS'}
        
        # Check for key reference files
        expected_files = [
            'avian_influenza_empres_india.csv',
            'mareks_disease_ncbi_taxonomy.tsv',
            'REFERENCE_DATA_README.md'
        ]
        
        for filename in expected_files:
            file_path = reference_path / filename
            exists = file_path.exists()
            status = "[OK]" if exists else "[WAIT]"
            print(f"{status} {filename}")
            check_result['files'][filename] = exists
        
        self.results['checks']['reference_data'] = check_result
        return True
    
    def check_management_scripts(self):
        """Verify dataset management scripts exist"""
        print("\n" + "="*70)
        print("MANAGEMENT SCRIPTS CHECK")
        print("="*70)
        
        scripts = [
            ('AI/scripts/data_management/manage_datasets.py', 'Dataset audit tool'),
            ('Backend/import_dataset.py', 'Dataset import tool'),
            ('Backend/add_sample_data.py', 'Legacy import script'),
            ('add_datasets.py', 'Root level import script')
        ]
        
        check_result = {'scripts': {}, 'status': 'PASS'}
        
        for script_path, description in scripts:
            full_path = self.project_root / script_path
            exists = full_path.exists()
            status = "[OK]" if exists else "[WAIT]"
            print(f"{status} {script_path:40} - {description}")
            check_result['scripts'][script_path] = exists
        
        self.results['checks']['scripts'] = check_result
        return True
    
    def check_documentation(self):
        """Verify documentation files"""
        print("\n" + "="*70)
        print("DOCUMENTATION CHECK")
        print("="*70)
        
        docs = [
            'docs/START_HERE.txt',
            'docs/QUICK_START.txt',
            'README.md'
        ]
        
        check_result = {'docs': {}, 'status': 'PASS'}
        
        for doc_path in docs:
            full_path = self.project_root / doc_path
            exists = full_path.exists()
            status = "[OK]" if exists else "[WAIT]"
            print(f"{status} {doc_path}")
            check_result['docs'][doc_path] = exists
        
        self.results['checks']['documentation'] = check_result
        return True
    
    def generate_final_report(self):
        """Generate comprehensive final report"""
        print("\n" + "="*70)
        print("FINAL VERIFICATION REPORT")
        print("="*70)
        
        # Calculate coverage
        images_check = self.results['checks'].get('images', {})
        config_check = self.results['checks'].get('config', {})
        
        total_images = images_check.get('total_images', 0)
        config_images = config_check.get('total_training_images', 0)
        
        datasets_with_images = len([d for d in images_check.get('datasets', {}).values() if d > 0])
        total_diseases = config_check.get('diseases_count', 12)
        
        coverage_percent = (datasets_with_images / total_diseases * 100) if total_diseases > 0 else 0
        
        print(f"\n[OK] SYSTEM STATUS SUMMARY")
        print(f"{'-'*70}")
        print(f"Total Diseases Configured:     {total_diseases}")
        print(f"Diseases with Training Images: {datasets_with_images}/{total_diseases} ({coverage_percent:.1f}%)")
        print(f"Total Training Images:         {total_images:,}")
        print(f"Config Status:                 {config_check.get('status', 'UNKNOWN')}")
        print(f"Directory Structure:           {self.results['checks'].get('directory_structure', {}).get('status', 'UNKNOWN')}")
        
        # Determine overall status
        all_pass = all(c.get('status', 'FAIL') == 'PASS' for c in self.results['checks'].values() if 'status' in c)
        self.results['status'] = 'READY' if all_pass and total_images > 0 else 'INCOMPLETE'
        
        print(f"\nTARGET OVERALL STATUS: {self.results['status']}")
        
        if self.results['status'] == 'READY':
            print(f"\n[OK] Setup is READY for model training!")
        else:
            print(f"\n[WAIT] Setup is INCOMPLETE. Missing datasets needed.")
            print(f"\nNext steps:")
            print(f"  1. Add images for priority diseases (see docs)")
            print(f"  2. Run: python AI/scripts/data_management/manage_datasets.py")
            print(f"  3. Update disease_config.json with new counts")
            print(f"  4. Re-run this verification")
        
        return self.results
    
    def run_complete_verification(self):
        """Run all verification checks"""
        print("\n[*] STARTING COMPLETE SETUP VERIFICATION...\n")
        
        checks = [
            self.check_directory_structure,
            self.check_disease_folders,
            self.check_config_file,
            self.check_image_datasets,
            self.check_reference_data,
            self.check_management_scripts,
            self.check_documentation
        ]
        
        for check in checks:
            try:
                check()
            except Exception as e:
                print(f"[WAIT] Error during check: {e}")
        
        report = self.generate_final_report()
        
        print(f"\n{'='*70}")
        print(f"[OK] VERIFICATION COMPLETE")
        print(f"{'='*70}\n")
        
        return report


if __name__ == "__main__":
    project_root = Path(__file__).parent
    verifier = SetupVerifier(project_root)
    report = verifier.run_complete_verification()
