# Termux Setup Guide for Telegram Landing Page Bot

This guide will help you set up the Telegram Landing Page Generator Bot on Termux (Android).

## Prerequisites

1. **Android device** with Termux installed
2. **Internet connection**
3. **API keys** (Telegram Bot Token, Gemini API Key, GitHub PAT)

## Step 1: Install Termux

1. Download Termux from [F-Droid](https://f-droid.org/en/packages/com.termux/) (recommended) or [Google Play Store](https://play.google.com/store/apps/details?id=com.termux)
2. Open Termux app

## Step 2: Update Termux

```bash
pkg update && pkg upgrade
```

## Step 3: Install Required Packages

```bash
# Install Python and essential tools
pkg install python git curl wget

# Install Python package manager
pip install --upgrade pip

# Install additional dependencies for image processing
pkg install libjpeg-turbo libpng
```

## Step 4: Clone the Repository

```bash
# Navigate to home directory
cd ~

# Clone the bot repository
git clone https://github.com/sixtyfourbitsquad/Gemini-TG-BOT.git

# Navigate to the bot directory
cd Gemini-TG-BOT
```

## Step 5: Install Python Dependencies

```bash
# Install required Python packages
pip install -r requirements.txt

# If you encounter issues with Pillow, try:
pip install --upgrade Pillow
```

## Step 6: Set Up Environment Variables

```bash
# Copy the example environment file
cp env.example .env

# Edit the .env file with your API keys
nano .env
```

### Required Environment Variables:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# GitHub Configuration
GITHUB_PAT=your_github_personal_access_token_here
GITHUB_REPO_URL=https://github.com/yourusername/your-repo-name.git

# Netlify Configuration (optional)
NETLIFY_API_TOKEN=your_netlify_api_token_here
NETLIFY_SITE_ID=your_netlify_site_id_here

# Repository Directory (optional)
REPO_DIR=landing_pages_repo
```

## Step 7: Test the Setup

```bash
# Run the setup test
python test_setup.py
```

## Step 8: Run the Bot

```bash
# Start the bot
python bot.py
```

## Step 9: Keep Bot Running (Optional)

To keep the bot running in the background on Termux:

### Method 1: Using nohup
```bash
# Run bot in background
nohup python bot.py > bot.log 2>&1 &

# Check if bot is running
ps aux | grep python

# View logs
tail -f bot.log

# Stop the bot
pkill -f "python bot.py"
```

### Method 2: Using screen (if available)
```bash
# Install screen
pkg install screen

# Start a new screen session
screen -S bot

# Run the bot
python bot.py

# Detach from screen (Ctrl+A, then D)
# Reattach to screen
screen -r bot
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Python Package Installation Issues
```bash
# If pip install fails, try:
pip install --user -r requirements.txt

# Or use conda if available
pkg install python-cryptography
pip install --upgrade setuptools wheel
```

#### 2. Image Processing Issues
```bash
# Install additional image libraries
pkg install libjpeg-turbo libpng freetype

# Reinstall Pillow
pip uninstall Pillow
pip install Pillow
```

#### 3. Git Issues
```bash
# Configure Git
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

#### 4. Permission Issues
```bash
# Make sure you have write permissions
chmod +x bot.py
chmod +x setup.py
chmod +x test_setup.py
```

#### 5. Network Issues
```bash
# Test internet connection
ping google.com

# Check if ports are accessible
curl -I https://api.telegram.org
```

### Memory and Performance

#### Check System Resources
```bash
# Check memory usage
free -h

# Check disk space
df -h

# Check running processes
ps aux
```

#### Optimize for Mobile
```bash
# Reduce memory usage by limiting concurrent operations
export PYTHONUNBUFFERED=1

# Run with reduced memory footprint
python -O bot.py
```

## Security Considerations

1. **Never share your .env file** - it contains sensitive API keys
2. **Use strong passwords** for your API accounts
3. **Regularly update** your API keys
4. **Monitor usage** to avoid exceeding API limits

## Getting API Keys

### 1. Telegram Bot Token
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot`
3. Follow instructions to create your bot
4. Copy the token

### 2. Google Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Click "Get API Key"
3. Create a new API key
4. Copy the key

### 3. GitHub Personal Access Token
1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Click "Generate new token (classic)"
3. Select `repo` permissions
4. Copy the token

### 4. Netlify (Optional)
1. Go to [Netlify](https://netlify.com) and sign up
2. Create a new site from your GitHub repository
3. Get API token from User settings → Applications
4. Get Site ID from Site settings → General

## Running Multiple Bots

If you want to run multiple instances:

```bash
# Create separate directories
mkdir bot1 bot2

# Copy files to each directory
cp -r Gemini-TG-BOT/* bot1/
cp -r Gemini-TG-BOT/* bot2/

# Use different .env files for each
# Edit bot1/.env and bot2/.env with different tokens
```

## Backup and Updates

### Backup Your Configuration
```bash
# Create a backup of your .env file
cp .env .env.backup

# Backup the entire bot directory
tar -czf bot_backup.tar.gz Gemini-TG-BOT/
```

### Update the Bot
```bash
# Navigate to bot directory
cd ~/Gemini-TG-BOT

# Pull latest changes
git pull origin master

# Update dependencies
pip install -r requirements.txt --upgrade
```

## Monitoring and Logs

### View Bot Logs
```bash
# If running with nohup
tail -f bot.log

# If running normally, logs appear in terminal
```

### Check Bot Status
```bash
# Check if bot process is running
ps aux | grep python

# Check network connections
netstat -tulpn | grep python
```

## Performance Tips

1. **Close unnecessary apps** to free up memory
2. **Use WiFi** instead of mobile data for better stability
3. **Keep Termux updated** for latest features and security
4. **Monitor battery usage** - the bot will use some battery
5. **Use a stable internet connection** to avoid disconnections

## Support

If you encounter issues:

1. Check the logs for error messages
2. Verify all API keys are correct
3. Ensure internet connection is stable
4. Try restarting the bot
5. Check if all dependencies are installed correctly

## Quick Start Commands

```bash
# Complete setup in one go
cd ~
git clone https://github.com/sixtyfourbitsquad/Gemini-TG-BOT.git
cd Gemini-TG-BOT
pip install -r requirements.txt
cp env.example .env
nano .env  # Edit with your API keys
python test_setup.py
python bot.py
```

Your bot should now be running on Termux! 🎉
