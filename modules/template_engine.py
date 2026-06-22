
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

def create_template(name, bot_type):
    cmd = ["sameer-template", name, bot_type]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    return (result.stdout + result.stderr).strip()
