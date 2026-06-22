
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
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

BASE = Path("/root/sameer_ai_manager")
BOT = BASE / "bot.py"
BACKUPS = BASE / "backups"
BACKUPS.mkdir(exist_ok=True)

def sh(cmd, timeout=120):
    return subprocess.run(
        cmd,
        shell=True,
        executable="/bin/bash",
        capture_output=True,
        text=True,
        timeout=timeout
    )

def run_ai_fix(note=""):
    ts = datetime.now().strftime("%Y-%m-%d_%H%M")
    backup = BACKUPS / f"bot_before_fix_{ts}.py"

    shutil.copy2(BOT, backup)

    check = sh(f"python3 -m py_compile {BOT}")

    if check.returncode != 0:
        return "❌ Compile failed:\n\n" + (check.stdout + check.stderr)[-3000:]

    return (
        "✅ FIX CHECK SUCCESS\n"
        "Backup created:\n"
        f"{backup}\n\n"
        "Compile OK.\n"
        "Agar restart chahiye to /repair bhejo."
    )
