
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
import shlex

QUEUE="/root/sameer_ai_manager/ai_worker/queue"
DONE="/root/sameer_ai_manager/ai_worker/completed"
FAILED="/root/sameer_ai_manager/ai_worker/failed"
LOG="/root/sameer_ai_manager/ai_worker/logs/worker_v2.log"
PLAN_RUNNER="/root/sameer_ai_manager/ai_worker/plan_runner.py"
PY="/root/sameer_ai_manager/venv/bin/python"

for d in [QUEUE,DONE,FAILED,os.path.dirname(LOG)]:
    os.makedirs(d, exist_ok=True)

def log(x):
    line=f"{datetime.datetime.now()} | {x}"
    print(line)
    open(LOG,"a").write(line+"\n")

def process_task(path):
    data=json.load(open(path))
    bot=data.get("bot","").strip()
    task=data.get("task","").strip()
    if not bot or not task:
        raise Exception("BAD_TASK_JSON")
    log(f"START bot={bot} task={task}")
    cmd=f"{PY} {PLAN_RUNNER} {shlex.quote(bot)} {shlex.quote(task)}"
    plan_path=subprocess.getoutput(cmd).strip()
    if not plan_path.startswith("/root/sameer_ai_manager/ai_worker/plans/"):
        raise Exception("PLAN_FAILED "+plan_path[:500])
    log(f"AI_PLAN_OK {plan_path}")
    shutil.move(path, os.path.join(DONE, os.path.basename(path)))
    log(f"DONE {os.path.basename(path)}")

log("WORKER_V2_PLAN_ONLY_STARTED")

while True:
    try:
        files=[x for x in os.listdir(QUEUE) if x.endswith(".json")]
        for f in files:
            path=os.path.join(QUEUE,f)
            try:
                process_task(path)
            except Exception as e:
                log(f"FAILED {f} ERROR={e}")
                shutil.move(path, os.path.join(FAILED,f))
        time.sleep(5)
    except Exception as e:
        log(f"MAIN_ERROR {e}")
        time.sleep(5)
