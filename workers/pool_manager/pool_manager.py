
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
import os, subprocess, time

QUEUE = "/root/sameer_ai_manager/ai_worker/queue"
MAX_WORKERS = 10

def qcount():
    return len([x for x in os.listdir(QUEUE) if x.endswith(".json")])

def active(n):
    return subprocess.getoutput(f"systemctl is-active sameer_ai_worker_auto@{n}.service").strip() == "active"

def start(n):
    subprocess.getoutput(f"systemctl restart sameer_ai_worker_auto@{n}.service")

def stop(n):
    subprocess.getoutput(f"systemctl stop sameer_ai_worker_auto@{n}.service")

while True:
    q = qcount()
    need = min(MAX_WORKERS, max(1, (q // 5) + 1))
    for i in range(2, MAX_WORKERS + 1):
        if i <= need and not active(i):
            start(i)
        if i > need and active(i):
            stop(i)
    time.sleep(15)
