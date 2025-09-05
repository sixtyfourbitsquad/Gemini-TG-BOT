#!/bin/bash

# Termux Setup Script for Telegram Landing Page Bot
# Run this script in Termux to automatically set up the bot

echo "🚀 Setting up Telegram Landing Page Bot on Termux..."
echo ""

# Update packages
echo "📦 Updating Termux packages..."
pkg update && pkg upgrade -y

# Install required packages
echo "📦 Installing required packages..."
pkg install python git curl wget libjpeg-turbo libpng freetype -y

# Install Python package manager
echo "📦 Installing pip..."
pip install --upgrade pip

# Clone repository
echo "📥 Cloning repository..."
cd ~
if [ -d "Gemini-TG-BOT" ]; then
    echo "Repository already exists. Updating..."
    cd Gemini-TG-BOT
    git pull origin master
else
    git clone https://github.com/sixtyfourbitsquad/Gemini-TG-BOT.git
    cd Gemini-TG-BOT
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your API keys:"
    echo "   nano .env"
    echo ""
fi

# Make scripts executable
chmod +x setup.py test_setup.py

echo "✅ Setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your API keys:"
echo "   nano .env"
echo ""
echo "2. Test the setup:"
echo "   python test_setup.py"
echo ""
echo "3. Run the bot:"
echo "   python bot.py"
echo ""
echo "📚 For detailed instructions, see TERMUX_SETUP.md"
echo ""
echo "🎉 Happy botting!"
