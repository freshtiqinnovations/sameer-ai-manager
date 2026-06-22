
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
#!/usr/bin/env python3
"""
Chat auto-processor — watches for Sameer AI messages and processes them.
Runs continuously as a systemd service.
"""
import time, json, subprocess, os, sys
sys.path.insert(0, "/root/sameer_ai_manager/openclaw_bridge")
from pathlib import Path
from datetime import datetime, timezone

CHAT_AGENT = "/root/sameer_ai_manager/openclaw_bridge/chat_agent.py"
INBOX = "/root/sameer_ai_manager/openclaw_bridge/tasks_inbox.jsonl"
OUTBOX = "/root/sameer_ai_manager/openclaw_bridge/chat_outbox.jsonl"
DONE = "/root/sameer_ai_manager/openclaw_bridge/tasks_done.jsonl"

def log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    with open("/root/sameer_ai_manager/openclaw_bridge/chat_loop.log", "a") as f:
        f.write(f"[{ts}] {msg}\n")

def send_reply(text, status="done"):
    """Send reply to Sameer AI inbox."""
    entry = {
        "id": f"auto_{int(time.time())}",
        "text": text,
        "status": status,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    }
    with open("/root/sameer_ai_manager/openclaw_bridge/chat_inbox.jsonl", "a") as f:
        f.write(json.dumps(entry) + "\n")
    log(f"Auto-reply: {text[:60]}")

def check_done():
    """Check if tasks in inbox have been processed."""
    p = Path(INBOX)
    if p.exists() and p.stat().st_size > 0:
        return False
    return True

def monitor():
    log("📡 Chat loop started")
    while True:
        try:
            # Process through TRIO ENGINE — Sameer AI ↔ OpenClaw unified
            subprocess.getoutput(f"python3 /root/sameer_ai_manager/openclaw_bridge/trio_engine.py daemon >/dev/null 2>&1 &")
            time.sleep(1)
            
            # Check if inbox is being processed
            if check_done():
                time.sleep(2)
                continue
            
            # Wait for inbox to be processed
            waited = 0
            while not check_done() and waited < 60:
                time.sleep(2)
                waited += 2
            
            # Check done file for results
            p = Path(DONE)
            if p.exists() and p.stat().st_size > 0:
                lines = p.read_text().strip().splitlines()
                if lines:
                    try:
                        last = json.loads(lines[-1])
                        result = last.get("result", {})
                        status = result.get("status", "?")
                        steps = result.get("steps", [])
                        summary = " | ".join(steps[:3])
                        send_reply(f"Done: {status} — {summary[:100]}")
                    except:
                        pass
            
            time.sleep(5)
        except Exception as e:
            log(f"Loop error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    monitor()
