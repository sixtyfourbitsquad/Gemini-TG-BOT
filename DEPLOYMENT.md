# Deployment Guide

This guide will help you deploy your Telegram Landing Page Generator Bot to various platforms.

## Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd telegram-landing-page-bot
   ```

2. **Run setup**
   ```bash
   python setup.py
   ```

3. **Configure environment variables**
   - Edit `.env` file with your API keys
   - See `env.example` for reference

4. **Test the setup**
   ```bash
   python test_setup.py
   ```

5. **Run the bot**
   ```bash
   python bot.py
   ```

## Cloud Deployment Options

### 1. Heroku

1. **Install Heroku CLI**
   - Download from [heroku.com](https://devcenter.heroku.com/articles/heroku-cli)

2. **Create Heroku app**
   ```bash
   heroku create your-bot-name
   ```

3. **Set environment variables**
   ```bash
   heroku config:set TELEGRAM_BOT_TOKEN=your_token
   heroku config:set GEMINI_API_KEY=your_key
   heroku config:set GITHUB_PAT=your_pat
   heroku config:set GITHUB_REPO_URL=your_repo_url
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

5. **Scale the bot**
   ```bash
   heroku ps:scale worker=1
   ```

### 2. Railway

1. **Connect your GitHub repository**
   - Go to [railway.app](https://railway.app)
   - Connect your GitHub account
   - Select your repository

2. **Set environment variables**
   - In Railway dashboard, go to Variables tab
   - Add all required environment variables

3. **Deploy**
   - Railway will automatically deploy when you push to main branch

### 3. DigitalOcean App Platform

1. **Create a new app**
   - Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
   - Create new app from GitHub

2. **Configure the app**
   - Select your repository
   - Choose Python as the runtime
   - Set the run command: `python bot.py`

3. **Set environment variables**
   - Add all required environment variables in the app settings

4. **Deploy**
   - Click "Create Resources" to deploy

### 4. VPS Deployment (Ubuntu/Debian)

1. **Set up the server**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip git
   ```

2. **Clone and setup**
   ```bash
   git clone <your-repo-url>
   cd telegram-landing-page-bot
   pip3 install -r requirements.txt
   ```

3. **Create systemd service**
   ```bash
   sudo nano /etc/systemd/system/telegram-bot.service
   ```

4. **Service file content**
   ```ini
   [Unit]
   Description=Telegram Landing Page Bot
   After=network.target

   [Service]
   Type=simple
   User=your-username
   WorkingDirectory=/path/to/telegram-landing-page-bot
   Environment=PATH=/usr/bin:/usr/local/bin
   ExecStart=/usr/bin/python3 bot.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

5. **Enable and start service**
   ```bash
   sudo systemctl enable telegram-bot
   sudo systemctl start telegram-bot
   sudo systemctl status telegram-bot
   ```

## Environment Variables

Make sure to set these environment variables in your deployment platform:

| Variable | Description | Example |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather | `123456789:ABCdefGHIjklMNOpqrsTUVwxyz` |
| `GEMINI_API_KEY` | Google Gemini API key | `AIzaSyB...` |
| `GITHUB_PAT` | GitHub Personal Access Token | `ghp_...` |
| `GITHUB_REPO_URL` | Your GitHub repository URL | `https://github.com/user/repo.git` |
| `REPO_DIR` | Local directory for Git repo (optional) | `landing_pages_repo` |

## Monitoring and Logs

### Heroku
```bash
heroku logs --tail
```

### Railway
- View logs in the Railway dashboard

### DigitalOcean
- View logs in the App Platform dashboard

### VPS
```bash
sudo journalctl -u telegram-bot -f
```

## Troubleshooting

### Common Issues

1. **Bot not responding**
   - Check if the bot is running
   - Verify the bot token is correct
   - Check logs for errors

2. **GitHub integration not working**
   - Verify GitHub PAT has correct permissions
   - Check repository URL is correct
   - Ensure repository exists and is accessible

3. **Gemini API errors**
   - Verify API key is correct
   - Check API quota limits
   - Ensure internet connectivity

4. **Memory issues**
   - Consider upgrading your hosting plan
   - Monitor memory usage
   - Restart the bot if needed

### Health Checks

You can add a simple health check endpoint to monitor your bot:

```python
# Add this to your bot.py
from flask import Flask

app = Flask(__name__)

@app.route('/health')
def health():
    return {'status': 'ok', 'bot': 'running'}

# Run Flask in a separate thread
import threading
threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000), daemon=True).start()
```

## Security Best Practices

1. **Never commit sensitive data**
   - Use environment variables for all secrets
   - Keep `.env` file in `.gitignore`

2. **Regular updates**
   - Keep dependencies updated
   - Monitor for security vulnerabilities

3. **Access control**
   - Limit GitHub PAT permissions
   - Use least privilege principle

4. **Monitoring**
   - Set up alerts for bot downtime
   - Monitor API usage and costs

## Scaling

For high-traffic bots:

1. **Use a database**
   - Store user data and page history
   - Consider PostgreSQL or MongoDB

2. **Queue system**
   - Use Redis or RabbitMQ for job queuing
   - Handle multiple requests concurrently

3. **Load balancing**
   - Deploy multiple bot instances
   - Use a load balancer

4. **Caching**
   - Cache frequently generated pages
   - Use Redis for caching

## Support

If you encounter issues:

1. Check the logs first
2. Verify all environment variables
3. Test locally before deploying
4. Check API quotas and limits
5. Review the troubleshooting section above
