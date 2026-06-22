
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
Multi-Project Tracker — handles N projects simultaneously.
Each project has its own path, status, backup, notifications.
"""
import json, subprocess, time
from pathlib import Path
from datetime import datetime, timezone

PROJECTS_FILE = Path("/root/sameer_ai_manager/openclaw_bridge/projects.json")
LOG_FILE = Path("/root/sameer_ai_manager/openclaw_bridge/projects.log")

DEFAULT_PROJECTS = {
    "freshtiq_android": {
        "path": "/root/workspaces/customers/freshtiq_android_app/app",
        "type": "flutter",
        "status": "deployed",
        "version": "2.7.3",
        "backup_path": "/root/backups",
        "last_build": "2026-06-06",
        "notifications": True,
        "notes": "Google Play Store production"
    },
    "freshtiq_web": {
        "path": "/tmp/freshtiq_web",
        "type": "web",
        "status": "staging",
        "version": "1.0.0",
        "backup_path": "/root/backups",
        "last_build": "2026-06-05",
        "notifications": False,
        "notes": "Website demo"
    },
    "sameer_ai_manager": {
        "path": "/root/sameer_ai_manager",
        "type": "python",
        "status": "running",
        "version": "latest",
        "backup_path": "/root/backups",
        "last_build": "daily",
        "notifications": True,
        "notes": "Master controller"
    }
}

def log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {msg}\n")

def sh(cmd):
    return subprocess.getoutput(cmd).strip()

def load():
    if PROJECTS_FILE.exists():
        return json.loads(PROJECTS_FILE.read_text())
    return DEFAULT_PROJECTS

def save(projects):
    PROJECTS_FILE.write_text(json.dumps(projects, indent=2))

def check_project(project):
    """Check if a project is healthy."""
    result = {"name": project, "checks": []}
    data = DEFAULT_PROJECTS.get(project, {})
    path = data.get("path", "")
    
    if not path or not Path(path).exists():
        result["status"] = "missing"
        result["checks"].append(f"Path not found: {path}")
        return result
    
    # Check disk space
    disk = int(sh(f"df {path} | awk 'NR==2 {{gsub(/%/,\"\",$5); print $5}}'") or "0")
    result["checks"].append(f"Disk: {disk}%")
    
    # Check git
    if Path(f"{path}/.git").exists():
        branch = sh(f"cd {path} && git branch --show-current 2>/dev/null || echo '?'")
        dirty = sh(f"cd {path} && git status --porcelain 2>/dev/null | wc -l")
        result["checks"].append(f"Git: {branch} ({dirty} dirty)")
    
    # Check backups
    bpath = data.get("backup_path", "/root/backups")
    if Path(bpath).exists():
        bsize = sh(f"du -sh {bpath} 2>/dev/null | awk '{{print $1}}'")
        result["checks"].append(f"Backup: {bsize}")
    
    result["status"] = "healthy"
    return result

def status_all():
    """Get status of all projects."""
    projects = load()
    results = []
    for name in projects:
        r = check_project(name)
        results.append(r)
    return results

def main():
    action = "status"
    if len(subprocess.getoutput("ls /root/workspaces/customers/ 2>/dev/null || true").splitlines()) > 3:
        # Auto-detect more projects
        pass
    
    projects = load()
    
    if not PROJECTS_FILE.exists():
        save(projects)
        log(f"Created default projects config ({len(projects)} projects)")
    
    # Update statuses
    all_ok = True
    for name, data in projects.items():
        r = check_project(name)
        if r["status"] != "healthy":
            all_ok = False
            log(f"⚠️ {name}: {r['status']} — {'; '.join(r['checks'][:2])}")
        else:
            log(f"✅ {name}: {r['status']} — {'; '.join(r['checks'][:2])}")
    
    report = []
    report.append(f"# Multi-Project Status — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    report.append("")
    for name, data in projects.items():
        r = check_project(name)
        report.append(f"## {name} ({data.get('type','?')})")
        report.append(f"- Path: {data.get('path','?')}")
        report.append(f"- Status: {r['status']}")
        report.append(f"- Version: {data.get('version','?')}")
        for c in r["checks"]:
            report.append(f"- {c}")
        report.append("")
    
    report_path = Path("/root/sameer_ai_manager/openclaw_bridge/projects_report.md")
    report_path.write_text("\n".join(report))
    print(f"✅ Report saved: {report_path}")

if __name__ == "__main__":
    main()
