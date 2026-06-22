
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
import os
import re
import subprocess

def _safe_name(raw: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]+", "_", raw.lower()).strip("_")

def _is_admin(user_id) -> bool:
    allowed = os.getenv("ALLOWED_USER_IDS", "")
    return str(user_id) in [x.strip() for x in allowed.split(",") if x.strip()]

async def deploy_template_cmd(update, context):
    if not _is_admin(update.effective_user.id):
        return await update.message.reply_text("Access denied.")

    if len(context.args) < 3:
        return await update.message.reply_text(
            "Use: /deploy_template botname token template\n"
            "Templates: telegram_basic, travel_agency, shop_bot, support_bot, ai_assistant"
        )

    botname = _safe_name(context.args[0])
    token = context.args[1].strip()
    template = _safe_name(context.args[2])

    allowed = ["telegram_basic", "travel_agency", "shop_bot", "support_bot", "ai_assistant", "appointment_bot"]
    if template not in allowed:
        return await update.message.reply_text("Invalid template. Use: " + ", ".join(allowed))

    cmd = f"/root/customer_templates/deploy_template.sh {botname} {token} {template}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=180)
    out = (result.stdout + result.stderr)[-3500:]

    await update.message.reply_text("✅ TEMPLATE DEPLOY RESULT:\n\n" + out)
