#!/usr/bin/env python3
"""
Test script to verify the bot setup
"""

import os
import sys
from dotenv import load_dotenv

def test_environment_variables():
    """Test if all required environment variables are set."""
    load_dotenv()
    
    required_vars = [
        "TELEGRAM_BOT_TOKEN",
        "GEMINI_API_KEY", 
        "GITHUB_REPO_URL",
        "GITHUB_PAT"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var) or os.getenv(var) == f"your_{var.lower()}_here":
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing or not configured environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    
    print("✅ All environment variables are configured")
    return True

def test_imports():
    """Test if all required modules can be imported."""
    try:
        import requests
        import telegram
        from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
        import subprocess
        from dotenv import load_dotenv
        print("✅ All required modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def test_git():
    """Test if Git is working."""
    try:
        import subprocess
        result = subprocess.run(["git", "--version"], capture_output=True, text=True, check=True)
        print(f"✅ Git is working: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"❌ Git test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing bot setup...\n")
    
    tests = [
        ("Import Test", test_imports),
        ("Git Test", test_git),
        ("Environment Variables Test", test_environment_variables)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        if test_func():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your bot is ready to run.")
        print("Run: python bot.py")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
