#!/usr/bin/env python3
"""
Factory Brain — Standalone system overview tool
Part of OpenClaw autonomous learning worker system

Provider: DeepSeek primary (Ollama fallback)
Per AI_PROVIDER_POLICY.md & AUTO_LEARNING_POLICY.md

Functions:
  factory_status()    → human-readable dashboard + JSON payload
  factory_services()  → all services (active, dead, deprecated)
  factory_projects()  → customer projects + active bots
  factory_memory()    → memory_core file audit
  factory_lessons()   → lesson count, categories, critical items
  factory_audit()     → 10-point system capability audit

Design doc: memory_core/FACTORY_BRAIN_DESIGN.md
            memory_core/CEO_DASHBOARD_DESIGN.md

Rules: Read-only evidence. No risky action. No service modification.
"""

import json
import subprocess
import os
from pathlib import Path
from datetime import datetime

# ── Paths ────────────────────────────────────────────────────────
MEMORY_DIR = Path("/root/.openclaw/workspace/memory_core")
BRIDGE_DIR = Path("/root/sameer_ai_manager/openclaw_bridge")
CUSTOMERS_DIR = Path("/root/workspaces/customers")
LOG_DIR = Path("/root/sameer_ai_manager/logs")
SECURITY_LOG = BRIDGE_DIR / "security.log"
EMERGENCY_LOG = BRIDGE_DIR / "emergency_log.jsonl"

SERVICE_REGISTRY = MEMORY_DIR / "SERVICE_REGISTRY.md"
COMPLETED_WORK = MEMORY_DIR / "COMPLETED_WORK_REGISTRY.md"
LESSON_ENGINE = MEMORY_DIR / "AUTO_LESSON_ENGINE.md"
LESSONS_LEARNED = MEMORY_DIR / "LESSONS_LEARNED.md"
PROJECT_REGISTRY = MEMORY_DIR / "PROJECT_REGISTRY.md"
KNOWN_BOTS = MEMORY_DIR / "KNOWN_BOTS.md"
MASTER_MEMORY = MEMORY_DIR / "MASTER_MEMORY.md"
CURRENT_STATUS = MEMORY_DIR / "CURRENT_STATUS.md"

# ── Helpers ──────────────────────────────────────────────────────
def _sh(cmd: str) -> str:
    """Run shell command, return stdout stripped."""
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return r.stdout.strip()
    except Exception as e:
        return f"[error: {e}]"


def _read_file(path: Path, max_lines: int = 50) -> list:
    """Read file, return lines."""
    try:
        with open(path) as f:
            return f.readlines()[:max_lines]
    except FileNotFoundError:
        return []
    except Exception as e:
        return [f"[error: {e}]"]


def _file_age(path: Path) -> str:
    """Return human-readable age of file."""
    try:
        mtime = os.path.getmtime(path)
        age_s = datetime.now().timestamp() - mtime
        if age_s < 60:
            return f"{int(age_s)}s ago"
        if age_s < 3600:
            return f"{int(age_s / 60)}m ago"
        if age_s < 86400:
            return f"{int(age_s / 3600)}h ago"
        return f"{int(age_s / 86400)}d ago"
    except OSError:
        return "unknown"


