
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
import subprocess, datetime

def run_autoupgrade(bot, task):
    log="/root/sameer_ai_manager/logs/autoupgrade.log"
    msg=f"{datetime.datetime.now()} | BOT={bot} | TASK={task}\n"
    open(log,"a").write(msg)
    return f"✅ AUTO UPGRADE QUEUED\nBot: {bot}\nTask: {task}\n\nSaved in autoupgrade.log"
