
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
import json, subprocess, os
from pathlib import Path
from datetime import datetime

BASE = Path("/root/sameer_ai_manager")
CUSTOMERS = Path("/root/workspaces/customers")
OUT = BASE / "bot_registry.json"

def sh(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return r.stdout.strip()

services = sh("systemctl list-unit-files '*.service' --no-pager | grep -E 'bot|sameer|freshtiq|salama' | awk '{print $1}'").splitlines()

bots = []
for svc in services:
    name = svc.replace(".service", "")
    status = sh(f"systemctl is-active {name}")
    unit = sh(f"systemctl cat {name} 2>/dev/null")
    path = ""
    for line in unit.splitlines():
        if "ExecStart=" in line and ".py" in line:
            path = line.split("ExecStart=",1)[1]
    bots.append({
        "service": name,
        "status": status,
        "exec": path,
        "updated": datetime.now().isoformat()
    })

OUT.write_text(json.dumps({"bots": bots}, indent=2), encoding="utf-8")
print(json.dumps({"count": len(bots), "bots": bots}, indent=2))
