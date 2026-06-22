
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
import os, time, json, subprocess, datetime

ROOT="/root/sameer_ai_manager"
LOG=f"{ROOT}/logs/auto_master.log"
REG=f"{ROOT}/bot_registry.json"
BACK="/root/backups"

os.makedirs(f"{ROOT}/logs", exist_ok=True)
os.makedirs(BACK, exist_ok=True)

def sh(cmd):
    return subprocess.getoutput(cmd)

def log(x):
    msg=f"{datetime.datetime.now()} | {x}"
    print(msg, flush=True)
    with open(LOG,"a") as f:
        f.write(msg+"\n")

def backup():
    name=f"{BACK}/sameer_auto_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
    sh(f"tar --exclude='{BACK}' -czf {name} {ROOT} /etc/systemd/system 2>/dev/null")
    log(f"BACKUP_OK {name}")

def scan_services():
    raw=sh("systemctl list-units --type=service --all --no-pager | awk '{print $1}' | grep -E 'sameer|freshtiq|salama|restaurant|bot' || true")
    services=[]
    for x in raw.splitlines():
        x=x.strip().replace(".service","")
        if x and x not in services:
            services.append(x)
    json.dump([{"service":s} for s in services], open(REG,"w"), indent=2)
    log(f"SCAN_OK {len(services)} services")
    return services

def repair(service):
    status=sh(f"systemctl is-active {service}.service").strip()
    log(f"{service}:{status}")
    if status!="active":
        log(f"REPAIR_START {service}")
        sh(f"systemctl restart {service}.service")
        time.sleep(4)
        status2=sh(f"systemctl is-active {service}.service").strip()
        log(f"REPAIR_RESULT {service}:{status2}")
        if status2!="active":
            err=sh(f"journalctl -u {service}.service -n 20 --no-pager")
            log(f"ERROR {service}: {err[-1000:]}")

def main():
    log("AUTO_MASTER_START")
    backup()
    services=scan_services()
    for s in services:
        repair(s)
    log("AUTO_MASTER_DONE")

if __name__=="__main__":
    main()
