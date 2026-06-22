
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
import json
import time
import shutil
import datetime
import subprocess
import sys
sys.path.append("/root/sameer_ai_manager")
from ai_brain.auto_coder import plan as ai_plan

QUEUE="/root/sameer_ai_manager/ai_worker/queue"
DONE="/root/sameer_ai_manager/ai_worker/completed"
FAILED="/root/sameer_ai_manager/ai_worker/failed"
LOG="/root/sameer_ai_manager/ai_worker/logs/worker.log"

def log(x):
    with open(LOG,"a") as f:
        f.write(f"{datetime.datetime.now()} | {x}\n")

def process_task(path):
    try:
        data=json.load(open(path))

        bot=data.get("bot")
        task=data.get("task")

        log(f"START {bot} => {task}")

        project=f"/root/workspaces/customers/{bot}"

        if not os.path.exists(project):
            log(f"BOT_NOT_FOUND {bot}")
            shutil.move(path,f"{FAILED}/{os.path.basename(path)}")
            return

        backup=f"/root/backups/{bot}_{int(time.time())}.tar.gz"

        subprocess.getoutput(
            f"tar -czf {backup} {project}"
        )

        log(f"BACKUP_OK {backup}")

        note=f"{project}/AUTO_UPGRADE_NOTE.txt"

        with open(note,"a") as f:
            f.write(f"\n[{datetime.datetime.now()}] {task}\n")

        service=f"{bot}.service"

        subprocess.getoutput(
            f"systemctl restart {service}"
        )

        status=subprocess.getoutput(
            f"systemctl is-active {service}"
        ).strip()

        log(f"SERVICE {service} => {status}")

        if status=="active":
            shutil.move(path,f"{DONE}/{os.path.basename(path)}")
            log(f"SUCCESS {bot}")
        else:
            shutil.move(path,f"{FAILED}/{os.path.basename(path)}")
            log(f"FAILED {bot}")

    except Exception as e:
        log(f"ERROR {e}")

while True:
    try:
        files=[x for x in os.listdir(QUEUE) if x.endswith(".json")]

        for f in files:
            process_task(f"{QUEUE}/{f}")

    except Exception as e:
        log(f"MAIN_ERROR {e}")

    time.sleep(20)
