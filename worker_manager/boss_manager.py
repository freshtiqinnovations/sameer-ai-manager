
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
import os,json,time,subprocess,datetime
BASE="/root/sameer_ai_manager"
LOG=BASE+"/worker_manager/boss_manager.log"
DASH=BASE+"/worker_manager/factory_dashboard.py"
SERVICES=["sameer_ai_manager.service","sameer_ai_worker_auto.service","sameer_approved_monitor.service","autopilot_hub_bot.service","freshtiq_ai_travel_pro.service","salama_radiator_bot.service"]
def sh(c): return subprocess.getoutput(c).strip()
def log(x):
    line=str(datetime.datetime.now())+" | "+str(x)
    print(line)
    open(LOG,"a").write(line+"\n")
def count(p):
    return len([x for x in os.listdir(p) if x.endswith(".json")]) if os.path.isdir(p) else 0
def check():
    report={"time":time.time(),"services":{},"queue":count(BASE+"/ai_worker/queue"),"pending":count(BASE+"/approval_queue/pending"),"approved":count(BASE+"/approval_queue/approved"),"deployed":count(BASE+"/approval_queue/deployed"),"rejected":count(BASE+"/approval_queue/rejected"),"failed":count(BASE+"/ai_worker/failed"),"worker_auto_processes":sh("pgrep -af worker_auto.py | grep -v pgrep | wc -l"),"approved_monitor_processes":sh("pgrep -af approved_monitor.py | grep -v pgrep | wc -l"),"latest_deployed":sh("ls -t "+BASE+"/approval_queue/deployed/*.json 2>/dev/null | head -1"),"recent_deployments":sh("ls -t "+BASE+"/approval_queue/deployed/*.json 2>/dev/null | head -10 | wc -l"),"recent_failures":sh("ls -t "+BASE+"/ai_worker/failed/*.json 2>/dev/null | head -10 | wc -l")}
    for s in SERVICES:
        st=sh("systemctl is-active "+s)
        report["services"][s]=st
        if st!="active":
            log("SERVICE_DOWN "+s+"="+st+" restarting")
            sh("systemctl restart "+s)
            report["services"][s]=sh("systemctl is-active "+s)
    open(BASE+"/worker_manager/state/boss_report.json","w").write(json.dumps(report,indent=2))
    if int(report["worker_auto_processes"])>1: log("DUPLICATE_WORKER_AUTO_DETECTED")
    if int(report["approved_monitor_processes"])>1: log("DUPLICATE_APPROVED_MONITOR_DETECTED")
    if report["queue"]>0: log("QUEUE_PENDING="+str(report["queue"]))
    if report["approved"]>0: log("APPROVALS_PENDING="+str(report["approved"]))
    log("BOSS_CHECK "+json.dumps(report))
while True:
    try: check()
    except Exception as e: log("BOSS_ERROR "+str(e))
    time.sleep(300)
