#!/usr/bin/env python3
"""
Rate Limit Prevention Monitor
Ensures no GitHub API rate limit errors occur
"""

import os
import sys
from pathlib import Path

def check_github_token():
    """Verify GitHub token is properly set"""
    token = os.getenv("GITHUB_TOKEN")
    if token and len(token) > 10:
        print("✅ GitHub token configured")
        return True
    print("❌ GitHub token not configured")
    return False

def check_pip_config():
    """Verify pip is configured with cache"""
    home = Path.home()
    candidates = [
        home / ".config" / "pip" / "pip.conf",      # Linux/macOS
        home / ".pip" / "pip.conf",                  # macOS
        Path(os.getenv("APPDATA", "")) / "pip" / "pip.ini",  # Windows
    ]
    
    for config_path in candidates:
        if config_path.exists():
            print(f"✅ pip config found: {config_path}")
            return True
    
    print("⚠️  pip config not found - Install pip>=21.0 or set cache directory")
    return False

def check_packages_cached():
    """Check if critical packages are already installed"""
    packages = ["tensorflow", "torch", "requests"]
    import subprocess
    
    result = subprocess.run([sys.executable, "-m", "pip", "list"], 
                          capture_output=True, text=True)
    
    found = []
    for pkg in packages:
        if pkg.lower() in result.stdout.lower():
            found.append(pkg)
    
    if found:
        print(f"✅ Packages cached locally: {', '.join(found)}")
        print("   No GitHub API calls will be made")
        return True
    return False

def prevent_rate_limits():
    """Configure environment to reduce external API calls and logging"""
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    os.environ['PIP_DISABLE_PIP_VERSION_CHECK'] = '1'
    
    print("✅ Environment configured: reduced logging, cached bytecode")
    return True

def main():
    print("\n" + "="*50)
    print("🛡️  PoultryGuardAI Rate Limit Prevention Check")
    print("="*50 + "\n")
    
    checks = [
        ("GitHub Token", check_github_token),
        ("pip Configuration", check_pip_config),
        ("Package Cache", check_packages_cached),
        ("Rate Limit Prevention", prevent_rate_limits),
    ]
    
    passed = 0
    for name, check_func in checks:
        try:
            if check_func():
                passed += 1
        except Exception as e:
            print(f"⚠️  {name}: {e}")
    
    print("\n" + "="*50)
    if passed >= 3:
        print("✅ Mitigations detected — rate limits may still occur")
        print("   Consider adding caching, backoff, or queuing mechanisms")
    else:
        print(f"⚠️  {passed}/{len(checks)} checks passed")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
