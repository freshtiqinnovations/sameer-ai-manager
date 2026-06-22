
# --- SMART_CONVERSATION_FILTER START ---
def is_valid_terminal_command(text_input):
    clean_text = str(text_input).strip().lower()
    allowed = ['pwd', 'df', 'free', 'systemctl', 'ls', 'top', 'uptime', 'ifconfig']
    if not clean_text: return False
    first_word = clean_text.split()[0]
    if first_word in allowed and len(clean_text.split()) <= 4:
        return True
    return False
# --- SMART_CONVERSATION_FILTER END ---
#!/usr/bin/env python3
"""
CODE FACTORY — AI Code Generator + Bot Builder + App Builder
Uses DeepSeek API (or free fallback) to generate code from prompts.
Sameer AI bolega → Code Factory code likhega → OpenClaw deploy karega.
"""
import json, subprocess, os, re, time
from pathlib import Path
from datetime import datetime, timezone

BRIDGE = Path("/root/sameer_ai_manager/openclaw_bridge")
LOG = BRIDGE / "code_factory.log"
DEEPSEEK_ENABLED = False  # Will be set if key is configured

def log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    msg = f"[{ts}] {msg}"
    with open(LOG, "a") as f:
        f.write(msg + "\n")
    print(msg)

def sh(cmd):
    return subprocess.getoutput(cmd).strip()

def load_deepseek_key():
    """Load DeepSeek API key from env or config."""
    env_file = Path("/root/sameer_ai_manager/.env")
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if "DEEPSEEK_API_KEY" in line and "your" not in line and "sk-" in line:
                key = line.split("=", 1)[1].strip()
                if key:
                    return key
    return None

def call_deepseek(prompt, system_prompt="You are a code generator. Write clean, production-ready code."):
    """Call DeepSeek API for code generation."""
    key = load_deepseek_key()
    if not key:
        log("⚠️ DeepSeek API key not configured — using template fallback")
        return None
    
    try:
        import urllib.request
        data = json.dumps({
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 4096
        }).encode()
        
        req = urllib.request.Request(
            "https://api.deepseek.com/v1/chat/completions",
            data=data,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            }
        )
        
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            content = result["choices"][0]["message"]["content"]
            log(f"✅ DeepSeek response: {len(content)} chars")
            return content
    except Exception as e:
        log(f"❌ DeepSeek API error: {e}")
        return None

def generate_bot(prompt):
    """Generate a Telegram bot from prompt."""
    log(f"🤖 Generating bot: {prompt[:60]}...")
    
    # Try DeepSeek first
    code = call_deepseek(
        f"Create a complete Python Telegram bot using python-telegram-bot library. Prompt: {prompt}\n"
        f"Requirements:\n"
        f"- Use python-telegram-bot v20+\n"
        f"- Async handlers\n"
        f"- /start, /help commands\n"
        f"- Error handling\n"
        f"- Config from environment variables\n"
        f"Return ONLY the Python code, no explanation."
    )
    
    if not code:
        # Free fallback: template-based
        code = _generate_bot_template(prompt)
    
    return code

def generate_website(prompt):
    """Generate a website from prompt."""
    log(f"🌐 Generating website: {prompt[:60]}...")
    
    code = call_deepseek(
        f"Create a complete HTML/CSS/JS website. Prompt: {prompt}\n"
        f"Requirements:\n"
        f"- Modern responsive design\n"
        f"- Mobile-first CSS\n"
        f"- Semantic HTML5\n"
        f"- No external dependencies\n"
        f"Return ONLY the complete HTML file with embedded CSS and JS."
    )
    
    if not code:
        code = _generate_website_template(prompt)
    
    return code

def generate_script(prompt):
    """Generate a bash/python script from prompt."""
    log(f"📜 Generating script: {prompt[:60]}...")
    
    code = call_deepseek(
        f"Create a complete {prompt}\n"
        f"Requirements:\n"
        f"- Error handling\n"
        f"- Input validation\n"
        f"- Clear comments\n"
        f"Return ONLY the code, no explanation."
    )
    
    if not code:
        code = f"#!/usr/bin/env python3\n# Auto-generated: {prompt}\n# TODO: Implement\nprint('Not yet implemented: {prompt}')\n"
    
    return code