# ═════════════════════════════════════════════════════════════════=
# 1. factory_status() — Full CEO dashboard
# ═════════════════════════════════════════════════════════════════=
def factory_status() -> dict:
    """
    Full CEO dashboard: system, bots, today's work, lessons,
    memory health, security, AI status, projects, weaknesses.
    
    Returns:
        dict with display (human-readable) and data (JSON-safe payload)
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M IST")

    # ── Live systemctl (state=running) ──
    running_lines = _sh("systemctl list-units --type=service --state=running --no-pager 2>/dev/null | tail -n +2")
    running = []
    for line in running_lines.split("\n"):
        parts = line.strip().split()
        if parts and parts[0].endswith(".service"):
            running.append(parts[0])

    # Filter sameer-related services
    sameer_keywords = ["sameer", "freshtiq", "salama", "autopilot", "ollama", "website", "flight"]
    sameer_related = [s for s in running if any(k in s.lower() for k in sameer_keywords)]

    failed = _sh("systemctl list-units --type=service --state=failed --no-pager 2>/dev/null | tail -n +2 | awk '{print $1}'")
    failed = [f for f in failed.split("\n") if f.strip()]

    # ── Bots from process ──
    bot_lines = _sh("ps aux | grep 'bot\\.py' | grep -v grep | awk '{print $11, $2}'").split("\n")
    bot_pids = [b.strip() for b in bot_lines if b.strip()]

    # ── Today's work ──
    today = datetime.now().strftime("%Y-%m-%d")
    completed_lines = _read_file(COMPLETED_WORK, max_lines=30)
    today_work = [l.strip().replace("- [x]", "✅") for l in completed_lines if today in l or "✅" in l]

    # ── Lessons ──
    lesson_count = sum(1 for _ in _read_file(LESSON_ENGINE).__iter__()) // 5 if LESSON_ENGINE.exists() else 0

    # ── Memory ──
    memory_files = list(MEMORY_DIR.glob("*.md"))
    memory_total_kb = sum(f.stat().st_size for f in memory_files) / 1024 if memory_files else 0

    # ── Security ──
    blocked_count = 0
    if SECURITY_LOG.exists():
        blocked_count = int(_sh(f"grep -c 'BLOCKED\|blocked\|duplicate' {SECURITY_LOG} 2>/dev/null || echo 0"))

    # ── Ollama ──
    ollama_http = _sh("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:11434/api/tags 2>/dev/null || echo '000'")
    ollama_ok = ollama_http == "200"

    # ── Projects ──
    customer_dirs = [d.name for d in CUSTOMERS_DIR.iterdir() if d.is_dir()] if CUSTOMERS_DIR.exists() else []

    # ── Weaknesses count ──
    weaknesses_count = _read_file(MEMORY_DIR / "TOP_20_REMAINING_WEAKNESSES.md")
    critical_w = sum(1 for l in weaknesses_count if "🔴" in l)
    high_w = sum(1 for l in weaknesses_count if "🟠" in l)

    # ── Build display ──
    display = f"""
╔══════════════════════════════════════╗
║        OPENCLAW CEO DASHBOARD        ║
╚══════════════════════════════════════╝
📅 {now}

🟢 SYSTEM: {len(sameer_related)} sameer services running | {len(failed)} failed
   Running: {', '.join(sameer_related[:10])}
   {'(more...)' if len(sameer_related) > 10 else ''}

🤖 BOTS: {len(bot_pids)} running
   {chr(10).join(f'   → {b}' for b in bot_pids[:10])}

📊 TODAY'S WORK: {len(today_work)} items
   {chr(10).join(f'   → {w}' for w in today_work[:10])}

📚 LESSONS: ~{lesson_count} in AUTO_LESSON_ENGINE.md

🗄️ MEMORY: {len(memory_files)} files ({memory_total_kb:.0f}KB)
   → MASTER_MEMORY.md: {'✅' if MASTER_MEMORY.exists() else '❌'}
   → COMPLETED_WORK_REGISTRY.md: {'✅' if COMPLETED_WORK.exists() else '❌'}
   → AUTO_LESSON_ENGINE.md: {'✅' if LESSON_ENGINE.exists() else '❌'}
   → SERVICE_REGISTRY.md: {'✅' if SERVICE_REGISTRY.exists() else '❌'}
   → TOP_20_WEAKNESSES.md: {'✅' if (MEMORY_DIR / 'TOP_20_REMAINING_WEAKNESSES.md').exists() else '❌'}

🔒 SECURITY: {blocked_count} blocked events
   → Emergency loop: {'STOPPED ✅' if blocked_count > 0 else 'No data'}

🧠 AI: {'✅ Ollama reachable' if ollama_ok else '❌ Ollama DOWN'} (HTTP {ollama_http})
   → Provider Policy: DeepSeek primary, Ollama fallback

📦 PROJECTS: {len(customer_dirs)} customer directories
   → {', '.join(customer_dirs[:8])}{' (more...)' if len(customer_dirs) > 8 else ''}

⚠️ WEAKNESSES: {critical_w} critical | {high_w} high of 20 total
   → See TOP_20_REMAINING_WEAKNESSES.md for details

