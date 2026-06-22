
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
import os, subprocess, shutil, datetime
from pathlib import Path

LOG="/root/sameer_ai_manager/ai_brain/autopilot.log"

def log(x):
    with open(LOG,"a") as f:
        f.write(f"{datetime.datetime.now()} | {x}\n")

def sh(cmd):
    return subprocess.getoutput(cmd)

def disk_used():
    return int(sh("df / | awk 'NR==2 {gsub(\"%\",\"\",$5); print $5}'").strip())

def cleanup():
    log("CLEANUP_START")
    sh("rm -rf /tmp/sameer_voice.* /tmp/sameer_reply.mp3 /tmp/*.ogg /tmp/*.wav /tmp/*.mp3")
    sh("apt clean")
    sh("rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/*")
    sh("journalctl --vacuum-time=12h >/dev/null 2>&1")
    sh("find /root -type d -name '__pycache__' -prune -exec rm -rf {} + 2>/dev/null")
    sh("find /root -type f -name '*.log' -size +5M -delete 2>/dev/null")

    # keep latest 1 auto backup if disk high
    sh("mkdir -p /root/backups/auto")
    sh("find /root/backups/auto -type f -name '*.tar.gz' -printf '%T@ %p\\n' | sort -nr | tail -n +2 | cut -d' ' -f2- | xargs -r rm -f")

    # delete archived old backups
    sh("find /root/backups/archive -type f -name '*.tar.gz' -delete 2>/dev/null")

    log("CLEANUP_DONE " + sh("df -h / | tail -1"))

def restart_failed_services():
    services=[
        "sameer_ai_manager.service",
        "sameer_ai_worker_auto.service",
        "freshtiq_ai_travel_pro.service",
        "restaurant_demo_bot.service",
        "salama_radiator_bot.service",
        "salama_service_bot.service",
        "autopilot_hub_bot.service"
    ]
    for svc in services:
        status=sh(f"systemctl is-active {svc}").strip()
        if status!="active":
            log(f"RESTART {svc} status={status}")
            sh(f"systemctl restart {svc}")

def main():
    used=disk_used()
    log(f"AUTOPILOT_START disk={used}%")

    if used > 85:
        cleanup()

    restart_failed_services()

    used=disk_used()
    if used > 90:
        cleanup()

    log(f"AUTOPILOT_DONE disk={disk_used()}%")

if __name__=="__main__":
    main()
