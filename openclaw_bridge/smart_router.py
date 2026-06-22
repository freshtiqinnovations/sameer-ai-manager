#!/usr/bin/env python3
"""
SMART ROUTER — Sameer AI bolta hai → router samajhta hai → sahi ko task deta hai
Understands Hinglish, English, mixed language commands automatically.
"""
import json, sys, re
from pathlib import Path
from datetime import datetime, timezone

BRIDGE = Path("/root/sameer_ai_manager/openclaw_bridge")
INBOX = BRIDGE / "tasks_inbox.jsonl"

def log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    with open(BRIDGE / "router.log", "a") as f:
        f.write(f"[{ts}] {msg}\n")

def parse_command(text):
    """Parse any command — Hinglish, English, mixed — and create task."""
    t = text.lower().strip()
    
    # Bot related
    if re.search(r'bot (banao|ban|make|create|build|generate)', t):
        desc = re.sub(r'bot (banao|ban|make|create|build|generate)\s*', '', text, count=1).strip()
        return {
            "type": "needs_approval_new_bot",
            "description": f"Generate bot: {desc}",
            "prompt": desc,
            "target": "new_bot"
        }
    
    # Website related
    if re.search(r'(website|site|web) (banao|ban|make|create|build|generate)', t):
        desc = re.sub(r'(website|site|web) (banao|ban|make|create|build|generate)\s*', '', text, count=1).strip()
        return {
            "type": "needs_approval_new_website",
            "description": f"Generate website: {desc}",
            "prompt": desc,
            "target": "website"
        }
    
    # Code related
    if re.search(r'code (likh|liquidate|write|generate|make|create)', t):
        desc = re.sub(r'code (likh|write|generate|make|create|liquidate)\s*', '', text, count=1).strip()
        return {
            "type": "generate_code",
            "description": f"Generate code: {desc}",
            "prompt": desc
        }
    
    # App related
    if re.search(r'(app|application|mobile app) (banao|ban|make|create)', t):
        desc = re.sub(r'(app|application|mobile app) (banao|ban|make|create)\s*', '', text, count=1).strip()
        return {
            "type": "needs_approval_new_app",
            "description": f"Generate app: {desc}",
            "prompt": desc
        }
    
    # System tasks
    if re.search(r'(check|status|health|dekh|dikha|dikhao|kitna)', t):
        if re.search(r'(disk|storage|space|memory|hard)', t):
            return {"type": "test", "description": f"Check disk: {text}", "command": "df -h / && du -sh /root/backups/"}
        elif re.search(r'(ram|memory|free)', t):
            return {"type": "test", "description": f"Check RAM: {text}", "command": "free -h && uptime"}
        elif re.search(r'(service|worker|bot|daemon)', t):
            return {"type": "test", "description": f"Check services: {text}", "command": "systemctl list-units --type=service --state=running --no-pager | head -20"}
        else:
            return {"type": "test", "description": f"Full health: {text}", "command": "uptime && free -h && df -h / && systemctl list-units --state=failed --no-pager"}
    
    # Deploy
    if re.search(r'(deploy|publish|live|production|release)', t):
        return {"type": "deploy", "description": f"Deploy: {text}"}
    
    # Backup
    if re.search(r'(backup|bakup|save|bache)', t):
        return {"type": "test", "description": f"Backup check: {text}", "command": "du -sh /root/backups/ && ls -lt /root/backups/ | head -5"}
    
    # Security
    if re.search(r'(security|safety|suraksha|fortress|guard)', t):
        return {"type": "test", "description": f"Security check: {text}", "command": "tail -10 /root/sameer_ai_manager/openclaw_bridge/security.log"}
    
    # Inspect path
    path_match = re.search(r'(/[\w/._-]+)', text)
    if path_match:
        return {"type": "inspect", "description": f"Inspect: {path_match.group(1)}", "path": path_match.group(1)}
    
    # Default: simple status
    return {
        "type": "status",
        "description": f"Default status: {text[:60]}"
    }

def route(text, priority="P2"):
    """Parse and route a command to the right system."""
    task = parse_command(text)
    
    if task is None:
        return {"status": "error", "reason": "Command not understood"}
    
    task["id"] = f"route_{datetime.now(timezone.utc).strftime('%H%M%S')}"
    task["priority"] = priority
    task["created_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    task["source"] = "smart_router"
    task["retries"] = 0
    
    # Write to inbox
    with open(INBOX, "a") as f:
        f.write(json.dumps(task) + "\n")
    
    log(f"✅ Routed: {task['type']}:{task.get('description','')[:50]}")
    
    return {
        "status": "accepted",
        "task": task,
        "message": f"✅ Task created: {task['type']} - {task.get('description','')[:50]}"
    }

def main():
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        result = route(text)
        print(json.dumps(result, indent=2))
    else:
        print("Usage: smart_router.py <command text>")
        print("Example: smart_router.py 'ek support bot banao jo customers se baat kare'")

if __name__ == "__main__":
    main()
