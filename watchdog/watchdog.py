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
import time, subprocess, json, os

SERVICES = [
    "sameer_ai_manager.service",
    "freshtiq_ai_travel_pro.service",
    "salama_service_bot.service",
    "salama_radiator_bot.service",
    "restaurant_demo_bot.service",
]

COOLDOWN_FILE = "/tmp/watchdog_cooldown.json"
CONSECUTIVE_FILE = "/tmp/watchdog_consecutive.json"
LOG = "/root/sameer_ai_manager/logs/watchdog.log"

def log(msg):
    t = str(__import__('datetime').datetime.now())
    with open(LOG, "a") as f:
        f.write(f"{t} | {msg}\n")

def load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f)

while True:
    now = time.time()
    for service in SERVICES:
        try:
            status = subprocess.getoutput(f"systemctl is-active {service}").strip()

            if status in ["active", "activating"]:
                log(f"HEALTHY {service} -- no action")
                continue

            # Cooldown check: only restart every 120s minimum
            cooldowns = load_json(COOLDOWN_FILE, {})
            consecutive = load_json(CONSECUTIVE_FILE, {})

            last = cooldowns.get(service, 0)
            if now - last < 120:
                log(f"SKIP {service} -- cooldown active ({120-(now-last):.0f}s left), status={status}")
                continue

            # Consecutive check: need 2
            fail_count = consecutive.get(service, 0) + 1
            consecutive[service] = fail_count
            save_json(CONSECUTIVE_FILE, consecutive)

            if fail_count < 2:
                log(f"WARN {service} -- 1st consecutive, waiting, status={status}")
                continue

            # Confirmed: restart
            log(f"RESTART {service} -- consecutive={fail_count}, status={status}")
            subprocess.call(f"systemctl restart {service}", shell=True)

            cooldowns[service] = time.time()
            save_json(COOLDOWN_FILE, cooldowns)

            # Check result
            time.sleep(3)
            new_status = subprocess.getoutput(f"systemctl is-active {service}").strip()
            log(f"RESULT {service} => {new_status}")

        except Exception as e:
            log(f"ERROR {service}: {e}")

    time.sleep(60)
