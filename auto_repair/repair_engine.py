
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
import subprocess
import time
from datetime import datetime

SERVICES = [
    "sameer_ai_manager.service",
    "freshtiq_ai_travel_pro.service",
    "salama_service_bot.service",
]

while True:
    for service in SERVICES:
        status = subprocess.getoutput(
            f"systemctl is-active {service}"
        ).strip()

        if status != "active":
            subprocess.call(
                f"systemctl restart {service}",
                shell=True
            )

            with open(
                "/root/sameer_ai_manager/logs/repair.log",
                "a"
            ) as f:
                f.write(
                    f"{datetime.now()} REPAIRED {service}\n"
                )

    time.sleep(120)
