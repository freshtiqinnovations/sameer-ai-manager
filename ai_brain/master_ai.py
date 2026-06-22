
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
import os
import subprocess
import time
from datetime import datetime

SERVICES = [
    "sameer_ai_manager.service",
    "freshtiq_ai_travel_pro.service",
    "salama_service_bot.service",
    "salama_radiator_bot.service",
    "restaurant_demo_bot.service"
]

LOG="/root/sameer_ai_manager/logs/master_ai.log"

def log(msg):
    with open(LOG,"a") as f:
        f.write(f"{datetime.now()} | {msg}\n")

while True:

    log("AI_SCAN_START")

    for service in SERVICES:

        status = subprocess.getoutput(
            f"systemctl is-active {service}"
        ).strip()

        log(f"{service}:{status}")

        if status != "active":

            log(f"REPAIRING:{service}")

            subprocess.call(
                f"systemctl restart {service}",
                shell=True
            )

            time.sleep(5)

            check = subprocess.getoutput(
                f"systemctl is-active {service}"
            ).strip()

            log(f"RESULT:{service}:{check}")

    cpu = subprocess.getoutput(
        "top -bn1 | grep Cpu"
    )

    ram = subprocess.getoutput(
        "free -m"
    )

    disk = subprocess.getoutput(
        "df -h /"
    )

    with open("/root/sameer_ai_manager/logs/server_health.log","a") as f:
        f.write(f"\n{datetime.now()}\n")
        f.write(cpu + "\n")
        f.write(ram + "\n")
        f.write(disk + "\n")

    log("AI_SCAN_DONE")

    time.sleep(120)
