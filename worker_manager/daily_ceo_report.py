
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
import os,json,datetime,subprocess
BASE="/root/sameer_ai_manager"
def count(p):
    return len([x for x in os.listdir(p) if x.endswith(".json")]) if os.path.isdir(p) else 0
def sh(c): return subprocess.getoutput(c).strip()
services=["sameer_ai_manager.service","sameer_ai_worker_auto.service","sameer_approved_monitor.service","sameer_boss_manager.service","autopilot_hub_bot.service","freshtiq_ai_travel_pro.service","salama_radiator_bot.service"]
print("📊 DAILY CEO REPORT")
print("Date:",datetime.datetime.now())
print("Queue:",count(BASE+"/ai_worker/queue"))
print("Pending:",count(BASE+"/approval_queue/pending"))
print("Approved:",count(BASE+"/approval_queue/approved"))
print("Deployed:",count(BASE+"/approval_queue/deployed"))
print("Rejected:",count(BASE+"/approval_queue/rejected"))
print("\nServices:")
for s in services:
    print(s, sh("systemctl is-active "+s))
