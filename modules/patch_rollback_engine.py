
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
from pathlib import Path
import shutil
import subprocess

BASE = Path("/root/sameer_ai_manager")
BACKUPS = BASE / "backups"

def rollback_latest():
    files = sorted(BACKUPS.glob("bot_before_apply_*.py"), reverse=True)
    if not files:
        return "NO_APPLY_BACKUP_FOUND"

    latest = files[0]
    shutil.copy(latest, BASE / "bot.py")

    subprocess.check_call(["python3", "-m", "py_compile", str(BASE / "bot.py")])

    subprocess.Popen(
        ["bash", "-lc", "sleep 2 && systemctl restart sameer_ai_manager"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    return f"ROLLBACK_OK:{latest.name}"
