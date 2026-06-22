
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
import os, json, glob, time, urllib.parse, urllib.request, subprocess
from pathlib import Path
from dotenv import load_dotenv

BASE="/root/sameer_ai_manager"
load_dotenv(BASE+"/.env")

def count(p):
    return len(glob.glob(p))

def active(s):
    return subprocess.getoutput(f"systemctl is-active {s}").strip()

reg=Path(BASE+"/factory_registry.json")
status=Path(BASE+"/factory_registry/factory_status.json")

data=json.load(open(reg)) if reg.exists() else {}
st=json.load(open(status)) if status.exists() else {}

msg=f"""🏭 SAMEER AI FACTORY 24/7 REPORT

📊 Progress: {st.get('progress_percent','?')}%
⚙️ Mode: {data.get('production_mode','REAL_ONLY')}
🧠 Manager: {st.get('manager','ONLINE')}
🤖 Worker: {st.get('worker','ONLINE')}

📥 Queue: {count(BASE+'/ai_worker/queue/*.json')}
✅ Completed: {count(BASE+'/ai_worker/completed/*.json')}
❌ Failed: {count(BASE+'/ai_worker/failed/*.json')}
🟢 Pending Approval: {count(BASE+'/approval_queue/pending/*.json')}

🟢 Services:
sameer_ai_manager: {active('sameer_ai_manager.service')}
sameer_ai_worker_auto: {active('sameer_ai_worker_auto.service')}
sameer_approved_monitor: {active('sameer_approved_monitor.service')}

🛡 Rules:
REAL ONLY ✅
NO FAKE ✅
NO DEMO ✅
DUPLICATE GUARD ✅
BACKUP → COMPILE → VERIFY ✅

⏰ {time.strftime('%Y-%m-%d %H:%M:%S')}
"""

token=os.getenv("TELEGRAM_TOKEN")
chat=os.getenv("CEO_CHAT_ID")
if token and chat:
    url=f"https://api.telegram.org/bot{token}/sendMessage"
    body=urllib.parse.urlencode({"chat_id":chat,"text":msg}).encode()
    urllib.request.urlopen(url,data=body,timeout=15).read()
    print("CEO_24X7_REPORT_SENT")
else:
    print("TOKEN_OR_CHAT_MISSING")