def _generate_bot_template(prompt):
    """Free fallback bot template."""
    name = "custom_bot"
    if "support" in prompt.lower() or "customer" in prompt.lower():
        name = "support_bot"
    elif "shop" in prompt.lower() or "store" in prompt.lower():
        name = "shop_bot"
    elif "lead" in prompt.lower() or "contact" in prompt.lower():
        name = "lead_bot"
    
    code = f'''#!/usr/bin/env python3
"""
Auto-generated bot: {name}
Prompt: {prompt}
"""
import logging, os, json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"👋 Hello {{user.first_name}}!\\n\\n"
        f"Welcome to {name.replace('_',' ').title()}.\\n"
        f"Use /help to see available commands."
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Available commands:\\n"
        "/start - Start the bot\\n"
        "/help - Show this message\\n"
        "/contact - Contact us\\n"
        "/about - About us"
    )

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📞 Contact us:\\n"
        "Phone: +918381848389\\n"
        "Email: contact@freshtiqautomation.com\\n"
        "Website: https://freshtiqautomation.com"
    )

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Freshtiq Automation\\n"
        "Building intelligent solutions for businesses.\\n"
        "Powered by Sameer AI Manager + OpenClaw."
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"You said: {{update.message.text}}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("contact", contact))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    print(f"🤖 {name.replace('_',' ').title()} started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
'''
    return code

def _generate_website_template(prompt):
    """Free fallback website template."""
    title = "My Website"
    if "business" in prompt.lower():
        title = "Business Website"
    elif "portfolio" in prompt.lower():
        title = "Portfolio"
    elif "landing" in prompt.lower():
        title = "Landing Page"
    
    code = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Freshtiq Automation</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
        header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 100px 0; text-align: center; }}
        header h1 {{ font-size: 3em; margin-bottom: 20px; }}
        header p {{ font-size: 1.2em; opacity: 0.9; }}
        section {{ padding: 80px 0; }}
        .features {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; margin-top: 40px; }}
        .feature {{ background: #f8f9fa; padding: 30px; border-radius: 10px; text-align: center; }}
        .feature h3 {{ margin-bottom: 15px; color: #667eea; }}
        .cta {{ background: #667eea; color: white; text-align: center; padding: 80px 0; }}
        .cta h2 {{ font-size: 2.5em; margin-bottom: 20px; }}
        .btn {{ display: inline-block; padding: 15px 40px; background: white; color: #667eea; text-decoration: none; border-radius: 50px; font-weight: bold; font-size: 1.1em; transition: transform 0.3s; }}
        .btn:hover {{ transform: translateY(-3px); }}
        footer {{ background: #333; color: white; text-align: center; padding: 40px 0; }}
        footer a {{ color: #667eea; text-decoration: none; }}
        @media (max-width: 768px) {{ header h1 {{ font-size: 2em; }} .cta h2 {{ font-size: 1.8em; }} }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>{title}</h1>
            <p>Built with ❤️ by Freshtiq Automation</p>
        </div>
    </header>
    <section>
        <div class="container">
            <h2 style="text-align:center;margin-bottom:20px;">Our Services</h2>
            <p style="text-align:center;margin-bottom:40px;">We provide cutting-edge solutions for your business needs.</p>
            <div class="features">
                <div class="feature"><h3>🚀 Web Development</h3><p>Modern, responsive websites built with latest technologies.</p></div>
                <div class="feature"><h3>🤖 Bot Development</h3><p>Intelligent bots for automation and customer support.</p></div>
                <div class="feature"><h3>📱 Mobile Apps</h3><p>Cross-platform apps with Flutter for Android & iOS.</p></div>
            </div>
        </div>
    </section>
    <section class="cta">
        <div class="container">
            <h2>Ready to Get Started?</h2>
            <p style="margin-bottom:30px;font-size:1.2em;">Contact us today for a free consultation.</p>
            <a href="https://t.me/AutoPilotHubBot" class="btn">Contact Us on Telegram</a>
        </div>
    </section>
    <footer>
        <div class="container">
            <p>&copy; 2026 Freshtiq Automation. All rights reserved.</p>
            <p style="margin-top:10px;">Contact: <a href="https://wa.me/918381848389">WhatsApp</a> | <a href="https://t.me/AutoPilotHubBot">Telegram</a></p>
        </div>
    </footer>
</body>
</html>'''
    return code


def main():
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    prompt = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "default"

    if action in ("generate_bot","bot"):
        print(generate_bot(prompt))
    elif action in ("generate_website","website"):
        print(generate_website(prompt))
    elif action in ("generate_script","script","generate"):
        print(generate_script(prompt))
    else:
        print("Usage: code_factory.py generate_bot|generate_website|generate_script <prompt>")

if __name__ == "__main__":
    main()
