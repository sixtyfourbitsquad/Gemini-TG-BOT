#!/usr/bin/env python3
"""
Setup script for the Telegram Landing Page Generator Bot
"""

import os
import subprocess
import sys

def check_python_version():
    """Check if Python version is 3.8 or higher."""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_git():
    """Check if Git is installed."""
    try:
        result = subprocess.run(["git", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Git found: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ Error: Git is not installed or not in PATH.")
    print("Please install Git from https://git-scm.com/")
    return False

def install_dependencies():
    """Install required Python packages."""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def create_env_file():
    """Create .env file from template if it doesn't exist."""
    if os.path.exists(".env"):
        print("✅ .env file already exists")
        return True
    
    if os.path.exists("env.example"):
        try:
            with open("env.example", "r") as src, open(".env", "w") as dst:
                dst.write(src.read())
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env file with your actual API keys")
            return True
        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
            return False
    else:
        print("❌ Error: env.example file not found")
        return False

def main():
    """Main setup function."""
    print("🚀 Setting up Telegram Landing Page Generator Bot...\n")
    
    # Check requirements
    if not check_python_version():
        return False
    
    if not check_git():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Create .env file
    if not create_env_file():
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit the .env file with your actual API keys:")
    print("   - TELEGRAM_BOT_TOKEN (from @BotFather)")
    print("   - GEMINI_API_KEY (from Google AI Studio)")
    print("   - GITHUB_PAT (from GitHub Settings)")
    print("   - GITHUB_REPO_URL (your repository URL)")
    print("\n2. Run the bot:")
    print("   python bot.py")
    print("\n3. Start chatting with your bot on Telegram!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
