
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
UPGRADE 8: Two-Way Chat — Sameer AI ↔ OpenClaw Direct Communication

How it works:
- Sameer AI writes to bridge/chat_outbox.jsonl
- OpenClaw reads it, processes, writes reply to bridge/chat_inbox.jsonl
- Both can talk back and forth like a team
"""
import json, time, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone

BRIDGE = Path("/root/sameer_ai_manager/openclaw_bridge")
OUTBOX = BRIDGE / "chat_outbox.jsonl"
INBOX = BRIDGE / "chat_inbox.jsonl"
CHAT_LOG = BRIDGE / "chat_log.jsonl"
INBOX_FILE = BRIDGE / "tasks_inbox.jsonl"
FORT_WORKER = BRIDGE / "fortress_worker.py"
BRIDGE_WORKER = BRIDGE / "bridge_worker.py"

def log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{ts}] {msg}")

def sh(cmd):
    return subprocess.getoutput(cmd).strip()

def get_last_inbox_task():
    """Get last task from done file for context."""
    done_file = BRIDGE / "tasks_done.jsonl"
    if done_file.exists() and done_file.stat().st_size > 0:
        lines = done_file.read_text().strip().splitlines()
        if lines:
            try:
                return json.loads(lines[-1])
            except:
                pass
    return None

def process_chat():
    """Read Sameer AI messages and reply."""
    if not OUTBOX.exists() or OUTBOX.stat().st_size == 0:
        return

    lines = OUTBOX.read_text().strip().splitlines()
    kept = []
    replies = []

    for line in lines:
        if not line.strip():
            continue
        try:
            msg = json.loads(line)
            msg_id = msg.get("id", str(int(time.time())))
            text = msg.get("text", "")
            priority = msg.get("priority", "P2")
            
            log(f"📩 Sameer AI: {text[:80]}")
            
            # Parse intent and create task
            task = parse_intent(text, msg_id)
            
            if task:
                # Write to inbox with priority
                task["priority"] = priority
                task["created_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                task["source"] = "chat"
                
                with open(INBOX_FILE, "a") as f:
                    f.write(json.dumps(task) + "\n")
                
                # Run fortress + bridge immediately
                sh(f"python3 {FORT_WORKER} process")
                
                reply = {
                    "id": f"reply_{msg_id}",
                    "in_reply_to": msg_id,
                    "text": f"✅ Task created: {task.get('type','?')} — {task.get('description','?')}",
                    "status": "processed",
                    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                }
            else:
                reply = {
                    "id": f"reply_{msg_id}",
                    "in_reply_to": msg_id,
                    "text": f"❌ Samajh nahi paya: {text[:60]}... P2 ki tarah likho: 'disk check karo', 'backup lo', 'status do'",
                    "status": "failed",
                    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                }
            
            replies.append(reply)
            
            # Log to chat history
            chat_entry = {"msg": msg, "reply": reply, "timestamp": reply["timestamp"]}
            with open(CHAT_LOG, "a") as f:
                f.write(json.dumps(chat_entry) + "\n")
                
        except Exception as e:
            log(f"⚠️ Chat error: {e}")
            kept.append(line)

    # Write replies
    if replies:
        with open(INBOX, "a") as f:
            for r in replies:
                f.write(json.dumps(r) + "\n")
        log(f"📨 {len(replies)} reply/replies sent to Sameer AI")

    # Clear outbox
    open(OUTBOX, "w").close()

def parse_intent(text, msg_id):
    """Smart delegation — convert natural language to task."""
    t = text.lower().strip()
    
    # Disk / storage
    if any(w in t for w in ["disk", "storage", "space", "memory"]):
        if any(w in t for w in ["check", "status", "show", "kitna", "kya"]):
            return {"id": msg_id, "type": "test", "description": f"Check disk usage: {text}", 
                    "command": "df -h / && du -sh /root/backups/"}
        if any(w in t for w in ["clean", "free", "saaf", "delete"]):
            return {"id": msg_id, "type": "test", "description": f"Clean disk: {text}",
                    "command": "df -h /"}
    
    # Backup
    if any(w in t for w in ["backup", "bakup"]):
        return {"id": msg_id, "type": "test", "description": f"Check backup status: {text}",
                "command": "du -sh /root/backups/ && ls -t /root/backups/ | head -5"}
    
    # Status / Health
    if any(w in t for w in ["status", "health", "sab thik", "kya haal", "report"]):
        return {"id": msg_id, "type": "test", "description": f"Full health check: {text}",
                "command": "uptime && free -h && df -h / && systemctl list-units --state=failed --no-pager"}
    
    # Service check
    if any(w in t for w in ["service", "worker", "bot"]):
        return {"id": msg_id, "type": "test", "description": f"Check services: {text}",
                "command": "systemctl list-units --type=service --state=running --no-pager | head -20"}
    
    # Security
    if any(w in t for w in ["security", "fortress", "safety", "attack"]):
        return {"id": msg_id, "type": "test", "description": f"Security check: {text}",
                "command": "cat /root/sameer_ai_manager/openclaw_bridge/security.log | tail -10"}
    
    # Inspect path
    if any(w in t for w in ["inspect", "check", "dikh", "dikhao"]):
        # Extract potential path
        words = text.split()
        for w in words:
            if w.startswith("/"):
                return {"id": msg_id, "type": "inspect", "description": f"Inspect: {w}", "path": w}
    
    # Unknown — return None for basic reply
    return None

def main():
    process_chat()

if __name__ == "__main__":
    main()
