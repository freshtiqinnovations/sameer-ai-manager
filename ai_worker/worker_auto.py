
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
from dotenv import load_dotenv
load_dotenv('/root/sameer_ai_manager/.env')
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

def ceo_report(bot, task, status):
    try:
        import os, urllib.parse, urllib.request
        token=os.getenv("TELEGRAM_TOKEN")
        chat=os.getenv("CEO_CHAT_ID")
        if not token or not chat:
            return
        msg=f"👑 CEO DEPLOY REPORT\n\nBot: {bot}\nTask: {task}\n\nStatus:\n{status}"
        url=f"https://api.telegram.org/bot{token}/sendMessage"
        data=urllib.parse.urlencode({"chat_id":chat,"text":msg}).encode()
        urllib.request.urlopen(url,data=data,timeout=10).read()
        log("CEO_REPORT_SENT")
    except Exception as e:
        log(f"CEO_REPORT_FAILED {e}")
def process_task(path):
    data=json.load(open(path))
    bot=data.get("bot","").strip()
    task=data.get("task","").strip()
    if not bot or not task: raise Exception("BAD_TASK_JSON")

    details=str(data.get("details","")).strip()
    mode=str(data.get("mode") or "APPROVAL_REQUIRED").strip().upper()
    details_l=details.lower()
    if any(x in details_l for x in ["report only", "no patch", "no queue", "no restart", "plan only", "do not patch"]):
        mode="REPORT_ONLY"
    data["mode"]=mode

    log(f"START bot={bot} task={task} mode={mode}")

    if mode in ["REPORT_ONLY", "PLAN_ONLY", "QUEUE_ONLY"]:
        data["status"]="blocked_by_mode_gate"
        data["result"]="blocked_by_mode_gate"
        data["blocked_reason"]="mode_gate"
        data["blocked_time"]=str(datetime.datetime.now())
        out=os.path.join(DONE, os.path.basename(path))
        open(out,"w").write(json.dumps(data,indent=2))
        if os.path.exists(path): os.remove(path)
        log(f"BLOCKED_BY_MODE_GATE {os.path.basename(path)} mode={mode}")
        return

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
    deploy_cmd=f"{PY} /root/sameer_ai_manager/workers/auto_deploy_worker/auto_deploy_worker.py {shlex.quote(patch_path)}"
    deploy_result=subprocess.getoutput(deploy_cmd).strip()
    log(f"AUTO_DEPLOY_RESULT {deploy_result}")
    ceo_report(bot,task,deploy_result)
    bad = ("NOT_APPROVED" in deploy_result or "SAFE_PATCH_FAILED" in deploy_result or "COMPILE_FAILED" in deploy_result or "Traceback" in deploy_result or "\'ok\': False" in deploy_result or "\"ok\": false" in deploy_result)
    if bad:
        if os.path.exists(path): shutil.move(path, os.path.join(FAILED, os.path.basename(path)))
        log(f"FAILED {os.path.basename(path)} DEPLOY_FAILED")
        return
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
                ceo_report("unknown","unknown","FAILED: "+str(e))
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
