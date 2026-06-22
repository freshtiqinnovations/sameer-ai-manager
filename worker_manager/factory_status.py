
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
import json,subprocess,os

def sh(c): return subprocess.getoutput(c).strip()

def status():
 services=["sameer_ai_manager.service","sameer_ai_worker_auto.service","autopilot_hub_bot.service","freshtiq_ai_travel_pro.service","salama_radiator_bot.service"]
 data={"services":{},"pending_approvals":len([x for x in os.listdir("/root/sameer_ai_manager/approval_queue/pending") if x.endswith(".json")]),"queue":len([x for x in os.listdir("/root/sameer_ai_manager/ai_worker/queue") if x.endswith(".json")])}
 for s in services:
  data["services"][s]=sh("systemctl is-active "+s)
 return data

print(json.dumps(status(),indent=2))
