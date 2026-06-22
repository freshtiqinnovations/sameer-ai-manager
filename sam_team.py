#!/usr/bin/env python3
"""
sam_team.py — Phase 6: Team Mode / Swarm Coordination

Team room, role system, task discussion, tough task mode, cost-safe routing.
"""

import os, json, sqlite3, time, random, subprocess
from datetime import datetime

SAM_DIR = "/root/workspaces/sameer_ai_manager"
TASK_DB = os.path.join(SAM_DIR, "task_queue.db")
TEAM_ROOM = os.path.join(SAM_DIR, "team_room.jsonl")

# ROLES

ROLES = {
    "Boss": "Task creator, final approver — Sameer AI Manager",
    "CTO": "Plan review, tech risk assessment — OpenClaw",
    "Monitor": "Health context before execution",
    "Repair Worker": "Execute bot repairs/restarts",
    "Vision Worker": "Handle screenshot/PDF analysis (Gemini only)",
    "Voice Worker": "Handle voice transcription (Google SR)",
    "Payment Worker": "Handle payment verification tasks",
    "Website Worker": "Handle website/nginx tasks",
    "Bot Worker": "Handle bot config/command changes",
    "Prover": "Verify evidence, compute score",
    "Learner": "Save lessons/mistakes/fixes after task completion",
}

# TEAM ROOM

def send_to_team_room(task_id, sender, receiver, message, status="sent"):
    entry = {
        "timestamp": datetime.now().isoformat()[:19],
        "task_id": task_id,
        "sender": sender,
        "receiver": receiver,
        "status": status,
        "message": message[:500],
    }
    with open(TEAM_ROOM, 'a') as f:
        f.write(json.dumps(entry) + '\n')
    return entry

def get_team_discussion(task_id, limit=20):
    if not os.path.exists(TEAM_ROOM):
        return []
    messages = []
    with open(TEAM_ROOM) as f:
        for line in f:
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
                if entry.get("task_id") == task_id:
                    messages.append(entry)
            except:
                continue
    return messages[-limit:]

def get_recent_team_room(limit=10):
    if not os.path.exists(TEAM_ROOM):
        return []
    messages = []
    with open(TEAM_ROOM) as f:
        for line in f:
            if not line.strip():
                continue
            try:
                messages.append(json.loads(line))
            except:
                continue
    return messages[-limit:]

# DISCUSSION FLOW

def parse_team_task_intent(task_text):
    text = task_text.lower()
    intent = {
        "target": "sam",
        "targets_customer": False,
        "action_type": "general",
        "subtasks": []
    }
    LOCKED = ["flight_fare_ai", "freshtiq_trader", "freshtiq_sales", "salama",
              "autopilot_hub", "flight_scanner", "restaurant_demo"]
    for bot in LOCKED:
        if bot in text:
            intent["targets_customer"] = True
            intent["target"] = bot
            break
    if any(w in text for w in ["payment","payu","upi","refund","charge"]):
        intent["action_type"] = "payment"
    elif any(w in text for w in ["fix","repair","edit","patch","change"]):
        intent["action_type"] = "fix"
    elif any(w in text for w in ["check","status","health","test"]):
        intent["action_type"] = "check"
    elif any(w in text for w in ["backup","snapshot","sync","registry"]):
        intent["action_type"] = "maintenance"
    elif any(w in text for w in ["website","nginx","portal"]):
        intent["action_type"] = "website"
    elif any(w in text for w in ["voice","vision","screenshot","analyze"]):
        intent["action_type"] = "sensor"
    return intent

