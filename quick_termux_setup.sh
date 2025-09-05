#!/bin/bash

# Quick Termux Setup - One command setup
# Copy and paste this entire script into Termux

echo "🚀 Quick Termux Setup for Telegram Bot"
echo "======================================"

# Update and install packages
pkg update && pkg upgrade -y
pkg install python git curl wget libjpeg-turbo libpng freetype -y
pip install --upgrade pip

# Clone and setup bot
cd ~
git clone https://github.com/sixtyfourbitsquad/Gemini-TG-BOT.git
cd Gemini-TG-BOT
pip install -r requirements.txt
cp env.example .env
chmod +x *.py

echo ""
echo "✅ Setup Complete!"
echo ""
echo "📝 Now edit your .env file:"
echo "   nano .env"
echo ""
echo "🔑 Add your API keys:"
echo "   - TELEGRAM_BOT_TOKEN (from @BotFather)"
echo "   - GEMINI_API_KEY (from Google AI Studio)"
echo "   - GITHUB_PAT (from GitHub Settings)"
echo "   - GITHUB_REPO_URL (your repository URL)"
echo ""
echo "🧪 Test setup:"
echo "   python test_setup.py"
echo ""
echo "🚀 Run bot:"
echo "   python bot.py"
echo ""
echo "📚 Full guide: cat TERMUX_SETUP.md"
