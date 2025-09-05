import requests
import json
import asyncio
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler
import subprocess
from dotenv import load_dotenv
import re
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image

# Load environment variables from .env file
load_dotenv()

# --- Configuration from environment variables ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GITHUB_REPO_URL = os.getenv("GITHUB_REPO_URL")
GITHUB_PAT = os.getenv("GITHUB_PAT")
NETLIFY_API_TOKEN = os.getenv("NETLIFY_API_TOKEN")
NETLIFY_SITE_ID = os.getenv("NETLIFY_SITE_ID")
REPO_DIR = os.getenv("REPO_DIR", "landing_pages_repo")

# Validate required environment variables
if not all([TELEGRAM_BOT_TOKEN, GEMINI_API_KEY, GITHUB_REPO_URL, GITHUB_PAT]):
    print("Error: Missing required environment variables. Please check your .env file.")
    print("Required variables: TELEGRAM_BOT_TOKEN, GEMINI_API_KEY, GITHUB_REPO_URL, GITHUB_PAT")
    exit(1)

# Conversation states
CHANNEL_NAME, LOGO_IMAGE, PAGE_TYPE, FOOTER_CHOICE, FOOTER_TEXT = range(5)

# Button callbacks
CALLBACK_START = "start"
CALLBACK_GENERATE = "generate"
CALLBACK_HELP = "help"
CALLBACK_CANCEL = "cancel"
CALLBACK_FOOTER_YES = "footer_yes"
CALLBACK_FOOTER_NO = "footer_no"

# --- Gemini API Endpoint and Model ---
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={GEMINI_API_KEY}"

# --- Landing page types ---
LANDING_PAGE_TYPES = {
    "1": "Tech Startup - Modern, clean design with focus on innovation",
    "2": "E-commerce Store - Product showcase with shopping features",
    "3": "Personal Brand - Professional portfolio and about section",
    "4": "SaaS Product - Software service with features and pricing",
    "5": "Restaurant/Food - Culinary focus with menu highlights",
    "6": "Fitness/Health - Workout plans and health tips",
    "7": "Education/Course - Learning platform with course offerings",
    "8": "Non-profit - Cause-focused with donation features",
    "9": "Real Estate - Property listings and contact forms",
    "10": "Creative Agency - Portfolio showcase and services"
}

# --- System prompts for different page types ---
def get_system_prompt(page_type, channel_name, footer_text=None):
    base_prompt = f"""
You are a web page generator. Your task is to generate a complete, single-file HTML landing page for a channel called "{channel_name}".
The page must be fully responsive and styled with Tailwind CSS.
It must follow this specific structure:
1. A centered header with a logo (logo.png), title, and tagline.
2. A call-to-action section with a button and a 15-second countdown timer.
3. A main content section with a heading and two paragraphs.
4. A footer with a credit link.
The page should have a dark background and use vibrant, contrasting colors. The button must have a multi-color gradient and a subtle breathing animation. All text must be centered.
Do NOT include any external JavaScript or CSS files, put all code in a single file.
"""
    
    if footer_text:
        base_prompt += f"\nThe footer should include: 'Ads by {footer_text}'"
    
    # Add specific instructions based on page type
    type_instructions = {
        "1": "Focus on modern tech aesthetics, innovation, and cutting-edge design. Use tech-related colors like blues, purples, and cyans.",
        "2": "Emphasize product showcase, shopping experience, and e-commerce features. Use warm, inviting colors like oranges, reds, and golds.",
        "3": "Professional, clean design with personal branding. Use sophisticated colors like navy, gold, and whites.",
        "4": "Software-focused with features, pricing, and signup forms. Use professional blues, greens, and modern gradients.",
        "5": "Food-focused with appetizing visuals and warm colors. Use reds, oranges, and food-related imagery descriptions.",
        "6": "Energetic, motivational design with fitness themes. Use vibrant colors like greens, oranges, and energetic gradients.",
        "7": "Educational, trustworthy design with learning focus. Use academic colors like deep blues, purples, and scholarly tones.",
        "8": "Cause-focused, emotional design with donation features. Use meaningful colors like greens, blues, and compassionate tones.",
        "9": "Professional, trustworthy design for property listings. Use earth tones, blues, and professional gradients.",
        "10": "Creative, artistic design showcasing portfolio work. Use bold, creative colors and artistic gradients."
    }
    
    if page_type in type_instructions:
        base_prompt += f"\n{type_instructions[page_type]}"
    
    base_prompt += "\nRespond with ONLY the raw HTML code, no extra text or markdown."
    return base_prompt

