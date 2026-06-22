
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
from datetime import datetime

BASE = Path("/root/sameer_ai_manager")
UPGRADES = BASE / "upgrades"

def apply_patch(filename):

    approved = UPGRADES / "approved" / filename

    if not approved.exists():
        return "PATCH_NOT_FOUND"

    backup_dir = BASE / "backups"
    backup_dir.mkdir(exist_ok=True)

    backup_file = backup_dir / f"bot_before_apply_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"

    shutil.copy(BASE / "bot.py", backup_file)

    try:

        with open(approved, "r") as f:
            content = f.read()

        marker = "# AUTO_PATCH_APPEND"

        bot = (BASE / "bot.py").read_text()

        if marker not in bot:
            bot += "\n\n# AUTO_PATCH_APPEND\n"

        bot += "\n" + content + "\n"

        (BASE / "bot.py").write_text(bot)

        subprocess.check_call([
            "python3",
            "-m",
            "py_compile",
            str(BASE / "bot.py")
        ])

        # Restart in background so Telegram command does not die with SIGTERM
        subprocess.Popen(
            ["bash", "-lc", "sleep 2 && systemctl restart sameer_ai_manager"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        applied = UPGRADES / "applied" / filename

        shutil.move(str(approved), str(applied))

        return "PATCH_APPLIED_OK"

    except Exception as e:

        shutil.copy(backup_file, BASE / "bot.py")

        return f"FAILED: {e}"
