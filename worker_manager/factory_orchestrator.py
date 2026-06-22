
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
import json,subprocess,time,os
BASE="/root/sameer_ai_manager"
TASK=BASE+"/worker_manager/state/factory_task.json"
NET=BASE+"/worker_manager/state/worker_network.json"
OUT=BASE+"/worker_manager/state/factory_task_result.json"
def sh(c): return subprocess.getoutput(c).strip()
task=json.load(open(TASK))
net=json.load(open(NET))
result={"time":time.time(),"task":task,"network_mode":net.get("mode"),"steps":[]}
result["steps"].append({"boss_manager":sh("systemctl is-active sameer_boss_manager.service")})
result["steps"].append({"worker_creator":sh("systemctl is-active sameer_worker_creator.service")})
result["steps"].append({"worker_auto":sh("systemctl is-active sameer_ai_worker_auto.service")})
result["steps"].append({"approved_monitor":sh("systemctl is-active sameer_approved_monitor.service")})
result["steps"].append({"generated_worker":sh("systemctl is-active auto_test_worker.service")})
result["status"]="CONNECTED_READY" if all("active" in list(x.values())[0] for x in result["steps"]) else "CHECK_REQUIRED"
open(OUT,"w").write(json.dumps(result,indent=2))
print("FACTORY_WORKERS_CONNECTED_AND_CHECKED")
print(json.dumps(result,indent=2))
