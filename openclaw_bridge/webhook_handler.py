
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
Bridge Webhook Handler
Listens on local TCP socket for Sameer AI Manager task submissions.
Sameer AI sends: echo '{"id":"...","type":"...","description":"...","priority":"P2"}' | nc localhost 18791
"""
import json
import socketserver
import subprocess
import time
from pathlib import Path
from datetime import datetime, timezone

INBOX = "/root/sameer_ai_manager/openclaw_bridge/tasks_inbox.jsonl"
LOG_FILE = "/root/sameer_ai_manager/openclaw_bridge/bridge_webhook.log"
FORT_WORKER = "/root/sameer_ai_manager/openclaw_bridge/fortress_worker.py"

AUTHORIZED_CMDS = {
    "status": 1, "inspect": 1, "plan": 1, "test": 1, "patch": 1, "report": 1
}

def log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {msg}\n")

class BridgeHandler(socketserver.StreamRequestHandler):
    def handle(self):
        try:
            raw = self.rfile.readline().strip().decode()
            if not raw:
                return
            
            task = json.loads(raw)
            
            # Validate
            task_type = task.get("type", "")
            if task_type not in AUTHORIZED_CMDS:
                self.wfile.write(b'{"status":"error","reason":"Unknown type. Allowed: status, inspect, plan, test, patch, report"}\n')
                return
            
            # Add defaults
            if "id" not in task:
                task["id"] = f"webhook_{int(time.time())}"
            if "priority" not in task:
                task["priority"] = "P2"
            if "created_at" not in task:
                task["created_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            if "retries" not in task:
                task["retries"] = 0
            
            # Write to inbox
            with open(INBOX, "a") as f:
                f.write(json.dumps(task) + "\n")
            
            # Immediately process
            subprocess.getoutput(f"python3 {FORT_WORKER} process")
            
            self.wfile.write(json.dumps({"status":"accepted","task_id":task["id"]}).encode() + b"\n")
            log(f"Webhook accepted: {task['id']} ({task['type']}:{task.get('description','?')[:40]})")
            
        except json.JSONDecodeError:
            self.wfile.write(b'{"status":"error","reason":"Invalid JSON"}\n')
        except Exception as e:
            log(f"Webhook error: {e}")
            self.wfile.write(json.dumps({"status":"error","reason":str(e)}).encode() + b"\n")

def main():
    port = 18791
    with socketserver.TCPServer(("127.0.0.1", port), BridgeHandler) as server:
        log(f"Bridge webhook listening on 127.0.0.1:{port}")
        print(f"✅ Bridge webhook on port {port}")
        print(f"   Sameer AI Manager sends:")
        print(f"   echo '<json>' | nc 127.0.0.1 {port}")
        server.serve_forever()

if __name__ == "__main__":
    main()
