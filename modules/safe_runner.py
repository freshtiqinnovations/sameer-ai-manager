
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
import subprocess
from datetime import datetime
from pathlib import Path

BASE = Path("/root/sameer_ai_manager")
LOG_DIR = BASE / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

def run_shell(cmd: str, timeout: int = 120) -> str:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            executable="/bin/bash",
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = (result.stdout or "") + (result.stderr or "")
        if not output.strip():
            output = "✅ Command completed. No output."
        final = output[-4000:]
    except Exception as e:
        final = f"❌ Command error: {e}"

    with open(LOG_DIR / "safe_runner.log", "a", encoding="utf-8") as f:
        f.write(f"\n\n===== {ts} =====\nCMD: {cmd}\nOUTPUT:\n{final}\n")

    return final