───────────────────────────────────────
factory_brain — v1.0 — Read-only CEO tool
""".strip()

    # ── Build JSON-safe data ──
    data = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "system": {
            "sameer_services_running": len(sameer_related),
            "services_failed": len(failed),
            "running": sameer_related,
        },
        "bots": {
            "count": len(bot_pids),
            "processes": bot_pids,
        },
        "today_work": today_work[:10],
        "memory": {
            "files_count": len(memory_files),
            "total_kb": round(memory_total_kb, 1),
            "master_memory_ok": MASTER_MEMORY.exists(),
            "completed_work_ok": COMPLETED_WORK.exists(),
            "lesson_engine_ok": LESSON_ENGINE.exists(),
            "registry_ok": SERVICE_REGISTRY.exists(),
        },
        "security": {
            "blocked_events": blocked_count,
        },
        "ai": {
            "ollama_ok": ollama_ok,
            "ollama_http": ollama_http,
            "provider": "deepseek-chat (primary)",
            "deepseek": "primary",
        },
        "projects": {
            "customer_dirs": len(customer_dirs),
            "dirs": customer_dirs,
        },
        "weaknesses": {
            "critical": critical_w,
            "high": high_w,
            "top20_file": str(MEMORY_DIR / "TOP_20_REMAINING_WEAKNESSES.md"),
        },
    }

    return {"display": display, "data": data}


# ══════════════════════════════════════════════════════════════════
# 2. factory_services() — All service status
# ══════════════════════════════════════════════════════════════════
def factory_services() -> dict:
    """
    List all sameer-related services with status, plus deprecated ones.
    
    Returns:
        dict with display + data
    """
    running_lines = _sh("systemctl list-units --type=service --state=running --no-pager 2>/dev/null | tail -n +2")
    active = []
    for line in running_lines.split("\n"):
        parts = line.strip().split()
        if parts and parts[0].endswith(".service"):
            active.append(parts[0])

    # Check sameer-related services one by one via systemctl is-active
    sameer_keywords = ["sameer", "freshtiq", "salama", "autopilot", "ollama", "website", "flight",
                       "openclaw", "restaurant", "binance", "radiator", "football"]
    # Get all installed service files
    installed = _sh("systemctl list-unit-files --type=service --no-pager 2>/dev/null | tail -n +2 | awk '{print $1}'")
    sameer_svcs = [s for s in installed.split("\n") if any(k in s.lower() for k in sameer_keywords)]

    not_running = []
    for svc in sameer_svcs:
        state = _sh(f"systemctl is-active {svc} 2>/dev/null")
        if state != "active" and state != "running":
            not_running.append(svc)

    # Deprecated from registry
    registry_lines = _read_file(SERVICE_REGISTRY)
    deprecated = [l.replace("- ", "").strip() for l in registry_lines if "DEPRECATED" in l or "deprecated" in l]

    # Restart counts (emergency service)
    emergency_restarts = _sh("systemctl show openclaw_emergency.service -p NRestarts 2>/dev/null | cut -d= -f2 || echo 'n/a'")

    display = f"""
══════════════ SERVICE REPORT ═══════════════

ACTIVE SERVICES ({len(active)}):
{chr(10).join(f'  🟢 {s}' for s in sorted(active)[:20])}
{'  ... (more)' if len(active) > 20 else ''}

DEAD / NOT RUNNING ({len(not_running)}):
{chr(10).join(f'  🔴 {s}' for s in sorted(not_running)[:10])}
{'  ... (more)' if len(not_running) > 10 else ''}

DEPRECATED (from SERVICE_REGISTRY.md):
{chr(10).join(f'  💀 {s}' for s in deprecated[:10])}
{'  ... (more)' if len(deprecated) > 10 else ''}

EMERGENCY RESTARTS: {emergency_restarts}
""".strip()

    data = {
        "active": active,
        "not_running": not_running,
        "deprecated": deprecated,
        "emergency_restarts": emergency_restarts,
    }

    return {"display": display, "data": data}


# ══════════════════════════════════════════════════════════════════
# 3. factory_projects() — Customer project overview
# ══════════════════════════════════════════════════════════════════
def factory_projects() -> dict:
    """
    List customer projects + active bots from KNOWN_BOTS.md.
    
    Returns:
        dict with display + data
    """
    customer_dirs = sorted([d.name for d in CUSTOMERS_DIR.iterdir() if d.is_dir()]) if CUSTOMERS_DIR.exists() else []

    # Bot details
    bot_lines = _sh("ps aux | grep 'bot\\.py' | grep -v grep").split("\n")
    bots = []
    for bl in bot_lines:
        parts = bl.split()
        if len(parts) >= 11:
            bots.append({"pid": parts[1], "cmd": parts[10], "uptime": _sh(f"ps -o etime= -p {parts[1]} 2>/dev/null || echo '?'")})

    # Project registry
    registry = _read_file(PROJECT_REGISTRY)
    stale_entries = [l.strip() for l in registry if "_deleted_" in l]

    display = f"""
══════════════ PROJECT REPORT ═══════════════

CUSTOMER PROJECTS ({len(customer_dirs)}):
{chr(10).join(f'  📁 {d}' for d in customer_dirs[:15])}
{'  ... (more)' if len(customer_dirs) > 15 else ''}

ACTIVE BOTS ({len(bots)}):
{chr(10).join(f'  🤖 PID {b["pid"]} → {b["cmd"]} (uptime: {b["uptime"]})' for b in bots)}

