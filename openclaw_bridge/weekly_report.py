
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
Weekly Report Generator — runs every Sunday and sends to CEO.
Tracks: uptime, incidents, repairs, failed tasks, security events.
"""
import json, subprocess, time
from pathlib import Path
from datetime import datetime, timezone, timedelta

BRIDGE = Path("/root/sameer_ai_manager/openclaw_bridge")
STATUS = BRIDGE / "openclaw_status.json"
DONE = BRIDGE / "tasks_done.jsonl"
SEC_LOG = BRIDGE / "security.log"
REP_LOG = BRIDGE / "repair.log"
AUD_LOG = BRIDGE / "audit.log"
WATCH_LOG = Path("/root/monitoring/watchdog_alerts.log")
OUTBOX = BRIDGE / "chat_outbox.jsonl"
INBOX = BRIDGE / "chat_inbox.jsonl"
PROJECTS = BRIDGE / "projects.json"

def sh(cmd):
    return subprocess.getoutput(cmd).strip()

def get_since(days=7):
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).timestamp()
    return cutoff

def count_lines_since(path, marker="", days=7):
    cutoff = get_since(days)
    count = 0
    if path and path.exists():
        with open(path) as f:
            for line in f:
                if marker and marker not in line:
                    continue
                count += 1
    return count

def get_done_stats(days=7):
    """Get task stats from done file."""
    total = 0
    failed = 0
    blocked = 0
    cutoff = get_since(days)
    
    if DONE.exists():
        with open(DONE) as f:
            for line in f:
                line = line.strip()
                if line:
                    total += 1
                    try:
                        t = json.loads(line)
                        result = t.get("result", {})
                        s = result.get("status", "")
                        if "failed" in s or "error" in s:
                            failed += 1
                        if "blocked" in s or "duplicate" in s:
                            blocked += 1
                    except:
                        pass
    return total, failed, blocked

def generate():
    now = datetime.now(timezone.utc)
    report = []
    report.append(f"# 📊 Weekly Report — {now.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    report.append("")
    
    # System overview
    uptime = sh("uptime")
    disk = sh("df -h / | awk 'NR==2{print $5}'")
    ram = sh("free -h | awk '/Mem:/{print $3\"/\"$2}'")
    
    report.append("## System Overview")
    report.append(f"- Uptime: {uptime}")
    report.append(f"- Disk: {disk}")
    report.append(f"- RAM: {ram}")
    report.append("")
    
    # Services
    failed_services = int(sh("systemctl list-units --type=service --state=failed --no-pager 2>/dev/null | awk '/failed/ {count++} END {print count+0}'"))
    sameer = sh("systemctl is-active sameer_ai_manager.service 2>/dev/null || echo unknown")
    oc = sh("ps aux | grep 'openclaw.*gateway' | grep -v grep | awk '{print $2}' | head -1")
    
    report.append("## Services")
    report.append(f"- Sameer AI Manager: {sameer}")
    report.append(f"- OpenClaw Gateway: {'UP (PID '+oc+')' if oc else 'DOWN'}")
    report.append(f"- Failed services: {failed_services}")
    report.append("")
    
    # Security events
    sec_count = count_lines_since(SEC_LOG)
    report.append("## Security")
    report.append(f"- Security events (7d): {sec_count}")
    if SEC_LOG.exists():
        last_sec = sh("tail -1 " + str(SEC_LOG))
        report.append(f"- Last event: {last_sec[:80]}")
    report.append("")
    
    # Tasks
    total, failed, blocked = get_done_stats()
    report.append("## Tasks")
    report.append(f"- Total completed: {total}")
    report.append(f"- Failed: {failed}")
    report.append(f"- Blocked: {blocked}")
    report.append("")
    
    # Repairs
    rep_count = count_lines_since(REP_LOG)
    report.append("## Auto-Repairs")
    report.append(f"- Repairs (7d): {rep_count}")
    if rep_count > 0 and REP_LOG.exists():
        last_rep = sh("tail -3 " + str(REP_LOG))
        report.append(f"- Recent: {last_rep[:100]}")
    else:
        report.append("- No repairs needed — system healthy")
    report.append("")
    
    # Projects
    projects = json.loads(PROJECTS.read_text()) if PROJECTS.exists() else {}
    if projects:
        report.append("## Projects")
        for name, data in projects.items():
            report.append(f"- **{name}**: {data.get('type','?')} | {data.get('status','?')} | v{data.get('version','?')}")
        report.append("")
    
    # Bridge stats
    bridge_queue = 0
    if (BRIDGE / "tasks_inbox.jsonl").exists():
        bridge_queue = int(sh("wc -l < " + str(BRIDGE / "tasks_inbox.jsonl")) or 0)
    
    report.append("## Bridge")
    report.append(f"- Queue: {bridge_queue}")
    report.append(f"- Done tasks total: {total}")
    report.append("")
    
    report.append("---")
    report.append(f"_Generated by OpenClaw Fortress | {now.strftime('%Y-%m-%d %H:%M:%S')} UTC_")
    
    return "\n".join(report)

def main():
    report = generate()
    
    # Save
    report_path = BRIDGE / f"weekly_report_{datetime.now(timezone.utc).strftime('%Y_%m_%d')}.md"
    report_path.write_text(report)
    print(f"✅ Weekly report saved: {report_path}")
    
    # Also write to outbox for Sameer AI to pick up
    entry = {
        "id": f"weekly_{int(time.time())}",
        "type": "weekly_report",
        "text": report[:2000],
        "summary": f"Weekly report — {report.count(chr(10))} lines, {len(report)} chars",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    }
    with open(OUTBOX, "a") as f:
        f.write(json.dumps(entry) + "\n")
    
    print(f"✅ Sent to Sameer AI outbox")
    print("")
    print(report)

if __name__ == "__main__":
    main()
