
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
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv("/root/sameer_ai_manager/.env")

BASE = Path("/root/sameer_ai_manager")
BOT = BASE / "bot.py"
BACKUPS = BASE / "backups"
LOGS = BASE / "logs"
BACKUPS.mkdir(exist_ok=True)
LOGS.mkdir(exist_ok=True)

SERVICE = "sameer_ai_manager"

def sh(cmd, timeout=90):
    return subprocess.run(
        cmd,
        shell=True,
        executable="/bin/bash",
        capture_output=True,
        text=True,
        timeout=timeout
    )

def ai_repair(user_note=""):
    ts = datetime.now().strftime("%Y-%m-%d_%H%M")
    backup = BACKUPS / f"bot_before_ai_fix_{ts}.py"
    shutil.copy2(BOT, backup)

    compile_check = sh(f"python3 -m py_compile {BOT}")
    logs = sh(f"journalctl -u {SERVICE} -n 120 --no-pager").stdout[-8000:]

    current_code = BOT.read_text(encoding="utf-8")

    prompt = f"""
You are Sameer AI Manager repair engineer.

Goal:
Fix / improve this Python Telegram bot safely.

Rules:
- Return ONLY full corrected Python code.
- No markdown.
- No explanation.
- Do not remove existing commands.
- Preserve OpenAI, Telegram, /run, /agent, /approve_patch features.
- Never include real API keys or secrets.
- Fix syntax, runtime, indentation, command handling, and Telegram reply issues.
- Keep bot.py compatible with python-telegram-bot async style.

User note:
{user_note}

Compile result:
{compile_check.stdout}
{compile_check.stderr}

Recent logs:
{logs}

Current bot.py:
{current_code}
"""

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "❌ OPENAI_API_KEY missing in environment."

    client = OpenAI(api_key=api_key)
    res = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-5.5"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )

    fixed = res.choices[0].message.content.strip()
    fixed = fixed.replace("```python", "").replace("```", "").strip()

    BOT.write_text(fixed, encoding="utf-8")

    check2 = sh(f"python3 -m py_compile {BOT}")
    if check2.returncode != 0:
        shutil.copy2(backup, BOT)
        return "❌ AI repair failed. Rolled back.\n\n" + (check2.stdout + check2.stderr)[-3000:]

    restart = sh(f"systemctl restart {SERVICE} && systemctl status {SERVICE} --no-pager", timeout=120)
    return "✅ AI REPAIR SUCCESS\n\nBackup:\n" + str(backup) + "\n\n" + (restart.stdout + restart.stderr)[-3000:]