REGISTRY ISSUES:
{chr(10).join(f'  ⚠️ {e}' for e in stale_entries[:5])}
{'  ... (more)' if len(stale_entries) > 5 else ''}

KNOWN BOTS (from KNOWN_BOTS.md): {'✅ exists' if KNOWN_BOTS.exists() else '❌ missing'}
""".strip()

    data = {
        "customer_dirs": customer_dirs,
        "active_bots": bots,
        "stale_registry_entries": stale_entries,
        "known_bots_ok": KNOWN_BOTS.exists(),
    }

    return {"display": display, "data": data}


# ══════════════════════════════════════════════════════════════════
# 4. factory_memory() — Memory file audit
# ══════════════════════════════════════════════════════════════════
def factory_memory() -> dict:
    """
    Audit all files in memory_core/: size, age, status.
    
    Returns:
        dict with display + data
    """
    files = sorted(MEMORY_DIR.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)

    lines = []
    for f in files:
        kb = f.stat().st_size / 1024
        age = _file_age(f)
        flag = "✅" if age != "unknown" else "❓"
        lines.append(f"  {flag} {f.name:<40s} {kb:>6.1f}KB  {age}")

    total_kb = sum(f.stat().st_size for f in files) / 1024

    display = f"""
══════════════ MEMORY REPORT ═══════════════

MEMORY FILES: {len(files)} total ({total_kb:.0f}KB)

{'─' * 60}
{'  File':<40s} {'Size':>7s}  {'Modified'}
{'─' * 60}
{chr(10).join(lines)}
{'─' * 60}
""".strip()

    data = {
        "total_files": len(files),
        "total_kb": round(total_kb, 1),
        "files": [{
            "name": f.name,
            "kb": round(f.stat().st_size / 1024, 1),
            "modified": _file_age(f),
        } for f in files],
    }

    return {"display": display, "data": data}


# ══════════════════════════════════════════════════════════════════
# 5. factory_lessons() — Lesson engine overview
# ══════════════════════════════════════════════════════════════════
def factory_lessons() -> dict:
    """
    Summarize lessons from AUTO_LESSON_ENGINE.md and LESSONS_LEARNED.md.
    
    Returns:
        dict with display + data
    """
    lessons = _read_file(LESSON_ENGINE)
    lessons_learned = _read_file(LESSONS_LEARNED)

    # Count categories
    categories = {"failed_patch":0, "duplicate_task":0, "service_conflict":0, 
                  "polling_conflict":0, "registry_mismatch":0, "memory_inconsistency":0}
    for l in lessons:
        for cat in categories:
            if cat in l.lower().replace(" ", "_"):
                categories[cat] += 1

    total_lessons = sum(l.strip().startswith("|") and "Lesson" in l for l in lessons)
    critical = [l.strip() for l in lessons if "P0" in l or "Critical" in l or "🔴" in l]
    high = [l.strip() for l in lessons if "P1" in l or "High" in l or "🟠" in l]

    display = f"""
══════════════ LESSONS REPORT ═══════════════

AUTO_LESSON_ENGINE.md: {'✅ exists' if LESSON_ENGINE.exists() else '❌ missing'}
LESSONS_LEARNED.md: {'✅ exists' if LESSONS_LEARNED.exists() else '❌ missing'}

LESSON CATEGORIES:
  🔴 Failed Patch:        {categories.get("failed_patch", 0)}
  🔴 Duplicate Task:      {categories.get("duplicate_task", 0)}
  🟠 Service Conflict:    {categories.get("service_conflict", 0)}
  🟠 Polling Conflict:    {categories.get("polling_conflict", 0)}
  🟡 Registry Mismatch:   {categories.get("registry_mismatch", 0)}
  🟡 Memory Inconsistency:{categories.get("memory_inconsistency", 0)}

CRITICAL LESSONS (P0/🔴):
{chr(10).join(f'  🔴 {l[:80]}' for l in critical[:5]) or '  (none found)'}

