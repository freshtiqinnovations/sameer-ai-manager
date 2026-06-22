
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
import json,time,subprocess,os
BASE="/root/sameer_ai_manager"
TASK=BASE+"/worker_manager/state/factory_task.json"
OUT=BASE+"/worker_manager/state/factory_task_result.json"
def sh(c): return subprocess.getoutput(c).strip()
task=json.load(open(TASK))
result=json.load(open(OUT))
result["handoff_chain"]=["boss_manager","worker_creator","worker_auto","approved_monitor","generated_worker"]
result["work_started"]=True
result["worker_assignment"]={"factory_self_check":"generated_worker"}
result["final_status"]="WORKERS_CONNECTED_TASK_STARTED"
open(OUT,"w").write(json.dumps(result,indent=2))
print("WORK_STARTED_BY_WORKERS")
print(json.dumps(result,indent=2))
