
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
import glob,os,subprocess,time
STATUS="/root/sameer_ai_manager/ai_worker/current_status.txt"
old=open(STATUS).read() if os.path.exists(STATUS) else "Idle"
stage="Idle"
for line in old.splitlines():
 if line.startswith(("🧠","🛠","🛡","🧪","📩","✅","❌","⚠️")): stage=line; break
bot=""
task=""
for line in old.splitlines():
 if line.startswith("Bot:"): bot=line
 if line.startswith("Task:"): task=line
out=[]
out.append("🤖 Worker: "+subprocess.getoutput("systemctl is-active sameer_ai_worker_auto.service").strip())
out.append("📚 Lessons: "+str(len(glob.glob("/root/sameer_ai_manager/ai_brain/lessons/*.txt"))))
out.append("📂 Queue: "+str(len([x for x in os.listdir("/root/sameer_ai_manager/ai_worker/queue") if x.endswith(".json")])))
out.append("🕒 Updated: "+time.strftime("%Y-%m-%d %H:%M:%S"))
out.append("")
out.append(stage)
if bot: out.append(bot)
if task: out.append(task)
open(STATUS,"w").write("\n".join(out)+"\n")
print("CLEAN_STATUS_READY")