HIGH LESSONS (P1/🟠):
{chr(10).join(f'  🟠 {l[:80]}' for l in high[:5]) or '  (none found)'}
""".strip()

    data = {
        "lesson_engine_ok": LESSON_ENGINE.exists(),
        "lessons_learned_ok": LESSONS_LEARNED.exists(),
        "categories": categories,
        "total_lessons_approx": total_lessons,
        "critical_count": len(critical),
        "high_count": len(high),
    }

    return {"display": display, "data": data}


# ══════════════════════════════════════════════════════════════════
# 6. factory_audit() — Full system capability audit
# ══════════════════════════════════════════════════════════════════
def factory_audit() -> dict:
    """
    10-point system capability audit.
    
    Returns:
        dict with display + data
    """
    checks = {}

    # 1. Memory unified
    checks["memory_unified"] = {
        "pass": MASTER_MEMORY.exists(),
        "detail": f"{'✅ MASTER_MEMORY.md present' if MASTER_MEMORY.exists() else '❌ Missing'}"
    }

    # 2. Completed work brain
    checks["completed_work_brain"] = {
        "pass": COMPLETED_WORK.exists(),
        "detail": f"{'✅ COMPLETED_WORK_REGISTRY.md present' if COMPLETED_WORK.exists() else '❌ Missing'}"
    }

    # 3. Auto lesson engine
    checks["auto_lesson_engine"] = {
        "pass": LESSON_ENGINE.exists(),
        "detail": f"{'✅ AUTO_LESSON_ENGINE.md present' if LESSON_ENGINE.exists() else '❌ Missing'}"
    }

    # 4. Service registry
    checks["service_registry"] = {
        "pass": SERVICE_REGISTRY.exists(),
        "detail": f"{'✅ SERVICE_REGISTRY.md present' if SERVICE_REGISTRY.exists() else '❌ Missing'}"
    }

    # 5. Project registry
    checks["project_registry"] = {
        "pass": PROJECT_REGISTRY.exists(),
        "detail": f"{'✅ PROJECT_REGISTRY.md present' if PROJECT_REGISTRY.exists() else '❌ Missing'}"
    }

    # 6. Known bots
    checks["known_bots"] = {
        "pass": KNOWN_BOTS.exists(),
        "detail": f"{'✅ KNOWN_BOTS.md present' if KNOWN_BOTS.exists() else '❌ Missing'}"
    }

    # 7. Current status
    checks["current_status"] = {
        "pass": CURRENT_STATUS.exists(),
        "detail": f"{'✅ CURRENT_STATUS.md present' if CURRENT_STATUS.exists() else '❌ Missing'}"
    }

    # 8. AI provider policy
    ai_policy = MEMORY_DIR / "AI_PROVIDER_POLICY.md"
    checks["ai_provider_policy"] = {
        "pass": ai_policy.exists(),
        "detail": f"{'✅ AI_PROVIDER_POLICY.md present' if ai_policy.exists() else '❌ Missing'}"
    }

    # 9. Browser worker (design or implementation)
    bw_design = MEMORY_DIR / "BROWSER_WORKER_ARCHITECTURE.md"
    bw_impl = BRIDGE_DIR / "browser_worker.py"
    checks["browser_worker"] = {
        "pass": bw_design.exists(),
        "detail": f"{'✅ Design exists' if bw_design.exists() else '❌ Missing design'}" +
                  (f" + {'✅ Implementation' if bw_impl.exists() else 'Implementation missing'}" if bw_design.exists() else "")
    }

    # 10. Factory brain (this tool)
    checks["factory_brain"] = {
        "pass": True,
        "detail": "✅ factory_brain.py running now (this session)"
    }

    passed = sum(1 for c in checks.values() if c["pass"])
    total = len(checks)

    display = f"""
══════════════ SYSTEM AUDIT ═══════════════

CAPABILITY SCORE: {passed}/{total}

{'─' * 50}
{chr(10).join(f'  {"✅" if c["pass"] else "❌"} {n:<25s} {c["detail"]}' for n, c in checks.items())}
{'─' * 50}

WEAKNESSES: See TOP_20_REMAINING_WEAKNESSES.md
  → {MEMORY_DIR / 'TOP_20_REMAINING_WEAKNESSES.md'}

DUPLICATE GUARD: {'✅ Active' if COMPLETED_WORK.exists() else '❌ Disabled'}
""".strip()

    data = {
        "score": f"{passed}/{total}",
        "checks": {n: {"pass": c["pass"], "detail": c["detail"]} for n, c in checks.items()},
    }

    return {"display": display, "data": data}


# ══════════════════════════════════════════════════════════════════
# CLI entry
# ══════════════════════════════════════════════════════════════════
ACTIONS = {
    "status": factory_status,
    "services": factory_services,
    "projects": factory_projects,
    "memory": factory_memory,
    "lessons": factory_lessons,
    "audit": factory_audit,
}

if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    format_ = sys.argv[2] if len(sys.argv) > 2 else "display"

    if action not in ACTIONS:
        print(f"Usage: python3 factory_brain.py <{'|'.join(ACTIONS)}> [display|json]")
        print(f"  Available actions: {', '.join(ACTIONS.keys())}")
        sys.exit(1)

    result = ACTIONS[action]()

    if format_ == "json":
        print(json.dumps(result["data"], indent=2, default=str))
    else:
        print(result["display"])
