
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
import os,json,time,shutil,datetime,subprocess,shlex,sys
sys.path.append("/root/sameer_ai_manager")
from ai_brain.patch_engine import dry_run
from worker_manager.approval_reporter import create_report
QUEUE="/root/sameer_ai_manager/ai_worker/queue"
DONE="/root/sameer_ai_manager/ai_worker/completed"
FAILED="/root/sameer_ai_manager/ai_worker/failed"
LOG="/root/sameer_ai_manager/ai_worker/logs/worker_auto.log"
PLAN_RUNNER="/root/sameer_ai_manager/ai_worker/plan_runner.py"
PATCH_GENERATOR="/root/sameer_ai_manager/workers/patch_generator/patch_generator.py"
QUALITY_CHECKER="/root/sameer_ai_manager/workers/patch_generator/patch_quality_checker.py"
PY="/root/sameer_ai_manager/venv/bin/python"
for d in [QUEUE,DONE,FAILED,os.path.dirname(LOG)]: os.makedirs(d,exist_ok=True)
def log(x):
    line=f"{datetime.datetime.now()} | {x}"
    print(line)
    open(LOG,"a").write(line+"\n")
def process_task(path):
    data=json.load(open(path)); bot=data.get("bot","").strip(); task=data.get("task","").strip()
    if not bot or not task: raise Exception("BAD_TASK_JSON")
    log(f"START bot={bot} task={task}")
    cmd=f"{PY} {PLAN_RUNNER} {shlex.quote(bot)} {shlex.quote(task)}"
    plan_path=subprocess.getoutput(cmd).strip()
    if not plan_path.startswith("/root/sameer_ai_manager/ai_worker/plans/"): raise Exception("PLAN_FAILED "+plan_path[:500])
    open("/root/sameer_ai_manager/ai_worker/current_status.txt","w").write(f"🧠 AI planning done\nBot: {bot}\nTask: {task}\nPlan: {plan_path}\n"); log(f"AI_PLAN_OK {plan_path}")
    patch_path=subprocess.getoutput(f"{PY} {PATCH_GENERATOR} {shlex.quote(plan_path)}").strip()
    open("/root/sameer_ai_manager/ai_worker/current_status.txt","w").write(f"🛠 Patch generated\nBot: {bot}\nTask: {task}\nPatch: {patch_path}\n"); log(f"PATCH_GENERATOR_OK {patch_path}")
    quality=subprocess.getoutput(f"{PY} {QUALITY_CHECKER} {shlex.quote(patch_path)}").strip()
    log(f"PATCH_QUALITY {quality}")
    dry=dry_run(bot); open("/root/sameer_ai_manager/ai_worker/current_status.txt","w").write(f"🧪 Dry run OK\nBot: {bot}\nTask: {task}\n"); log(f"DRY_RUN_OK {json.dumps(dry)}")
    report=create_report(bot,task,plan_path,dry); log(f"APPROVAL_REPORT_OK {report}")
    if os.path.exists(path): shutil.move(path, os.path.join(DONE, os.path.basename(path)))
    log(f"DONE {os.path.basename(path)}")
log("WORKER_AUTO_STARTED")
while True:
    try:
        for f in [x for x in os.listdir(QUEUE) if x.endswith(".json")]:
            path=os.path.join(QUEUE,f)
            try: process_task(path)
            except Exception as e:
                log(f"FAILED {f} ERROR={e}")
                try:
                    data=json.load(open(path)) if os.path.exists(path) else {}
                    data["status"]="failed"
                    data["error"]=str(e)
                    data["failed_time"]=str(datetime.datetime.now())
                    open(path,"w").write(json.dumps(data,indent=2))
                except Exception as save_err:
                    log(f"FAILED_SAVE_ERROR {f} {save_err}")
                if os.path.exists(path): shutil.move(path, os.path.join(FAILED,f))
        time.sleep(5)
    except Exception as e:
        log(f"MAIN_ERROR {e}"); time.sleep(5)
