#!/usr/bin/env python3
"""Comprehensive PoultryGuard AI diagnostic check"""

import requests
import json
import sys
import os
from datetime import datetime

# Fix encoding on Windows
if sys.platform == 'win32':
    os.chdir(os.path.dirname(__file__))

BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

class DiagnosticsReport:
    def __init__(self):
        self.checks = []
        self.passed = 0
        self.failed = 0
    
    def add_check(self, name, status, message=""):
        icon = "[PASS]" if status else "[FAIL]"
        self.checks.append({
            "name": name,
            "status": status,
            "message": message
        })
        if status:
            self.passed += 1
        else:
            self.failed += 1
        try:
            print(f"{icon} {name}: {message}")
        except UnicodeEncodeError:
            print(f"[OK] {name}: {message}" if status else f"[ERROR] {name}")
    
    def print_summary(self):
        print("\n" + "="*60)
        print(f"DIAGNOSTICS SUMMARY - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        print(f"PASSED: {self.passed}")
        print(f"FAILED: {self.failed}")
        print(f"Total: {self.passed + self.failed}")
        print("="*60 + "\n")

report = DiagnosticsReport()

# Test 1: Backend health
try:
    response = requests.get(f"{BASE_URL}/api/health", timeout=3)
    report.add_check("Backend Health", response.status_code == 200, f"Status: {response.status_code}")
except Exception as e:
    report.add_check("Backend Health", False, str(e))

# Test 2: Frontend accessibility
try:
    response = requests.get(FRONTEND_URL, timeout=3)
    report.add_check("Frontend Running", response.status_code == 200, f"Status: {response.status_code}")
except Exception as e:
    report.add_check("Frontend Running", False, str(e))

# Test 3: Auth endpoints
try:
    response = requests.post(f"{BASE_URL}/api/auth/register", json={
        "email": f"test_{datetime.now().timestamp()}@example.com",
        "password": "testpass123",
        "full_name": "Test User"
    }, timeout=3)
    # 409 is conflict (user exists), which is fine - endpoint is working
    ok = response.status_code in [200, 201, 409, 422]
    report.add_check("Auth Register Endpoint", ok, f"Status: {response.status_code}")
except Exception as e:
    report.add_check("Auth Register Endpoint", False, str(e))

# Test 4: Database
try:
    from app.db.session import SessionLocal
    from sqlalchemy import text
    db = SessionLocal()
    db.execute(text("SELECT 1"))
    db.close()
    report.add_check("Database Connection", True, "SQLite OK")
except Exception as e:
    report.add_check("Database Connection", False, str(e))

# Test 5: Main routes exist
routes_to_check = [
    ("/api/farms", "Farms"),
    ("/api/records", "Records"),
    ("/api/predictions/reference-status", "Predictions"),
    ("/api/alerts", "Alerts"),
    ("/api/dashboard", "Dashboard"),
    ("/api/history", "History"),
]

print("\nChecking API Routes (will return 401 without auth - expected):")
for route, name in routes_to_check:
    try:
        response = requests.get(f"{BASE_URL}{route}", timeout=3)
        # 401 = Unauthorized (auth required), 404 = route doesn't exist
        ok = response.status_code != 404
        report.add_check(f"Route {name}", ok, f"Status: {response.status_code}")
    except Exception as e:
        report.add_check(f"Route {name}", False, str(e))

# Test 6: CSS/Assets
print("\nChecking Frontend Assets:")
try:
    response = requests.get(f"{FRONTEND_URL}/_next/static", timeout=3)
    report.add_check("Frontend Assets", response.status_code < 500, f"Status: {response.status_code}")
except Exception as e:
    report.add_check("Frontend Assets", False, str(e))

# Test 7: Check for common issues
print("\nChecking Common Issues:")

# Check if uploads folder exists
import os
if os.path.exists("uploads"):
    report.add_check("Uploads Folder", True, "Exists and accessible")
else:
    report.add_check("Uploads Folder", False, "Missing")

# Check database file exists
if os.path.exists("poultryguard.db"):
    report.add_check("Database File", True, "poultryguard.db exists")
else:
    report.add_check("Database File", False, "poultryguard.db missing")

report.print_summary()

# Exit with code based on results
sys.exit(0 if report.failed == 0 else 1)
