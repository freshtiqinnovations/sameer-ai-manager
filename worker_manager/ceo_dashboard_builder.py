
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
import json,glob,subprocess,os
BASE="/root/sameer_ai_manager"
def build_ceo_dashboard():
 r=json.load(open(BASE+"/worker_manager/state/boss_report.json"))
 lessons=len(glob.glob(BASE+"/ai_brain/lessons/*.txt"))
 workers=len(glob.glob(BASE+"//*worker*.py",recursive=True))
 managers=len(glob.glob(BASE+"//*manager*.py",recursive=True))
 services=subprocess.getoutput("systemctl list-units --type=service --all | grep -E 'sameer|autopilot|freshtiq|salama' | wc -l").strip()
 active=[k for k,v in r.get("services",{}).items() if v=="active"]
 total=int(r.get("deployed",0))+int(r.get("rejected",0))+int(r.get("failed",0))
 good=int(r.get("deployed",0))
 progress=int((good/max(total,1))*100)
 return f"👑 SAMEER AI FACTORY CEO DASHBOARD\n\n📚 Lessons: {lessons}\n🤖 Workers: {workers}\n👨‍💼 Managers: {managers}\n⚙️ Services: {services}\n\n📂 Queue: {r.get('queue',0)}\n⏳ Pending: {r.get('pending',0)}\n🚀 Deployed: {r.get('deployed',0)}\n🛑 Rejected: {r.get('rejected',0)}\n💥 Failed: {r.get('failed',0)}\n\n🟢 Active Core:\n- " + "\n- ".join(active) + f"\n\n📈 Automation Progress: {progress}%\n🎯 Current Phase: Worker factory hardening + dashboard/control panel\n🛠 Remaining: better code generator, approve/reject commands, deploy verification, rollback automation"
if name=="main":
 print(build_ceo_dashboard())
