
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
import os,time,datetime,subprocess

LOG="/root/sameer_ai_manager/reports/brain_loop.log"

def sh(x):
    return subprocess.getoutput(x)

def log(x):
    with open(LOG,"a") as f:
        f.write(f"{datetime.datetime.now()} | {x}\n")

while True:

    disk=sh("df -h / | tail -1")
    ram=sh("free -h")
    failed=sh("systemctl --failed --no-pager")

    report=f"""
SYSTEM REPORT

DISK:
{disk}

RAM:
{ram}

FAILED:
{failed}
"""

    log(report)

    # AUTO HEAL
    services=[
        "sameer_ai_manager.service",
        "sameer_ai_worker_auto.service",
        "freshtiq_ai_travel_pro.service"
    ]

    for svc in services:
        state=sh(f"systemctl is-active {svc}")

        if "inactive" in state or "failed" in state:
            sh(f"systemctl restart {svc}")
            log(f"RESTARTED {svc}")

    # EXTREME CLEANUP IF DISK HIGH
    used=sh("df / | awk 'NR==2 {gsub(\"%\",\"\",$5); print $5}'")

    try:
        used=int(used)
    except:
        used=0

    if used > 80:
        sh("find /tmp -type f -delete")
        sh("journalctl --vacuum-time=1d >/dev/null 2>&1")
        sh("find /root -type f -name '*.log' -size +20M -delete")
        log("EXTREME CLEANUP RUN")

    time.sleep(300)
