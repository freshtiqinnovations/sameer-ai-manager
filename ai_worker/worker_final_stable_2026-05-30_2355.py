
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
import os, json, time, shutil, datetime, subprocess

BASE="/root/sameer_ai_manager/ai_worker"
QUEUE=f"{BASE}/queue"
DONE=f"{BASE}/completed"
FAILED=f"{BASE}/failed"
LOG=f"{BASE}/logs/worker.log"
PYTHON="/root/sameer_ai_manager/venv/bin/python"

BOTS={
 "autopilot":{"project":"/root/monster_bot","file":"/root/monster_bot/admin_panel.py","service":"autopilot_hub_bot.service"},
 "freshtiq_ai_travel_pro":{"project":"/root/workspaces/customers/freshtiq_ai_travel_pro","file":"/root/workspaces/customers/freshtiq_ai_travel_pro/bot.py","service":"freshtiq_ai_travel_pro.service"}
}

for d in [QUEUE,DONE,FAILED,os.path.dirname(LOG),"/root/backups/ai_worker"]:
    os.makedirs(d, exist_ok=True)

def log(x):
    line=f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {x}"
    print(line)
    open(LOG,"a").write(line+"\n")

def sh(cmd):
    return subprocess.getoutput(cmd).strip()

def move(path,dst):
    shutil.move(path, os.path.join(dst, os.path.basename(path)))

def process_task(path):
    data=json.load(open(path))
    bot=data.get("bot")
    task=data.get("task","")
    info=BOTS.get(bot)
    if not info:
        raise Exception(f"BOT_NOT_MAPPED {bot}")

    project=info["project"]
    code_file=info["file"]
    service=info["service"]

    if not os.path.isdir(project):
        raise Exception(f"PROJECT_NOT_FOUND {project}")

    ts=str(int(time.time()))
    backup=f"/root/backups/ai_worker/{bot}_{ts}.tar.gz"

    log(f"START bot={bot} task={task}")
    subprocess.check_call(f"tar -czf {backup} {project}", shell=True)
    log(f"BACKUP_OK {backup}")

    open(os.path.join(project,"AUTO_UPGRADE_NOTE.txt"),"a").write(f"\n[{datetime.datetime.now()}] {task}\n")

    out=sh(f"{PYTHON} -m py_compile {code_file}")
    if out:
        raise Exception("COMPILE_FAILED "+out[:700])
    log("COMPILE_OK")

    subprocess.check_call(f"systemctl restart {service}", shell=True)
    time.sleep(2)

    status=sh(f"systemctl is-active {service}")
    if status!="active":
        raise Exception(f"SERVICE_NOT_ACTIVE {service}={status}")

    log(f"SERVICE_OK {service}")

log("WORKER_V2_REAL_STARTED")

while True:
    try:
        files=[x for x in os.listdir(QUEUE) if x.endswith(".json")]
        for f in files:
            path=os.path.join(QUEUE,f)
            try:
                process_task(path)
                move(path,DONE)
                log(f"SUCCESS {f}")
            except Exception as e:
                log(f"FAILED {f} ERROR={e}")
                move(path,FAILED)
        time.sleep(5)
    except Exception as e:
        log(f"MAIN_LOOP_ERROR {e}")
        time.sleep(5)
