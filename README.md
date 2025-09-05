# Telegram Landing Page Generator Bot

A Telegram bot that generates responsive landing pages using Google's Gemini AI and automatically pushes them to GitHub for deployment.

## Features

- 🤖 **Telegram Bot Interface**: Easy-to-use commands and natural language processing
- 🎨 **AI-Powered Generation**: Uses Google Gemini AI to create beautiful, responsive landing pages
- 📱 **Responsive Design**: All pages are built with Tailwind CSS for mobile-first design
- ⚡ **Auto-Deployment**: Automatically pushes generated pages to GitHub branches
- 🔧 **Git Integration**: Full Git workflow with branch management
- 🛠️ **Easy Setup**: Automated setup script and configuration validation
- 📊 **Smart Branch Management**: Sanitized branch names and conflict resolution
- 🎯 **Enhanced UX**: Rich messages with emojis and detailed feedback
- 🔒 **Secure Configuration**: Environment variable management with validation

## Prerequisites

Before setting up the bot, you'll need:

1. **Telegram Bot Token**: Get one from [@BotFather](https://t.me/botfather)
2. **Google Gemini API Key**: Get one from [Google AI Studio](https://aistudio.google.com/)
3. **GitHub Personal Access Token**: Create one in your GitHub settings
4. **GitHub Repository**: A repository to store the generated landing pages
5. **Python 3.8+**: Make sure Python is installed on your system

## Installation

1. **Clone or download this repository**
   ```bash
   git clone <your-repo-url>
   cd telegram-landing-page-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   - Copy `env.example` to `.env`
   - Fill in your actual API keys and configuration:
   ```bash
   cp env.example .env
   ```

4. **Configure your `.env` file**
   ```env
   TELEGRAM_BOT_TOKEN=your_actual_bot_token
   GEMINI_API_KEY=your_actual_gemini_key
   GITHUB_PAT=your_actual_github_token
   GITHUB_REPO_URL=https://github.com/yourusername/your-repo.git
   ```

## Configuration

### 1. Telegram Bot Setup
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Use `/newbot` command to create a new bot
3. Follow the instructions to get your bot token
4. Add the token to your `.env` file

### 2. Google Gemini API Setup
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create a new API key
3. Add the key to your `.env` file

### 3. GitHub Setup
1. Create a new repository on GitHub for your landing pages
2. Go to GitHub Settings → Developer settings → Personal access tokens
3. Generate a new token with `repo` permissions
4. Add the token and repository URL to your `.env` file

## Usage

1. **Start the bot**
   ```bash
   python bot.py
   ```

2. **Use the bot on Telegram**
   - Send `/start` to see the main menu
   - Click "Create Landing Page" button
   - Follow the step-by-step process:
     • Enter your channel name
     • Upload your logo image
     • Select page type from buttons
     • Choose footer option
   - The bot will generate and deploy your page

## Bot Interface

- **Button-based Interface** - All interactions use inline keyboard buttons
- **Step-by-step Process** - Guided workflow for creating landing pages
- **No Text Commands** - Everything is done through buttons and simple text inputs

## Generated Landing Pages

Each generated landing page includes:
- **Responsive Header**: Logo, title, and tagline
- **Call-to-Action Section**: Button with 15-second countdown timer
- **Main Content**: Heading and descriptive paragraphs
- **Footer**: Credit link
- **Modern Design**: Dark background with vibrant colors and animations

## File Structure

```
telegram-landing-page-bot/
├── bot.py              # Main bot application
├── requirements.txt    # Python dependencies
├── env.example        # Environment variables template
├── setup.py           # Automated setup script
├── test_setup.py      # Setup verification script
├── DEPLOYMENT.md      # Deployment guide
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## Quick Start

1. **Run the setup script**
   ```bash
   python setup.py
   ```

2. **Configure your API keys**
   - Edit the `.env` file with your actual keys

3. **Test the setup**
   ```bash
   python test_setup.py
   ```

4. **Run the bot**
   ```bash
   python bot.py
   ```

## Troubleshooting

### Common Issues

1. **"GitHub Personal Access Token is not configured"**
   - Make sure you've set the `GITHUB_PAT` environment variable
   - Verify the token has `repo` permissions

2. **"Could not set up the Git repository"**
   - Check your GitHub repository URL
   - Verify your GitHub token is valid
   - Ensure the repository exists and is accessible

3. **"Error calling Gemini API"**
   - Verify your Gemini API key is correct
   - Check your internet connection
   - Ensure you have API quota remaining

### Logs

The bot will print detailed logs to the console. Check these for debugging information.

## Security Notes

- Never commit your `.env` file to version control
- Keep your API keys secure and private
- Use environment variables for all sensitive configuration
- Regularly rotate your API keys

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the [MIT License](LICENSE).
