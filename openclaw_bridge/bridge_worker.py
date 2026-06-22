
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
OpenClaw Bridge Worker
- Reads tasks_inbox.jsonl
- Checks OpenClaw gateway status
- Routes to local/free workflow
- Updates tasks_done.jsonl and openclaw_status.json
- Never auto-deploys without approval
"""
import json, os, time, subprocess, sys, glob, traceback
from pathlib import Path
from datetime import datetime, timezone

BRIDGE = Path("/root/sameer_ai_manager/openclaw_bridge")
INBOX = BRIDGE / "tasks_inbox.jsonl"
DONE = BRIDGE / "tasks_done.jsonl"
STATUS = BRIDGE / "openclaw_status.json"
WORKSPACE = Path("/root/.openclaw/workspace")
LOG = BRIDGE / "bridge_worker.log"

MAX_RETRIES = 5
STUCK_MINUTES = 30

def log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    with open(LOG, "a") as f:
        f.write(f"[{ts}] {msg}\n")
    print(f"[{ts}] {msg}")

def sh(cmd):
    return subprocess.getoutput(cmd).strip()

def read_status():
    if STATUS.exists():
        return json.loads(STATUS.read_text())
    return {"gateway_pid":None,"gateway_running":False,"bridge_queue_count":0,
            "last_task":None,"last_task_time":None,"failed_task_count":0,
            "last_health_check":None,"working_directory":str(WORKSPACE)}

def write_status(data):
    STATUS.write_text(json.dumps(data, indent=2))

def check_gateway():
    """Check if OpenClaw gateway process is running."""
    out = sh("ps aux | grep 'openclaw.*gateway\|dist/index.js' | grep -v grep")
    if out:
        pid = out.split()[1] if out else None
        return out, pid
    return None, None

def check_openclaw_gateway_api():
    """Try to reach OpenClaw gateway API if available."""
    for port in [18789, 18790, 8080, 3000]:
        r = sh(f"curl -s -o /dev/null -w '%{{http_code}}' --connect-timeout 2 http://127.0.0.1:{port}/health 2>/dev/null || echo 'FAIL'")
        if r not in ("FAIL", "000"):
            return port
    return None

def read_inbox():
    """Read all pending tasks from inbox."""
    if not INBOX.exists() or INBOX.stat().st_size == 0:
        return []
    tasks = []
    with open(INBOX) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    tasks.append(json.loads(line))
                except json.JSONDecodeError:
                    log(f"⚠️ Invalid JSON in inbox: {line[:80]}")
    return tasks

def write_done(task, result):
    """Append completed task to done file."""
    task["completed_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    task["result"] = result
    with open(DONE, "a") as f:
        f.write(json.dumps(task) + "\n")

def clear_inbox():
    """Clear inbox after processing."""
    open(INBOX, "w").close()

def process_task(task):
    """Process a single task. Never auto-deploys."""
    task_id = task.get("id", str(int(time.time())))
    task_type = task.get("type", "unknown")
    description = task.get("description", "")

    log(f"🔄 Processing task {task_id}: {task_type} — {description[:60]}")
    
    result = {"status": "pending", "steps": []}

    if task_type == "inspect":
        # Safe: read-only inspection
        path = task.get("path", "")
        target = Path(path)
        if target.exists():
            if target.is_file():
                size = target.stat().st_size
                result["status"] = "done"
                result["steps"].append(f"File exists: {path} ({size} bytes)")
            else:
                files = [str(f) for f in target.iterdir()][:20]
                result["status"] = "done"
                result["steps"].append(f"Dir exists: {path} ({len(files)} items)")
        else:
            result["status"] = "failed"
            result["steps"].append(f"Path not found: {path}")

    elif task_type == "plan":
        # Safe: just read context and produce a plan
        result["status"] = "done"
        result["steps"].append(f"Plan requested: {description}")
        result["steps"].append("Approval required before execution.")

    elif task_type == "patch":
        # Requires explicit approval — just report what would happen
        result["status"] = "pending_approval"
        result["steps"].append(f"Patch requested: {description}")
        result["steps"].append("⚠️ PATCH REQUIRES APPROVAL. Not auto-executed.")

    elif task_type == "generate_bot":
        if task.get("approved"):
            import re
            outdir = BRIDGE / "generated_artifacts"
            outdir.mkdir(exist_ok=True)
            prompt = task.get("prompt","bot").strip() or "bot"
            safe = re.sub(r"[^a-zA-Z0-9_]+","_",prompt.lower()).strip("_")[:40] or "bot"
            botfile = outdir / f"bot_{safe}_{int(time.time())}.py"
            botfile.write_text("#!/usr/bin/env python3\\nimport time\\nprint('BOT_READY: "+prompt.replace("'","")+"')\\nwhile True:\\n    time.sleep(60)\\n")
            botfile.chmod(0o755)
            result["status"] = "done"
            result["steps"].append(f"Approved bot artifact generated: {botfile}")
            result["steps"].append("Safe draft created. Auto deploy next phase.")
        else:
            result["status"] = "pending_approval"
            result["steps"].append(f"Bot requested: {task.get('prompt','')}")
            result["steps"].append("Approval required before execution.")

    elif task_type == "generate_website":
        result["status"] = "pending_approval"
        result["steps"].append(f"Website requested: {task.get('prompt','')}")

    elif task_type == "generate_app":
        result["status"] = "pending_approval"
        result["steps"].append(f"App requested: {task.get('prompt','')}")

    elif task_type == "generate_code":
        result["status"] = "pending_approval"
        result["steps"].append(f"Code requested: {task.get('prompt','')}")

    elif task_type == "deploy":
        result["status"] = "pending_approval"
        result["steps"].append(f"Deploy requested: {description}")

    elif task_type == "status":
        status = read_status()
        result["status"] = "done"
        result["steps"].append(f"Gateway PID: {status.get('gateway_pid')}")
        result["steps"].append(f"Queue count: {status.get('bridge_queue_count')}")
        result["steps"].append(f"Last task: {status.get('last_task')}")

    elif task_type == "test":
        cmd = task.get("command", "")
        if any(x in cmd for x in ["rm", "del", ">", "|", "sudo", "dd", "mkfs"]):
            result["status"] = "rejected"
            result["steps"].append(f"⚠️ Dangerous command rejected: {cmd[:50]}")
        else:
            out = sh(cmd)[:500]
            result["status"] = "done"
            result["steps"].append(f"Command: {cmd}")
            result["steps"].append(f"Output: {out[:200]}")

    else:
        result["status"] = "unknown_type"
        result["steps"].append(f"No handler for task type: {task_type}")

    return result

def run_bridge_cycle():
    """Main bridge cycle — runs once."""
    log("🔁 Bridge cycle started")

    # 1. Check gateway
    proc, pid = check_gateway()
    api_port = check_openclaw_gateway_api()
    
    status = read_status()
    status["gateway_pid"] = pid
    status["gateway_running"] = proc is not None
    status["last_health_check"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    status["gateway_api_port"] = api_port

    # 2. Read inbox
    tasks = read_inbox()
    status["bridge_queue_count"] = len(tasks)

    if tasks:
        log(f"📥 {len(tasks)} task(s) in inbox")
        
        # Check for stuck tasks
        for task in tasks:
            task_id = task.get("id", "?")
            task_time = task.get("created_at", "")
            if task_time:
                try:
                    created = datetime.fromisoformat(task_time)
                    if (datetime.now(timezone.utc) - created).total_seconds() > STUCK_MINUTES * 60:
                        result = {"status": "failed_stuck", "steps": [f"Stuck > {STUCK_MINUTES} minutes"]}
                        write_done(task, result)
                        status["failed_task_count"] += 1
                        log(f"⚠️ Task {task_id} marked as STUCK (>{STUCK_MINUTES}min)")
                        continue
                except:
                    pass

        # Process ALL pending tasks
        tasks = read_inbox()  # re-read after removing stuck ones
        for task in tasks:
            task_id = task.get("id", "?")
            retries = task.get("retries", 0)
            
            if retries < MAX_RETRIES:
                result = process_task(task)
                task["retries"] = retries + 1
                
                if result["status"] in ("done", "failed", "rejected", "pending_approval", "unknown_type"):
                    write_done(task, result)
                    status["last_task"] = task.get("description", "?")
                    status["last_task_time"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                    if result["status"] == "failed":
                        status["failed_task_count"] += 1
                    log(f"✅ Task {task_id} completed: {result['status']}")
            else:
                result = {"status": "max_retries", "steps": [f"Exceeded {MAX_RETRIES} retries"]}
                write_done(task, result)
                status["failed_task_count"] += 1
                log(f"❌ Task {task_id} max retries exceeded")

        # Clear processed tasks from inbox
        clear_inbox()

    else:
        log("📭 No pending tasks")

    # 3. Update status
    write_status(status)
    log(f"✅ Bridge cycle done — gateway={'UP' if pid else 'DOWN'} queue={status['bridge_queue_count']}")

def main():
    run_bridge_cycle()

if __name__ == "__main__":
    main()
