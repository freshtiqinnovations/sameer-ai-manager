
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
CHAT TO COMMANDS — Sameer AI ka text aata hai → Command Center samajhta hai → Execute karta hai → Reply bhejta hai.
Connects chat_outbox.jsonl → command_center.py → result → chat_inbox.jsonl
"""
import json, sys, subprocess, os
from pathlib import Path
from datetime import datetime, timezone

BRIDGE = Path("/root/sameer_ai_manager/openclaw_bridge")
OUTBOX = BRIDGE / "chat_outbox.jsonl"
INBOX = BRIDGE / "chat_inbox.jsonl"
TASKS = BRIDGE / "tasks_inbox.jsonl"

def log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    with open(BRIDGE / "chat_to_commands.log", "a") as f:
        f.write(f"[{ts}] {msg}\n")
    print(f"[{ts}] {msg}")

def sh(cmd):
    return subprocess.getoutput(cmd).strip()

def send_reply(text):
    """Send reply to Sameer AI inbox."""
    entry = {
        "id": f"cmd_{int(datetime.now().timestamp())}",
        "text": text[:2000],
        "status": "done",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    }
    with open(INBOX, "a") as f:
        f.write(json.dumps(entry) + "\n")

def format_result(result, cmd):
    """Format command result nicely."""
    t = result.get("type", "")
    
    if t == "status":
        return (
            f"📊 **System Status**\n\n"
            f"🤖 Sameer AI: {result.get('sameer_ai', '?')}\n"
            f"⚙️ OpenClaw: {result.get('openclaw', '?')}\n"
            f"💾 Disk: {result.get('disk', '?')}\n"
            f"🧠 RAM: {result.get('ram', '?')}\n"
            f"❌ Failed Services: {result.get('failed_services', '0')}\n"
            f"🛡️ Fortress: {result.get('fortress', '?')}\n"
            f"🚨 Emergency: {result.get('emergency', '?')}\n"
            f"📥 Queue: {result.get('queue', '0')}\n"
            f"🕐 {result.get('timestamp', '?')}"
        )
    
    elif t == "cleanup":
        return f"🧹 **Disk Cleanup Done**\n\nDisk: {result.get('disk', '?')}"
    
    elif t == "restart":
        return f"🔄 **Restart: {result.get('service','?')}**\nResult: {result.get('result','?')}\nStatus: {result.get('status','?')}"
    
    elif t == "services":
        lines = result.get("list", [])
        if lines:
            return f"📋 **Running Services**\n\n" + "\n".join(lines[:25])
        return "No Sameer/OpenClaw services found"
    
    elif t == "backup":
        return f"💾 **Backup Created**\nFile: {result.get('file','?')}\nSize: {result.get('size','?')}"
    
    elif t == "generate_bot":
        return f"🤖 **Bot Generation Queued**\nPrompt: {result.get('prompt','?')}\nCheck inbox for task."
    
    else:
        return f"Command result: {json.dumps(result, indent=2)}"

def process():
    """Read Sameer AI's outbox and process commands."""
    if not OUTBOX.exists() or OUTBOX.stat().st_size == 0:
        return
    
    lines = OUTBOX.read_text().strip().splitlines()
    kept = []
    
    for line in lines:
        if not line.strip():
            continue
        try:
            msg = json.loads(line)
            text = msg.get("text", "")
            msg_id = msg.get("id", "")
            
            log(f"📩 Processing: {text[:60]}")
            
            # Skip weekly reports and auto messages
            if msg.get("type") in ["weekly_report", "emergency"]:
                log("  Skipping auto-message")
                continue
            
            # Run through command center
            from command_center import execute
            result = execute(text)
            
            # Format and send reply
            reply = format_result(result, text)
            send_reply(reply)
            log(f"📨 Reply sent for: {text[:40]}")
            
        except Exception as e:
            log(f"⚠️ Error processing: {e}")
            kept.append(line)
    
    # Clear outbox
    open(OUTBOX, "w").close()

def main():
    process()

if __name__ == "__main__":
    main()
