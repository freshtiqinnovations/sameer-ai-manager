#!/usr/bin/env python3
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

import os, subprocess, datetime, json, time

# ─── PHASE 6 FIX: Cooldown + Consecutive Check Guard ───

SERVICES = [
    "sameer_ai_manager.service",
    "sameer_ai_worker_auto.service",
    "sameer_approved_monitor.service",
    "sameer_boss_manager.service",
    "sameer_master_ai.service",          # ADDED: cross-protect
    "sameer_watchdog.service",           # ADDED: cross-protect
    "sameer_auto_heal.service",          # ADDED: cross-protect (self-heal for auto-heal itself)
    "sameer_repair_engine.service",      # ADDED: cross-protect
    "freshtiq_ai_travel_pro.service",
    "restaurant_demo_bot.service",
    "salama_radiator_bot.service",
    "salama_service_bot.service",
    "autopilot_hub_bot.service"
]

LOG="/root/sameer_ai_manager/logs/auto_heal.log"
COOLDOWN_FILE="/tmp/auto_heal_cooldown.json"
CONSECUTIVE_FAIL_FILE="/tmp/auto_heal_consecutive.json"

def log(msg):
    t=str(datetime.datetime.now())
    with open(LOG,"a") as f:
        f.write(f"{t} | {msg}\n")
    print(f"{t} | {msg}")

def load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return default

def save_json(path, data):
    with open(path,"w") as f:
        json.dump(data, f)

while True:
    now = datetime.datetime.now().timestamp()

    for s in SERVICES:
        try:
            status=subprocess.getoutput(f"systemctl is-active {s}").strip()

            if status == "active":
                log(f"HEALTHY {s} -- no restart needed")
                continue

            cooldowns = load_json(COOLDOWN_FILE, {})
            consecutive = load_json(CONSECUTIVE_FAIL_FILE, {})

            last_restart = cooldowns.get(s, 0)
            if now - last_restart < 120:
                rem = 120 - (now - last_restart)
                log(f"SKIP {s} -- cooldown active ({rem:.0f}s remaining), status={status}")
                continue

            fail_count = consecutive.get(s, 0) + 1
            consecutive[s] = fail_count
            save_json(CONSECUTIVE_FAIL_FILE, consecutive)

            if fail_count < 2:
                log(f"WARN {s} -- 1st consecutive inactive ({status}), waiting for 2nd check")
                continue

            detail = subprocess.getoutput(f"systemctl status {s} --no-pager -n 3")
            log(f"CONFIRMED_FAIL {s} -- consecutive={fail_count}, status={status}, detail={detail[:200]}")

            log(f"REPAIR_START {s}")
            subprocess.getoutput(f"systemctl restart {s}")
            time.sleep(5)

            newstatus=subprocess.getoutput(f"systemctl is-active {s}").strip()
            log(f"REPAIR_RESULT {s} => {newstatus}")

            if newstatus == "active":
                consecutive[s] = 0
                save_json(CONSECUTIVE_FAIL_FILE, consecutive)

            cooldowns[s] = datetime.datetime.now().timestamp()
            save_json(COOLDOWN_FILE, cooldowns)

        except Exception as e:
            log(f"ERROR {s} => {e}")

    time.sleep(60)
