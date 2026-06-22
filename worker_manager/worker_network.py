
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
import json,subprocess,os,time
BASE="/root/sameer_ai_manager"
REG=BASE+"/worker_factory/registry/workers.json"
STATE=BASE+"/worker_manager/state/worker_network.json"
workers=json.load(open(REG))
services=["sameer_ai_manager.service","sameer_ai_worker_auto.service","sameer_approved_monitor.service","sameer_boss_manager.service","sameer_worker_creator.service","auto_test_worker.service"]
def sh(c): return subprocess.getoutput(c).strip()
net={"time":time.time(),"workers":workers,"services":{s:sh("systemctl is-active "+s) for s in services},"mode":"CONNECTED"}
open(STATE,"w").write(json.dumps(net,indent=2))
print("WORKER_NETWORK_CONNECTED")
print(json.dumps(net["services"],indent=2))