def run_discussion_flow(task_id, task_text):
    """Boss -> CTO plan -> Monitor context -> Learner lessons -> Prover checklist."""
    flow = []
    send_to_team_room(task_id, "Boss", "CTO", "New task: " + task_text[:100], "pending")
    flow.append(("Boss", "Task " + task_id + " created"))

    intent = parse_team_task_intent(task_text)
    risk = "HIGH" if intent.get("targets_customer") else "LOW"
    cto_msg = "Tech review: target=" + intent["target"] + ", risk=" + risk
    if intent.get("action_type"):
        cto_msg += ", action=" + intent["action_type"]
    send_to_team_room(task_id, "CTO", "Monitor", cto_msg, "approved")
    flow.append(("CTO", cto_msg))

    svc = subprocess.getoutput("systemctl is-active sameer_ai_manager.service 2>/dev/null")
    disk = subprocess.getoutput("df -h / | tail -1 | awk '{print $5}'")
    hc_msg = "SAM service: " + svc + ", disk: " + disk
    send_to_team_room(task_id, "Monitor", "Learner", hc_msg, "ok")
    flow.append(("Monitor", hc_msg))

    try:
        db = os.path.join(SAM_DIR, "learner.db")
        conn = sqlite3.connect(db, timeout=2)
        cur = conn.cursor()
        cur.execute("SELECT pattern_name FROM fixes ORDER BY count DESC LIMIT 3")
        past_fixes = [r[0] for r in cur.fetchall() if r[0]]
        conn.close()
        if past_fixes:
            learn_msg = "Past fixes: " + ", ".join(str(f)[:40] for f in past_fixes)
        else:
            learn_msg = "No past fixes found"
    except:
        learn_msg = "learner.db unavailable"
    send_to_team_room(task_id, "Learner", "Prover", learn_msg, "ok")
    flow.append(("Learner", learn_msg))

    proof_msg = "Proof gates: backup(20)+compile(20)+service(20)+learner(15)+repair_log(15)+router(10)=100"
    send_to_team_room(task_id, "Prover", "Boss", proof_msg, "ready")
    flow.append(("Prover", proof_msg))

    try:
        conn = sqlite3.connect(TASK_DB, timeout=2)
        cur = conn.cursor()
        plan = "\n".join([r + ": " + m for r, m in flow])
        cur.execute("UPDATE tasks SET plan=?, status=? WHERE id=?", (plan[:2000], "PLANNED", task_id))
        conn.commit()
        conn.close()
    except:
        pass

    return flow

# TOUGH TASK MODE

def split_tough_task(task_text):
    text = task_text.lower()
    if "payment" in text and "website" in text:
        return [
            ("Payment plan", "Create payment flow plan"),
            ("DB change", "Update payment database if needed"),
            ("Webhook", "Configure payment webhook endpoint"),
            ("UI", "Update payment UI"),
            ("Test", "Test payment flow end-to-end"),
            ("Proof", "Verify payment works, collect screenshots"),
        ]
    elif "website" in text or "nginx" in text or "portal" in text:
        return [
            ("Config plan", "Review current nginx config"),
            ("Change", "Apply configuration change"),
            ("Test", "Test HTTP response codes"),
            ("Verify", "Check all routes work"),
            ("Proof", "Capture evidence"),
        ]
    elif "bot" in text and ("fix" in text or "repair" in text):
        return [
            ("Diagnose", "Check logs, find root cause"),
            ("Backup", "Backup current bot code"),
            ("Fix", "Apply fix in dry-run first"),
            ("Compile", "Verify syntax"),
            ("Restart", "Restart service"),
            ("Verify", "Check logs for 0 errors"),
            ("Proof", "Evidence collection"),
        ]
    elif any(w in text for w in ["backup","snapshot","sync"]):
        return [
            ("Plan", "What to backup/sync"),
            ("Execute", "Run backup/sync"),
            ("Verify", "Check files exist"),
            ("Proof", "Evidence collection"),
        ]
    else:
        return [
            ("Plan", "Analyze task requirements"),
            ("Execute", "Run task in approval mode"),
            ("Verify", "Check result"),
            ("Proof", "Evidence collection"),
        ]

# ASSIGN

def assign_role(task_id, role_name):
    if role_name not in ROLES:
        return {"status": "UNKNOWN_ROLE", "valid_roles": list(ROLES.keys())}
    send_to_team_room(task_id, "Boss", role_name, "Assigned to " + role_name, "assigned")
    return {"status": "ASSIGNED", "role": role_name, "task_id": task_id}

