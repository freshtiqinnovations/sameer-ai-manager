
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
import json, subprocess, asyncio
from datetime import datetime, timezone
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters

CONFIG="/root/.openclaw/openclaw.json"
ADMIN_ID=8649581921

def token():
    return json.load(open(CONFIG))["channels"]["telegram"]["botToken"]

def sh(cmd, timeout=60):
    try:
        return subprocess.getoutput(cmd)[:3500] or "OK"
    except Exception as e:
        return str(e)

def health():
    names=[
        "tor.service","sameer_ai_manager.service","openclaw_telegram.service",
        "openclaw_chat.service","openclaw_webhook.service",
        "openclaw_fortress.service","openclaw_watcher.service"
    ]
    out=["🧠 OPENCLAW LIVE STATUS"]
    for n in names:
        s=sh(f"systemctl is-active {n}").strip()
        out.append(f"{'✅' if s=='active' else '❌'} {n}: {s}")
    out.append("Failed units: "+sh("systemctl --failed --no-legend | wc -l").strip())
    return "\n".join(out)

async def send_long(msg, text):
    for i in range(0, len(text), 3500):
        await msg.reply_text(text[i:i+3500])

async def start(update:Update, context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ OpenClaw Operator online.\nSend: status\nSend command: /sh systemctl --failed")

async def handle(update:Update, context:ContextTypes.DEFAULT_TYPE):
    msg=update.message
    uid=update.effective_user.id
    text=(msg.text or "").strip()
    if uid != ADMIN_ID:
        return await msg.reply_text("Unauthorized")
    await context.bot.send_chat_action(chat_id=msg.chat_id, action=ChatAction.TYPING)
    low=text.lower()
    if low in ["status","/status","health","/health"]:
        return await msg.reply_text(health())
    if low in ["who are you","/who","hi","hello"]:
        return await msg.reply_text("🧠 I am Sameer OpenClaw Operator. I am online and ready to repair/manage your VPS.")
    if low.startswith("/sh "):
        return await send_long(msg, "🖥 OUTPUT\n\n"+sh(text[4:]))
    if low.startswith("/run "):
        return await send_long(msg, "🖥 OUTPUT\n\n"+sh(text[5:]))
    return await send_long(msg, "🖥 OUTPUT\\n\\n"+sh(text))


async def cmd_ask(update, context):
    prompt = " ".join(context.args).strip()
    if not prompt:
        return await update.message.reply_text("Usage: /ask your question")
    await update.message.reply_text("🧠 DeepSeek agent working...")
    try:
        import sys
        sys.path.insert(0, "/root/sameer_ai_manager/openclaw_bridge")
        from deepseek_api import smart_call
        ans = smart_call(prompt, "Answer short in Hinglish. Direct solution only.", 700)
        await update.message.reply_text((ans or "NO_REPLY")[:3500])
    except Exception as e:
        await update.message.reply_text("DEEPSEEK_ERROR: " + str(e)[:500])


def main():
    app=Application.builder().token(token()).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ask", cmd_ask))
    app.add_handler(MessageHandler(filters.TEXT, handle))
    app.run_polling(drop_pending_updates=True)

if __name__=="__main__":
    main()