# --- Function to call the Gemini API ---
async def generate_page_html(page_type, channel_name, footer_text=None):
    """Sends a request to the Gemini API to generate the HTML for a landing page."""
    headers = {
        'Content-Type': 'application/json'
    }
    
    system_prompt = get_system_prompt(page_type, channel_name, footer_text)
    user_prompt = f"Create a {LANDING_PAGE_TYPES.get(page_type, 'landing page')} for the channel '{channel_name}'"
    
    payload = {
        "contents": [{"parts": [{"text": user_prompt}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]}
    }
    
    try:
        response = requests.post(GEMINI_API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # This will raise an HTTPError if the response was an error
        
        result = response.json()
        generated_text = result['candidates'][0]['content']['parts'][0]['text']
        
        # Strip any extra markdown like ```html and ```
        if generated_text.startswith("```html") and generated_text.endswith("```"):
            generated_text = generated_text[7:-3].strip()
            
        return generated_text
    
    except requests.exceptions.RequestException as e:
        print(f"Error calling Gemini API: {e}")
        return None

# --- Git Integration Functions ---
def run_git_command(command, cwd=None):
    """A helper function to run Git commands and handle errors."""
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True, cwd=cwd)
        print(f"Git command success: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e.stderr}")
        return False

def setup_git_repo():
    """Clones the repository if it doesn't exist."""
    if not os.path.exists(REPO_DIR):
        print("Cloning repository...")
        # Use PAT for authentication in the URL
        authenticated_url = GITHUB_REPO_URL.replace("https://", f"https://oauth2:{GITHUB_PAT}@")
        return run_git_command(["git", "clone", authenticated_url, REPO_DIR])
    else:
        print("Repository already exists. Pulling latest changes.")
        return run_git_command(["git", "pull"], cwd=REPO_DIR)

def sanitize_branch_name(name):
    """Sanitize a string to be a valid Git branch name."""
    # Remove special characters and replace spaces with hyphens
    sanitized = re.sub(r'[^a-zA-Z0-9\-_]', '-', name.lower())
    # Remove multiple consecutive hyphens
    sanitized = re.sub(r'-+', '-', sanitized)
    # Remove leading/trailing hyphens
    sanitized = sanitized.strip('-')
    # Ensure it starts with a letter or number
    if not re.match(r'^[a-zA-Z0-9]', sanitized):
        sanitized = f"page-{sanitized}"
    return sanitized

def push_to_github(filename, branch_name, logo_path=None):
    """Adds, commits, and pushes a file to GitHub on a new branch."""
    # Sanitize the branch name
    branch_name = sanitize_branch_name(branch_name)
    
    # Check if branch already exists
    result = subprocess.run(["git", "branch", "-r"], cwd=REPO_DIR, capture_output=True, text=True)
    if f"origin/{branch_name}" in result.stdout:
        # Switch to existing branch
        if not run_git_command(["git", "checkout", branch_name], cwd=REPO_DIR):
            return False
    else:
        # Create and switch to a new branch
        if not run_git_command(["git", "checkout", "-b", branch_name], cwd=REPO_DIR):
            return False
    
    # Add the new file
    if not run_git_command(["git", "add", filename], cwd=REPO_DIR):
        return False
    
    # Add logo if provided
    if logo_path and os.path.exists(logo_path):
        if not run_git_command(["git", "add", "logo.png"], cwd=REPO_DIR):
            return False
        
    # Commit the changes
    commit_message = f"feat: add new landing page for {branch_name}"
    if not run_git_command(["git", "commit", "-m", commit_message], cwd=REPO_DIR):
        return False
        
    # Push the new branch to the remote repository
    if not run_git_command(["git", "push", "-u", "origin", branch_name], cwd=REPO_DIR):
        return False
        
    return True

def deploy_to_netlify(branch_name, channel_name):
    """Deploy the branch to Netlify and return the deployment URL."""
    if not NETLIFY_API_TOKEN or not NETLIFY_SITE_ID:
        print("Netlify credentials not configured, skipping deployment")
        return None
    
    # Sanitize channel name for subdomain
    subdomain = re.sub(r'[^a-zA-Z0-9\-]', '-', channel_name.lower())
    subdomain = re.sub(r'-+', '-', subdomain).strip('-')
    
    # Create subdomain
    subdomain_url = f"{subdomain}.netlify.app"
    
    try:
        # Trigger Netlify build
        headers = {
            'Authorization': f'Bearer {NETLIFY_API_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        # Get site info
        site_response = requests.get(f'https://api.netlify.com/api/v1/sites/{NETLIFY_SITE_ID}', headers=headers)
        if site_response.status_code != 200:
            print(f"Error getting site info: {site_response.text}")
            return None
        
        # Create a new deploy
        deploy_data = {
            "branch": branch_name,
            "title": f"Deploy {channel_name} landing page"
        }
        
        deploy_response = requests.post(
            f'https://api.netlify.com/api/v1/sites/{NETLIFY_SITE_ID}/deploys',
            headers=headers,
            json=deploy_data
        )
        
        if deploy_response.status_code == 201:
            deploy_info = deploy_response.json()
            return f"https://{subdomain_url}"
        else:
            print(f"Error creating deploy: {deploy_response.text}")
            return None
            
    except Exception as e:
        print(f"Error deploying to Netlify: {e}")
        return None

# --- Telegram Bot Command Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message and instructions."""
    welcome_text = """
🎉 Welcome to the Landing Page Generator Bot!

I can create beautiful, responsive landing pages for you using AI and automatically push them to GitHub.

🚀 **How to use:**
1. Click "Create Landing Page" to start
2. Follow the step-by-step process
3. I'll generate a beautiful page and push it to GitHub
4. You'll get a link to view and deploy your page

✨ **Features:**
• AI-powered page generation
• Responsive design with Tailwind CSS
• Automatic GitHub integration
• Modern animations and effects
• Step-by-step guided process

Ready to create your first landing page?
    """
    
    keyboard = [
        [InlineKeyboardButton("🎨 Create Landing Page", callback_data=CALLBACK_GENERATE)],
        [InlineKeyboardButton("❓ Help", callback_data=CALLBACK_HELP)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows detailed help information."""
    help_text = """
🔧 **Detailed Help**

**Creating a Landing Page:**
1. Click "Create Landing Page" button
2. Follow the step-by-step process:
   • Enter your channel name
   • Upload your logo image
   • Select page type (1-10)
   • Choose footer option

**Available Page Types:**
1. Tech Startup - Modern, clean design
2. E-commerce Store - Product showcase
3. Personal Brand - Professional portfolio
4. SaaS Product - Software service
5. Restaurant/Food - Culinary focus
6. Fitness/Health - Workout plans
7. Education/Course - Learning platform
8. Non-profit - Cause-focused
9. Real Estate - Property listings
10. Creative Agency - Portfolio showcase

**What You'll Get:**
• A fully responsive HTML page
• Modern design with dark theme and vibrant colors
• Call-to-action button with countdown timer
• Professional layout with header, content, and footer
• All code in a single HTML file
• Live URL: channel-name.netlify.app

**GitHub Integration:**
• Each page is pushed to a new branch
• You'll get a direct link to the GitHub repository
• Automatic deployment to Netlify

Need help? Just ask!
    """
    
    keyboard = [
        [InlineKeyboardButton("🎨 Create Landing Page", callback_data=CALLBACK_GENERATE)],
        [InlineKeyboardButton("🏠 Main Menu", callback_data=CALLBACK_START)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(help_text, reply_markup=reply_markup)

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the landing page creation process."""
    await update.message.reply_text(
        "🎨 Great! Let's create your landing page!\n\n"
        "First, what's the name of your channel? This will be used for the domain (channel-name.netlify.app)\n\n"
        "Please enter the channel name:"
    )
    return CHANNEL_NAME

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles button callbacks."""
    query = update.callback_query
    await query.answer()
    
    if query.data == CALLBACK_START:
        await start_from_callback(query, context)
    elif query.data == CALLBACK_GENERATE:
        await generate_from_callback(query, context)
    elif query.data == CALLBACK_HELP:
        await help_from_callback(query, context)
    elif query.data == CALLBACK_CANCEL:
        await cancel_from_callback(query, context)
    elif query.data == CALLBACK_FOOTER_YES:
        await footer_yes_callback(query, context)
    elif query.data == CALLBACK_FOOTER_NO:
        await footer_no_callback(query, context)
    elif query.data.startswith("page_type_"):
        page_type = query.data.replace("page_type_", "")
        await page_type_callback(query, context, page_type)

async def start_from_callback(query, context):
    """Handle start button callback."""
    welcome_text = """
🎉 Welcome to the Landing Page Generator Bot!

I can create beautiful, responsive landing pages for you using AI and automatically push them to GitHub.

🚀 **How to use:**
1. Click "Create Landing Page" to start
2. Follow the step-by-step process
3. I'll generate a beautiful page and push it to GitHub
4. You'll get a link to view and deploy your page

✨ **Features:**
• AI-powered page generation
• Responsive design with Tailwind CSS
• Automatic GitHub integration
• Modern animations and effects
• Step-by-step guided process

Ready to create your first landing page?
    """
    
    keyboard = [
        [InlineKeyboardButton("🎨 Create Landing Page", callback_data=CALLBACK_GENERATE)],
        [InlineKeyboardButton("❓ Help", callback_data=CALLBACK_HELP)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(welcome_text, reply_markup=reply_markup)

async def help_from_callback(query, context):
    """Handle help button callback."""
    help_text = """
🔧 **Detailed Help**

**Creating a Landing Page:**
1. Click "Create Landing Page" button
2. Follow the step-by-step process:
   • Enter your channel name
   • Upload your logo image
   • Select page type (1-10)
   • Choose footer option

**Available Page Types:**
1. Tech Startup - Modern, clean design
2. E-commerce Store - Product showcase
3. Personal Brand - Professional portfolio
4. SaaS Product - Software service
5. Restaurant/Food - Culinary focus
6. Fitness/Health - Workout plans
7. Education/Course - Learning platform
8. Non-profit - Cause-focused
9. Real Estate - Property listings
10. Creative Agency - Portfolio showcase

**What You'll Get:**
• A fully responsive HTML page
• Modern design with dark theme and vibrant colors
• Call-to-action button with countdown timer
• Professional layout with header, content, and footer
• All code in a single HTML file
• Live URL: channel-name.netlify.app

**GitHub Integration:**
• Each page is pushed to a new branch
• You'll get a direct link to the GitHub repository
• Automatic deployment to Netlify

Need help? Just ask!
    """
    
    keyboard = [
        [InlineKeyboardButton("🎨 Create Landing Page", callback_data=CALLBACK_GENERATE)],
        [InlineKeyboardButton("🏠 Main Menu", callback_data=CALLBACK_START)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(help_text, reply_markup=reply_markup)

async def generate_from_callback(query, context):
    """Handle generate button callback."""
    await query.edit_message_text(
        "🎨 Great! Let's create your landing page!\n\n"
        "First, what's the name of your channel? This will be used for the domain (channel-name.netlify.app)\n\n"
        "Please enter the channel name:"
    )
    context.user_data['conversation_state'] = CHANNEL_NAME

async def get_channel_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gets the channel name from user."""
    channel_name = update.message.text.strip()
    context.user_data['channel_name'] = channel_name
    
    await update.message.reply_text(
        f"✅ Channel name: {channel_name}\n\n"
        "Now, please send me your logo image (logo.png). You can send it as a photo or document.\n\n"
        "The image will be used as logo.png in your landing page."
    )
    return LOGO_IMAGE

async def get_logo_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles logo image upload."""
    if update.message.photo:
        # Get the largest photo
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        
        # Download and save as logo.png
        logo_path = os.path.join(REPO_DIR, "logo.png")
        os.makedirs(REPO_DIR, exist_ok=True)
        
        await file.download_to_drive(logo_path)
        context.user_data['logo_path'] = logo_path
        
    elif update.message.document:
        # Handle document upload
        document = update.message.document
        file = await context.bot.get_file(document.file_id)
        
        logo_path = os.path.join(REPO_DIR, "logo.png")
        os.makedirs(REPO_DIR, exist_ok=True)
        
        await file.download_to_drive(logo_path)
        context.user_data['logo_path'] = logo_path
    else:
        await update.message.reply_text("Please send a valid image file.")
        return LOGO_IMAGE
    
    # Show landing page types with buttons
    types_text = "🎯 Perfect! Now, what type of landing page do you want to create?\n\n"
    
    keyboard = []
    for key, description in LANDING_PAGE_TYPES.items():
        keyboard.append([InlineKeyboardButton(f"{key}. {description.split(' - ')[0]}", callback_data=f"page_type_{key}")])
    
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data=CALLBACK_CANCEL)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(types_text, reply_markup=reply_markup)
    return PAGE_TYPE

async def get_page_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gets the landing page type from user."""
    page_type = update.message.text.strip()
    
    if page_type not in LANDING_PAGE_TYPES:
        await update.message.reply_text(
            "❌ Invalid choice. Please enter a number between 1 and 10:"
        )
        return PAGE_TYPE
    
    context.user_data['page_type'] = page_type
    
    keyboard = [
        [InlineKeyboardButton("✅ Yes, add footer", callback_data=CALLBACK_FOOTER_YES)],
        [InlineKeyboardButton("❌ No footer", callback_data=CALLBACK_FOOTER_NO)],
        [InlineKeyboardButton("❌ Cancel", callback_data=CALLBACK_CANCEL)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"✅ Page type: {LANDING_PAGE_TYPES[page_type]}\n\n"
        "Do you want to add a footer with 'Ads by [your name]'?",
        reply_markup=reply_markup
    )
    return FOOTER_CHOICE

async def get_footer_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gets footer choice from user."""
    choice = update.message.text.strip().lower()
    
    if choice in ['yes', 'y']:
        await update.message.reply_text(
            "Great! Please enter the name for the footer (e.g., 'Your Company Name'):\n\n"
            "This will appear as 'Ads by [your name]' in the footer."
        )
        return FOOTER_TEXT
    elif choice in ['no', 'n']:
        context.user_data['footer_text'] = None
        await create_landing_page(update, context)
        return ConversationHandler.END
    else:
        await update.message.reply_text("Please reply with 'yes' or 'no':")
        return FOOTER_CHOICE

async def get_footer_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gets footer text from user."""
    footer_text = update.message.text.strip()
    context.user_data['footer_text'] = footer_text
    
    await create_landing_page(update, context)
    return ConversationHandler.END

async def create_landing_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Creates the landing page and deploys it."""
    channel_name = context.user_data.get('channel_name')
    page_type = context.user_data.get('page_type')
    footer_text = context.user_data.get('footer_text')
    logo_path = context.user_data.get('logo_path')
    
    await update.message.reply_text("🚀 Creating your landing page... This may take a moment.")
    
    # Check for GitHub PAT and clone/pull the repo
    if not GITHUB_PAT:
        await update.message.reply_text("❌ GitHub Personal Access Token is not configured.")
        return
    
    # Setup Git repository
    if not setup_git_repo():
        await update.message.reply_text("❌ Could not set up the Git repository.")
        return
    
    # Generate HTML content
    html_content = await generate_page_html(page_type, channel_name, footer_text)
    
    if not html_content:
        await update.message.reply_text("❌ Failed to generate the landing page. Please try again.")
        return
    
    # Save HTML file
    filename = "index.html"
    file_path = os.path.join(REPO_DIR, filename)
    
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(html_content)
    
    # Create branch name
    branch_name = f"page-{channel_name}"
    
    # Push to GitHub
    await update.message.reply_text("📤 Pushing to GitHub...")
    if push_to_github(filename, branch_name, logo_path):
        # Deploy to Netlify
        await update.message.reply_text("🌐 Deploying to Netlify...")
        netlify_url = deploy_to_netlify(branch_name, channel_name)
        
        if netlify_url:
            await update.message.reply_text(
                f"🎉 **Success! Your landing page is live!**\n\n"
                f"🔗 **URL:** {netlify_url}\n"
                f"📁 **Branch:** {branch_name}\n"
                f"🎨 **Type:** {LANDING_PAGE_TYPES[page_type]}\n\n"
                f"Your page is now accessible at the URL above!"
            )
        else:
            await update.message.reply_text(
                f"✅ **Page created successfully!**\n\n"
                f"📁 **Branch:** {branch_name}\n"
                f"🎨 **Type:** {LANDING_PAGE_TYPES[page_type]}\n\n"
                f"⚠️ Netlify deployment failed, but your page is available on GitHub."
            )
    else:
        await update.message.reply_text("❌ Failed to push to GitHub. Please check the logs.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the conversation."""
    await update.message.reply_text("❌ Landing page creation cancelled.")
    return ConversationHandler.END

async def page_type_callback(query, context, page_type):
    """Handle page type selection callback."""
    if page_type not in LANDING_PAGE_TYPES:
        await query.answer("Invalid page type selected!")
        return
    
    context.user_data['page_type'] = page_type
    
    keyboard = [
        [InlineKeyboardButton("✅ Yes, add footer", callback_data=CALLBACK_FOOTER_YES)],
        [InlineKeyboardButton("❌ No footer", callback_data=CALLBACK_FOOTER_NO)],
        [InlineKeyboardButton("❌ Cancel", callback_data=CALLBACK_CANCEL)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"✅ Page type: {LANDING_PAGE_TYPES[page_type]}\n\n"
        "Do you want to add a footer with 'Ads by [your name]'?",
        reply_markup=reply_markup
    )

async def footer_yes_callback(query, context):
    """Handle footer yes callback."""
    await query.edit_message_text(
        "Great! Please enter the name for the footer (e.g., 'Your Company Name'):\n\n"
        "This will appear as 'Ads by [your name]' in the footer."
    )
    context.user_data['conversation_state'] = FOOTER_TEXT

async def footer_no_callback(query, context):
    """Handle footer no callback."""
    context.user_data['footer_text'] = None
    await create_landing_page_from_callback(query, context)

async def cancel_from_callback(query, context):
    """Handle cancel callback."""
    await query.edit_message_text(
        "❌ Landing page creation cancelled.\n\n"
        "Click the button below to start over:",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🎨 Create Landing Page", callback_data=CALLBACK_GENERATE)
        ]])
    )

async def create_landing_page_from_callback(query, context):
    """Creates the landing page from callback."""
    channel_name = context.user_data.get('channel_name')
    page_type = context.user_data.get('page_type')
    footer_text = context.user_data.get('footer_text')
    logo_path = context.user_data.get('logo_path')
    
    await query.edit_message_text("🚀 Creating your landing page... This may take a moment.")
    
    # Check for GitHub PAT and clone/pull the repo
    if not GITHUB_PAT:
        await query.edit_message_text("❌ GitHub Personal Access Token is not configured.")
        return
    
    # Setup Git repository
    if not setup_git_repo():
        await query.edit_message_text("❌ Could not set up the Git repository.")
        return
    
    # Generate HTML content
    html_content = await generate_page_html(page_type, channel_name, footer_text)
    
    if not html_content:
        await query.edit_message_text("❌ Failed to generate the landing page. Please try again.")
        return
    
    # Save HTML file
    filename = "index.html"
    file_path = os.path.join(REPO_DIR, filename)
    
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(html_content)
    
    # Create branch name
    branch_name = f"page-{channel_name}"
    
    # Push to GitHub
    await query.edit_message_text("📤 Pushing to GitHub...")
    if push_to_github(filename, branch_name, logo_path):
        # Deploy to Netlify
        await query.edit_message_text("🌐 Deploying to Netlify...")
        netlify_url = deploy_to_netlify(branch_name, channel_name)
        
        if netlify_url:
            keyboard = [
                [InlineKeyboardButton("🔗 Open Website", url=netlify_url)],
                [InlineKeyboardButton("🎨 Create Another", callback_data=CALLBACK_GENERATE)],
                [InlineKeyboardButton("🏠 Main Menu", callback_data=CALLBACK_START)]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"🎉 **Success! Your landing page is live!**\n\n"
                f"🔗 **URL:** {netlify_url}\n"
                f"📁 **Branch:** {branch_name}\n"
                f"🎨 **Type:** {LANDING_PAGE_TYPES[page_type]}\n\n"
                f"Your page is now accessible at the URL above!",
                reply_markup=reply_markup
            )
        else:
            keyboard = [
                [InlineKeyboardButton("🎨 Create Another", callback_data=CALLBACK_GENERATE)],
                [InlineKeyboardButton("🏠 Main Menu", callback_data=CALLBACK_START)]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"✅ **Page created successfully!**\n\n"
                f"📁 **Branch:** {branch_name}\n"
                f"🎨 **Type:** {LANDING_PAGE_TYPES[page_type]}\n\n"
                f"⚠️ Netlify deployment failed, but your page is available on GitHub.",
                reply_markup=reply_markup
            )
    else:
        keyboard = [
            [InlineKeyboardButton("🎨 Try Again", callback_data=CALLBACK_GENERATE)],
            [InlineKeyboardButton("🏠 Main Menu", callback_data=CALLBACK_START)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "❌ Failed to push to GitHub. Please check the logs.",
            reply_markup=reply_markup
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles text messages during conversation flow."""
    if not update.message or not update.message.text:
        return
    
    user_query = update.message.text.strip()
    
    # Check if we're in a conversation state
    conversation_state = context.user_data.get('conversation_state')
    
    if conversation_state == CHANNEL_NAME:
        # Handle channel name input
        context.user_data['channel_name'] = user_query
        await update.message.reply_text(
            f"✅ Channel name: {user_query}\n\n"
            "Now, please send me your logo image (logo.png). You can send it as a photo or document.\n\n"
            "The image will be used as logo.png in your landing page."
        )
        context.user_data['conversation_state'] = LOGO_IMAGE
        
    elif conversation_state == FOOTER_TEXT:
        # Handle footer text input
        context.user_data['footer_text'] = user_query
        await create_landing_page_from_message(update, context)
        
    else:
        # Show main menu for any other text
        keyboard = [
            [InlineKeyboardButton("🎨 Create Landing Page", callback_data=CALLBACK_GENERATE)],
            [InlineKeyboardButton("❓ Help", callback_data=CALLBACK_HELP)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "👋 Hi! I'm your Landing Page Generator Bot.\n\n"
            "Click the button below to get started:",
            reply_markup=reply_markup
        )

async def create_landing_page_from_message(update, context):
    """Creates the landing page from message flow."""
    channel_name = context.user_data.get('channel_name')
    page_type = context.user_data.get('page_type')
    footer_text = context.user_data.get('footer_text')
    logo_path = context.user_data.get('logo_path')
    
    await update.message.reply_text("🚀 Creating your landing page... This may take a moment.")
    
    # Check for GitHub PAT and clone/pull the repo
    if not GITHUB_PAT:
        await update.message.reply_text("❌ GitHub Personal Access Token is not configured.")
        return
    
    # Setup Git repository
    if not setup_git_repo():
        await update.message.reply_text("❌ Could not set up the Git repository.")
        return
    
    # Generate HTML content
    html_content = await generate_page_html(page_type, channel_name, footer_text)
    
    if not html_content:
        await update.message.reply_text("❌ Failed to generate the landing page. Please try again.")
        return
    
    # Save HTML file
    filename = "index.html"
    file_path = os.path.join(REPO_DIR, filename)
    
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(html_content)
    
    # Create branch name
    branch_name = f"page-{channel_name}"
    
    # Push to GitHub
    await update.message.reply_text("📤 Pushing to GitHub...")
    if push_to_github(filename, branch_name, logo_path):
        # Deploy to Netlify
        await update.message.reply_text("🌐 Deploying to Netlify...")
        netlify_url = deploy_to_netlify(branch_name, channel_name)
        
        if netlify_url:
            keyboard = [
                [InlineKeyboardButton("🔗 Open Website", url=netlify_url)],
                [InlineKeyboardButton("🎨 Create Another", callback_data=CALLBACK_GENERATE)],
                [InlineKeyboardButton("🏠 Main Menu", callback_data=CALLBACK_START)]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"🎉 **Success! Your landing page is live!**\n\n"
                f"🔗 **URL:** {netlify_url}\n"
                f"📁 **Branch:** {branch_name}\n"
                f"🎨 **Type:** {LANDING_PAGE_TYPES[page_type]}\n\n"
                f"Your page is now accessible at the URL above!",
                reply_markup=reply_markup
            )
        else:
            keyboard = [
                [InlineKeyboardButton("🎨 Create Another", callback_data=CALLBACK_GENERATE)],
                [InlineKeyboardButton("🏠 Main Menu", callback_data=CALLBACK_START)]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"✅ **Page created successfully!**\n\n"
                f"📁 **Branch:** {branch_name}\n"
                f"🎨 **Type:** {LANDING_PAGE_TYPES[page_type]}\n\n"
                f"⚠️ Netlify deployment failed, but your page is available on GitHub.",
                reply_markup=reply_markup
            )
    else:
        keyboard = [
            [InlineKeyboardButton("🎨 Try Again", callback_data=CALLBACK_GENERATE)],
            [InlineKeyboardButton("🏠 Main Menu", callback_data=CALLBACK_START)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "❌ Failed to push to GitHub. Please check the logs.",
            reply_markup=reply_markup
        )

# --- Main function to start the bot ---
def main() -> None:
    """Starts the bot."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Add callback query handler for buttons
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Add message handler for text and images
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO | filters.Document.IMAGE, get_logo_image))

    # Run the bot until the user presses Ctrl-C
    print("Bot started. Press Ctrl-C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
