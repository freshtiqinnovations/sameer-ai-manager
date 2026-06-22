
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
import os, json, time, subprocess
from dotenv import load_dotenv

load_dotenv("/root/sameer_ai_manager/.env")

REGISTRY = "/root/sameer_ai_manager/bot_registry.json"

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

def sh(cmd, timeout=60):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return r.returncode, (r.stdout + r.stderr).strip()

def alert(msg):
    if BOT_TOKEN and ADMIN_ID:
        subprocess.run(
            f'curl -s -X POST https://api.telegram.org/bot{BOT_TOKEN}/sendMessage '
            f'-d chat_id={ADMIN_ID} --data-urlencode text="{msg}"',
            shell=True,
            capture_output=True,
            text=True,
            timeout=20
        )

print("AUTONOMOUS AI MODE ACTIVE", flush=True)

while True:

    try:
        with open(REGISTRY, "r") as f:
            data = json.load(f)

        bots = data.get("bots", []) if isinstance(data, dict) else data if isinstance(data, list) else []

        print("SCAN START", flush=True)

        for bot in bots:

            service = bot.get("service")
            if not service:
                continue

            if service == "sameer_ai_manager":
                continue

            code, status = sh(f"systemctl is-active {service}")

            print(f"{service}:{status}", flush=True)

            if status != "active":

                alert(f"⚠️ BOT DOWN: {service}\nAttempting autonomous recovery.")

                print(f"RECOVERING {service}", flush=True)

                sh(f"systemctl restart {service}", timeout=90)

                time.sleep(8)

                code2, status2 = sh(f"systemctl is-active {service}")

                if status2 == "active":

                    alert(f"✅ RECOVERED: {service}")

                    print(f"{service}:recovered", flush=True)

                else:

                    logs = sh(
                        f"journalctl -u {service} -n 40 --no-pager",
                        timeout=60
                    )[1][-3000:]

                    alert(
                        f"❌ FAILED RECOVERY: {service}\n\n{logs}"
                    )

                    print(f"{service}:failed", flush=True)

    except Exception as e:

        print(str(e), flush=True)

    time.sleep(60)
