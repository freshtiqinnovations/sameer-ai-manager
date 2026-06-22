
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
UNIFIED COMMAND CENTER — Ek command se saare systems ko control karo.
Sameer AI + OpenClaw + VPS teeno ek saath command maane.
"""
import json, subprocess, sys, os
from pathlib import Path
from datetime import datetime, timezone

BRIDGE = Path("/root/sameer_ai_manager/openclaw_bridge")
CHAT_INBOX = BRIDGE / "chat_inbox.jsonl"
CHAT_OUTBOX = BRIDGE / "chat_outbox.jsonl"
TASKS_INBOX = BRIDGE / "tasks_inbox.jsonl"

def sh(cmd):
    return subprocess.getoutput(cmd).strip()

def log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    with open(BRIDGE / "command_center.log", "a") as f:
        f.write(f"[{ts}] {msg}\n")

def execute(command_text):
    """Parse and execute a command. Returns result dict."""
    t = command_text.lower().strip()
    
    # === SYSTEM COMMANDS ===
    
    # Normalize — remove common suffixes
    for suffix in [" do", " karo", " dekh", " check", " dikha", " dikhao", " bata", " batao", " lo", " abhi"]:
        if t.endswith(suffix) and t != suffix.strip():
            t = t[:-len(suffix)].strip()
            break
    
    # Status / Health
    if t in ["status", "health", "report", "sab thik", "sab thik hai", "full"]:
        return {
            "type": "status",
            "sameer_ai": sh("systemctl is-active sameer_ai_manager.service"),
            "openclaw": sh("ps aux | grep openclaw.*gateway | grep -v grep | awk '{print \"PID \"$2}'") or "Not running",
            "disk": sh("df -h / | awk 'NR==2{print $5, $3\"/\"$2}'"),
            "ram": sh("free -h | awk '/Mem:/{print $3\"/\"$2}'"),
            "failed_services": sh("systemctl list-units --type=service --state=failed --no-pager | awk '/failed/ {count++} END {print count+0}'"),
            "fortress": sh("systemctl is-active openclaw_fortress.service"),
            "emergency": sh("systemctl is-active openclaw_emergency.service"),
            "queue": sh("wc -l < " + str(TASKS_INBOX)) if TASKS_INBOX.exists() else "0",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        }
    
    # Disk cleanup
    if t in ["disk clean", "clean disk", "disk saaf", "space free", "cleanup"]:
        results = []
        results.append(sh("journalctl --vacuum-time=2d 2>/dev/null; echo '✅ Journal cleaned'"))
        results.append(sh("apt clean 2>/dev/null; echo '✅ Apt cache cleaned'"))
        results.append(sh("find /tmp -type f -mtime +2 -delete 2>/dev/null; echo '✅ Old tmp files cleaned'"))
        after = sh("df -h / | awk 'NR==2{print $5, $3\"/\"$2}'")
        results.append(f"Disk now: {after}")
        return {"type": "cleanup", "results": results, "disk": after}
    
    # Restart service
    if t.startswith("restart "):
        service = t.replace("restart ", "").strip()
        result = sh(f"systemctl restart {service}.service 2>&1 || systemctl restart {service} 2>&1")
        new_status = sh(f"systemctl is-active {service}.service 2>/dev/null || systemctl is-active {service} 2>/dev/null || echo 'unknown'")
        return {"type": "restart", "service": service, "result": result, "status": new_status}
    
    # List services
    if t in ["services", "list services", "saare services", "workers"]:
        raw = sh("systemctl list-units --type=service --state=running --no-pager | grep -E 'sameer|openclaw|auto_' | awk '{$2=$3=$4=\"\"; print $0}' | head -30")
        return {"type": "services", "list": raw.strip().splitlines()}
    
    # Backup
    if t in ["backup", "backup abhi", "save now", "bakup lo"]:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        result = sh(f"tar czf /root/backups/quick_backup_{ts}.tar.gz /root/sameer_ai_manager/openclaw_bridge/ 2>/dev/null; echo 'done'")
        size = sh(f"ls -lh /root/backups/quick_backup_{ts}.tar.gz | awk '{{print $5}}'")
        return {"type": "backup", "file": f"quick_backup_{ts}.tar.gz", "size": size, "result": result}
    
    # === BOT COMMANDS ===
    
    if t.startswith("bot banao") or t.startswith("bot ban") or t.startswith("make bot"):
        name = t.replace("bot banao", "").replace("bot ban", "").replace("make bot", "").strip()
        return {
            "type": "generate_bot",
            "prompt": name or "default_support_bot",
            "message": f"Bot generation queued for: {name or 'support bot'}"
        }
    
    # === UNKNOWN ===
    return {
        "type": "unknown",
        "message": f"Command not recognized: {command_text}:)",
        "available": "status, health, disk clean, restart <service>, services, backup, bot banao <description>"
    }

def main():
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        result = execute(text)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("Usage: command_center.py <command>")
        print("Commands: status, health, disk clean, restart <service>, services, backup, bot banao <desc>")

if __name__ == "__main__":
    main()
