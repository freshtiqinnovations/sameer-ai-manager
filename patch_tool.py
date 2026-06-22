
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
import shutil
import subprocess
from datetime import datetime

BASE = "/root/sameer_ai_manager"
BOT_FILE = f"{BASE}/bot.py"
PATCH_FILE = f"{BASE}/ai_patch.txt"
BACKUP_DIR = f"{BASE}/backups"

ts = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = f"{BACKUP_DIR}/bot_{ts}.py"

os.makedirs(BACKUP_DIR, exist_ok=True)

print("📦 Creating backup...")
shutil.copy2(BOT_FILE, backup_file)

if not os.path.exists(PATCH_FILE):
    print("❌ ai_patch.txt not found")
    exit(1)

with open(PATCH_FILE, "r", encoding="utf-8") as f:
    patch = f.read()

unsafe = [
    "rm -rf",
    "os.remove",
    "shutil.rmtree",
    "subprocess.Popen",
]

for bad in unsafe:
    if bad in patch:
        print(f"❌ Unsafe code detected: {bad}")
        exit(1)

print("🧠 Applying patch...")

with open(BOT_FILE, "a", encoding="utf-8") as f:
    f.write("\n\n# === AI PATCH START ===\n")
    f.write(patch)
    f.write("\n# === AI PATCH END ===\n")

print("🧪 Compile checking...")

result = subprocess.run(
    ["python3", "-m", "py_compile", BOT_FILE],
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print("❌ Compile failed")
    print(result.stderr)

    print("♻️ Restoring backup...")
    shutil.copy2(backup_file, BOT_FILE)

    exit(1)

print("🚀 Restarting bot...")

restart = subprocess.run(
    ["systemctl", "restart", "sameer_ai_manager"],
    capture_output=True,
    text=True
)

print("✅ APPLY SUCCESS")
