#!/usr/bin/env python3
"""
PoultryGuardAI - Comprehensive System Verification Script
Tests all components: Backend, Frontend, Database, AI Models
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

class VerificationReport:
    def __init__(self):
        self.results = {}
        self.status = "PASS"
        self.timestamp = datetime.now().isoformat()
    
    def add_check(self, category, name, passed, details=""):
        if category not in self.results:
            self.results[category] = []
        
        self.results[category].append({
            "name": name,
            "status": "✓ PASS" if passed else "✗ FAIL",
            "details": details
        })
        
        if not passed:
            self.status = "FAIL"
    
    def print_report(self):
        print("\n" + "=" * 80)
        print("POULTRYGUARDAI - SYSTEM VERIFICATION REPORT".center(80))
        print("=" * 80)
        print(f"Generated: {self.timestamp}")
        print(f"Status: {self.status}")
        print("=" * 80 + "\n")
        
        for category, checks in self.results.items():
            print(f"\n📋 {category.upper()}")
            print("-" * 80)
            for check in checks:
                symbol = "✓" if check["status"].startswith("✓") else "✗"
                print(f"  {symbol} {check['name']:<40} {check['status']:<10}")
                if check["details"]:
                    print(f"    → {check['details']}")
        
        print("\n" + "=" * 80)
        print(f"OVERALL STATUS: {self.status}")
        print("=" * 80 + "\n")

def verify_backend():
    """Verify backend components"""
    report = VerificationReport()
    
    print("\n🔍 Verifying Backend Components...")
    
    # Check FastAPI
    try:
        import fastapi
        report.add_check("Backend", "FastAPI Installation", True, f"v{fastapi.__version__}")
    except ImportError as e:
        report.add_check("Backend", "FastAPI Installation", False, str(e))
    
    # Check SQLAlchemy
    try:
        import sqlalchemy
        report.add_check("Backend", "SQLAlchemy Installation", True, f"v{sqlalchemy.__version__}")
    except ImportError as e:
        report.add_check("Backend", "SQLAlchemy Installation", False, str(e))
    
    # Check TensorFlow
    try:
        import tensorflow
        report.add_check("Backend", "TensorFlow Installation", True, f"v{tensorflow.__version__}")
    except ImportError as e:
        report.add_check("Backend", "TensorFlow Installation", False, str(e))
    
    # Check main.py
    main_file = Path("Backend/app/main.py")
    report.add_check("Backend", "main.py exists", main_file.exists(), 
                     f"Size: {main_file.stat().st_size} bytes" if main_file.exists() else "")
    
    # Check database file
    db_file = Path("Backend/poultryguard.db")
    report.add_check("Backend", "Database file exists", db_file.exists(),
                     f"Size: {db_file.stat().st_size} bytes" if db_file.exists() else "")
    
    # Check configuration
    config_file = Path("Backend/app/core/config.py")
    report.add_check("Backend", "Configuration file", config_file.exists())
    
    # Check API routes
    routes_dir = Path("Backend/app/api/routes")
    route_files = list(routes_dir.glob("*.py")) if routes_dir.exists() else []
    report.add_check("Backend", "API Routes", len(route_files) > 0, 
                     f"Found {len(route_files)} route modules")
    
    return report

def verify_frontend():
    """Verify frontend components"""
    report = VerificationReport()
    
    print("\n🔍 Verifying Frontend Components...")
    
    # Check package.json
    pkg_file = Path("Frontend/package.json")
    report.add_check("Frontend", "package.json exists", pkg_file.exists())
    
    # Check Next.js config
    next_config = Path("Frontend/next.config.ts")
    report.add_check("Frontend", "next.config.ts exists", next_config.exists())
    
    # Check tsconfig
    ts_config = Path("Frontend/tsconfig.json")
    report.add_check("Frontend", "tsconfig.json exists", ts_config.exists())
    
    # Check app directory
    app_dir = Path("Frontend/src/app")
    app_files = list(app_dir.glob("*.tsx")) if app_dir.exists() else []
    report.add_check("Frontend", "App pages", len(app_files) > 0,
                     f"Found {len(app_files)} page files")
    
    # Check components
    components_dir = Path("Frontend/src/components")
    components = list(components_dir.glob("*.tsx")) if components_dir.exists() else []
    report.add_check("Frontend", "Components", len(components) > 0,
                     f"Found {len(components)} component files")
    
    return report

def verify_ai_models():
    """Verify AI model components"""
    report = VerificationReport()
    
    print("\n🔍 Verifying AI Model Components...")
    
    # Check models directory
    models_dir = Path("AI/models")
    model_files = list(models_dir.glob("*")) if models_dir.exists() else []
    report.add_check("AI Models", "Trained models exist", len(model_files) > 0,
                     f"Found {len(model_files)} model files" if model_files else "Empty - needs training")
    
    # Check training scripts
    train_cnn = Path("AI/training/train_cnn.py")
    report.add_check("AI Models", "CNN training script", train_cnn.exists())
    
    train_risk = Path("AI/training/train_risk_model.py")
    report.add_check("AI Models", "Risk model training script", train_risk.exists())
    
    # Check sample data
    sample_data_dir = Path("AI/sample_data")
    sample_dirs = [d for d in sample_data_dir.iterdir() if d.is_dir()] if sample_data_dir.exists() else []
    report.add_check("AI Models", "Sample data directories", len(sample_dirs) > 0,
                     f"Found {len(sample_dirs)} disease directories")
    
    # Check scikit-learn for risk model
    try:
        import sklearn
        report.add_check("AI Models", "scikit-learn Installation", True, f"v{sklearn.__version__}")
    except ImportError as e:
        report.add_check("AI Models", "scikit-learn Installation", False, str(e))
    
    return report

def verify_database():
    """Verify database components"""
    report = VerificationReport()
    
    print("\n🔍 Verifying Database Components...")
    
    # Check database models
    models_dir = Path("Backend/app/models")
    model_files = list(models_dir.glob("*.py")) if models_dir.exists() else []
    report.add_check("Database", "SQLAlchemy models", len(model_files) > 0,
                     f"Found {len(model_files)} model files")
    
    # Check migrations
    migrations_dir = Path("Database/migrations")
    migration_files = list(migrations_dir.glob("*")) if migrations_dir.exists() else []
    report.add_check("Database", "Migrations", migrations_dir.exists(),
                     f"Found {len(migration_files)} migration files")
    
    # Check init script
    init_script = Path("Backend/init_db.py")
    report.add_check("Database", "Database init script", init_script.exists())
    
    # Check schemas
    schemas_dir = Path("Backend/app/schemas")
    schema_files = list(schemas_dir.glob("*.py")) if schemas_dir.exists() else []
    report.add_check("Database", "Pydantic schemas", len(schema_files) > 0,
                     f"Found {len(schema_files)} schema files")
    
    return report

def verify_configuration():
    """Verify configuration files"""
    report = VerificationReport()
    
    print("\n🔍 Verifying Configuration Files...")
    
    # Check .env file
    env_file = Path(".env")
    report.add_check("Configuration", ".env file exists", env_file.exists())
    
    # Check disease config
    disease_config = Path("disease_config.json")
    report.add_check("Configuration", "disease_config.json", disease_config.exists())
    
    # Check .gitignore files
    backend_gitignore = Path("Backend/.gitignore")
    report.add_check("Configuration", "Backend .gitignore", backend_gitignore.exists())
    
    frontend_gitignore = Path("Frontend/.gitignore")
    report.add_check("Configuration", "Frontend .gitignore", frontend_gitignore.exists())
    
    return report

def verify_documentation():
    """Verify documentation files"""
    report = VerificationReport()
    
    print("\n🔍 Verifying Documentation...")
    
    # Check README
    readme = Path("README.md")
    report.add_check("Documentation", "README.md", readme.exists(),
                     f"Size: {readme.stat().st_size} bytes" if readme.exists() else "")
    
    # Check documentation folder
    docs_dir = Path("documentation")
    doc_files = list(docs_dir.glob("*.md")) if docs_dir.exists() else []
    report.add_check("Documentation", "Documentation files", len(doc_files) > 0,
                     f"Found {len(doc_files)} documentation files")
    
    return report

def main():
    """Run all verifications"""
    os.chdir(Path(__file__).parent)
    
    all_reports = []
    
    # Run all verifications
    all_reports.append(verify_backend())
    all_reports.append(verify_frontend())
    all_reports.append(verify_ai_models())
    all_reports.append(verify_database())
    all_reports.append(verify_configuration())
    all_reports.append(verify_documentation())
    
    # Print combined report
    combined_status = "FAIL" if any(r.status == "FAIL" for r in all_reports) else "PASS"
    
    print("\n" + "=" * 80)
    print("POULTRYGUARDAI - COMPLETE SYSTEM VERIFICATION REPORT".center(80))
    print("=" * 80)
    print(f"Generated: {datetime.now().isoformat()}")
    print(f"Overall Status: {combined_status}")
    print("=" * 80)
    
    for report in all_reports:
        for category, checks in report.results.items():
            print(f"\n{category.upper()}")
            print("-" * 80)
            for check in checks:
                status_icon = "✓" if check["status"].startswith("✓") else "✗"
                print(f"  {status_icon} {check['name']:<40} {check['status']:<10}")
                if check["details"]:
                    print(f"    → {check['details']}")
    
    print("\n" + "=" * 80)
    print(f"FINAL STATUS: {combined_status}")
    print("=" * 80)
    
    if combined_status == "PASS":
        print("\n✅ All checks passed! Your PoultryGuardAI system is ready.")
        print("\nNext steps:")
        print("  1. Initialize database: python Backend/init_db.py")
        print("  2. Train AI models: python AI/training/train_cnn.py")
        print("  3. Start backend: python -m uvicorn Backend.app.main:app --reload")
        print("  4. Start frontend: npm run dev (from Frontend directory)")
    else:
        print("\n⚠️  Some checks failed. Please review the errors above.")
    
    return 0 if combined_status == "PASS" else 1

if __name__ == "__main__":
    sys.exit(main())
