
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
import sys, os, subprocess, datetime, shutil

bot=sys.argv[1]
task=sys.argv[2]

LOG="/root/sameer_ai_manager/logs/upgrade_worker.log"

def log(x):
    with open(LOG,"a") as f:
        f.write(f"{datetime.datetime.now()} | {x}\n")

paths={
 "freshtiq_ai_travel_pro":"/root/workspaces/customers/freshtiq_ai_travel_pro",
 "salama_service_bot":"/root/workspaces/customers/salama_service_bot",
 "salama_radiator_bot":"/root/workspaces/customers/el_salama_radiator_factory",
 "restaurant_demo_bot":"/root/workspaces/customers/restaurant_demo_bot",
}

path=paths.get(bot)

log(f"START bot={bot} task={task}")

if not path or not os.path.exists(path):
    log(f"ERROR bot path not found: {bot}")
    sys.exit(1)

backup=f"/root/backups/{bot}_auto_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
subprocess.call(f"tar -czf {backup} {path} 2>/dev/null", shell=True)
log(f"BACKUP_OK {backup}")

botfile=f"{path}/bot.py"
if os.path.exists(botfile):
    with open(botfile,"a") as f:
        f.write(f"\n# AUTO_UPGRADE_TASK {datetime.datetime.now()} :: {task}\n")
    log("TASK_MARKED_IN_BOT_FILE")

subprocess.call(f"python3 -m py_compile {botfile}", shell=True)
subprocess.call(f"systemctl restart {bot}.service", shell=True)
status=subprocess.getoutput(f"systemctl is-active {bot}.service")
log(f"FINISH {bot}:{status}")