# REVIEW

def review_task(task_id):
    try:
        conn = sqlite3.connect(TASK_DB, timeout=2)
        cur = conn.cursor()
        cur.execute("SELECT task, plan, route, evidence_score, status FROM tasks WHERE id=?", (task_id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return "Task not found."
        task_text, plan, route, evidence, status = row
        lines = [
            "🔍 CTO REVIEW — " + task_id,
            "",
            "📥 Task: " + str(task_text)[:100],
            "📌 Status: " + str(status),
            "📋 Route: " + (str(route) if route else "unrouted"),
            "📊 Current evidence: " + str(evidence or 0) + "/100",
            "",
            "Proof Checklist:",
            "  [ ] Backup exists (20 pts)",
            "  [ ] Compile passes (20 pts)",
            "  [ ] Service active (20 pts)",
            "  [ ] Learner.db updated (15 pts)",
            "  [ ] Repair log updated (15 pts)",
            "  [ ] Router active (10 pts)",
            "",
            "Need 100/100 to close.",
        ]
        return "\n".join(lines)
    except Exception as e:
        return "Review error: " + str(e)

# PROVE

def prove_task(task_id):
    try:
        import sys as _ps
        _ps.path.insert(0, SAM_DIR)
        import sam_approval
        ev = sam_approval.compute_evidence(task_id)
        send_to_team_room(task_id, "Prover", "Boss", "Evidence: " + str(ev['score']) + "/100", "verified")
        return ev
    except Exception as e:
        return {"score": 0, "components": [], "error": str(e)}

# CLOSE (only at 100)

TEAM_COMPLETED = "COMPLETED"

def close_task(task_id):
    ev = prove_task(task_id)
    if ev['score'] >= 100:
        try:
            conn = sqlite3.connect(TASK_DB, timeout=2)
            cur = conn.cursor()
            cur.execute("UPDATE tasks SET status=?, evidence_score=? WHERE id=?", (TEAM_COMPLETED, 100, task_id))
            conn.commit()
            conn.close()
        except:
            pass
        send_to_team_room(task_id, "Prover", "Boss", "Task CLOSED - evidence 100/100", "closed")
        return {"status": "CLOSED", "evidence": 100}
    else:
        send_to_team_room(task_id, "Prover", "Boss", "Cannot close - evidence " + str(ev['score']) + "/100, need 100", "blocked")
        return {"status": "BLOCKED", "evidence": ev['score'], "components": ev.get('components', [])}

# COST-SAFE ROUTING

COST_ROUTE = {
    "grep": "ollama",
    "systemctl": "ollama",
    "logs": "ollama",
    "file_check": "ollama",
    "screenshot": "gemini",
    "pdf": "gemini",
    "research": "gemini",
    "code": "deepseek",
    "fix": "deepseek",
    "edit": "deepseek",
    "config": "deepseek",
}

def recommend_model(task_text):
    text = task_text.lower()
    for keyword, model in COST_ROUTE.items():
        if keyword in text:
            return model
    return "deepseek"

# TEAM SUMMARY

def team_summary():
    lines = ["🤝 SAMEER OS — TEAM ROOM", "", "Generated: " + datetime.now().isoformat()[:19], "", "ROLES:"]
    for role, desc in ROLES.items():
        lines.append("  🔹 " + role + ": " + desc)
    lines.append("")
    try:
        conn = sqlite3.connect(TASK_DB, timeout=2)
        cur = conn.cursor()
        for status_name, emoji in [("PENDING","⏳"),("PLANNED","📋"),("APPROVED","✅"),
                                     ("RUNNING","⚡"),("COMPLETED","🟢"),("REJECTED","❌"),
                                     ("ROLLEDBACK","↩️"),("FAILED","🔴")]:
            cur.execute("SELECT COUNT(*) FROM tasks WHERE status=?", (status_name,))
            ct = cur.fetchone()[0]
            if ct > 0:
                lines.append(emoji + " " + status_name + ": " + str(ct))
        conn.close()
    except:
        lines.append("  (task db unavailable)")
    lines.append("")
    lines.append("DISCUSSION FLOW:")
    lines.append("  Boss -> CTO -> Monitor -> Learner -> Prover -> Boss")
    lines.append("")
    lines.append("COST-SAFE ROUTING:")
    for keyword, model in COST_ROUTE.items():
        lines.append("  " + keyword + " -> " + model)
    lines.append("")
    lines.append("PROOF GATE:")
    lines.append("  Close only when evidence = 100/100")
    return "\n".join(lines)

# FORMATTING

def format_team_discussion(task_id):
    msgs = get_team_discussion(task_id)
    if not msgs:
        return "No discussion for " + task_id
    lines = ["📋 TEAM DISCUSSION — " + task_id]
    for m in msgs:
        lines.append("")
        lines.append("  " + m['timestamp'])
        lines.append("  " + m['sender'] + " -> " + m['receiver'])
        lines.append("  " + m['message'][:120])
        lines.append("  Status: " + m['status'])
    return "\n".join(lines)

def format_team_room(limit=10):
    msgs = get_recent_team_room(limit)
    if not msgs:
        return "🤝 No team room activity yet."
    lines = ["🤝 TEAM ROOM — LATEST ACTIVITY"]
    for m in msgs:
        lines.append("")
        lines.append("  `" + m['task_id'] + "` | " + m['timestamp'])
        lines.append("  " + m['sender'] + " -> " + m['receiver'])
        lines.append("  " + m['message'][:100])
        lines.append("  Status: " + m['status'])
    return "\n".join(lines)

if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "demo"

    if cmd == "demo":
        print("PHASE 6 — TEAM MODE DEMO\n")
        try:
            conn = sqlite3.connect(TASK_DB, timeout=2)
            cur = conn.cursor()
            tid = "TEAM" + str(int(time.time()))
            cur.execute("INSERT OR REPLACE INTO tasks (id, task, status) VALUES (?, ?, ?)",
                       (tid, "Check SAM health and system status", "PENDING"))
            conn.commit()
            conn.close()
            print("1. Task created: " + tid)
        except Exception as e:
            print("1. Task creation error: " + str(e))
            tid = "TEAM" + str(int(time.time()))

        print("\n2. DISCUSSION FLOW:")
        flow = run_discussion_flow(tid, "Check SAM health")
        for role, msg in flow:
            print("   " + role + ": " + msg)

        print("\n3. TEAM ROOM:")
        room = get_team_discussion(tid)
        for m in room:
            print("   " + m['sender'] + " -> " + m['receiver'] + ": " + m['message'][:60])

        print("\n4. ASSIGN:")
        a = assign_role(tid, "Prover")
        print("   Result: " + a['status'])

        print("\n5. REVIEW:")
        r = review_task(tid)
        for line in r.split('\n')[:8]:
            print("   " + line)

        print("\n6. PROVE:")
        ev = prove_task(tid)
        print("   Score: " + str(ev['score']) + "/100")

        print("\n7. TOUGH TASK SPLIT:")
        tough = split_tough_task("Build website payment system")
        for name, desc in tough:
            print("   \u2022 " + name + ": " + desc)

        print("\n8. COST-SAFE ROUTING:")
        tests = ["fix flight_fare bot", "check systemctl status", "analyze screenshot error"]
        for t in tests:
            model = recommend_model(t)
            print('   "' + t + '" -> ' + model)

        print("\n9. CLOSE (blocked at 80):")
        c = close_task(tid)
        print("   Status: " + c['status'] + " (evidence " + str(c['evidence']) + ")")

        print("\n10. TEAM SUMMARY:")
        s = team_summary()
        for line in s.split('\n')[:15]:
            print("   " + line)

        print("\nPhase 6 demo complete (task " + tid + ").")
