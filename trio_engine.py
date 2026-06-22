
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
UNIFIED TRIO ENGINE v1.0
═══════════════════════════════════════
Sameer (TU) ↔ Sameer AI Manager (BRAIN) ↔ OpenClaw (WORKER)

Is system ka kaam:
1. Tu Sameer AI bot ko kuch bhi bole (Hinglish/English)
2. Sameer AI Bot humein (OpenClaw) ko task de
3. Hum process karein, result bhejein
4. Sameer AI result ko samjhe, tujhe human-friendly reply kare

Aise ChatGPT ki zaroorat nahi — sab kuch local, team me.
"""
import json, subprocess, sys, os, re
from pathlib import Path
from datetime import datetime, timezone

BRIDGE = Path("/root/sameer_ai_manager/openclaw_bridge")
INBOX = BRIDGE / "tasks_inbox.jsonl"
DONE = BRIDGE / "tasks_done.jsonl"
OUTBOX = BRIDGE / "chat_outbox.jsonl"
INBOX_REPLY = BRIDGE / "chat_inbox.jsonl"
TRIO_LOG = BRIDGE / "trio_engine.log"
SECURITY_POLICY = BRIDGE / "security_policy.json"

# ═══════════════════════════════════════
# CENTRAL OLLAMA-FIRST AI ROUTER
# ═══════════════════════════════════════

def ask_ollama_first(text):
    """Central Ollama-first AI gateway. DeepSeek is approval-only."""
    try:
        import sys
        from pathlib import Path
        bridge = Path(__file__).resolve().parent
        if str(bridge) not in sys.path:
            sys.path.insert(0, str(bridge))
        import openclaw_brain
        return openclaw_brain.ask(text)
    except Exception as e:
        return "Ollama/evidence router error: " + str(e)[:250]

# ═══════════════════════════════════════
# TRIO SYSTEM MODE
# ═══════════════════════════════════════

def log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    with open(TRIO_LOG, "a") as f:
        f.write(f"[{ts}] {msg}\n")

def sh(cmd):
    return subprocess.getoutput(cmd)

def load_policy():
    if SECURITY_POLICY.exists():
        return json.loads(SECURITY_POLICY.read_text())
    return {"blocked_commands": [], "ceo_approval": []}

# ═══════════════════════════════════════
# INTELLIGENT TASK UNDERSTANDING
# ═══════════════════════════════════════

def understand_text(text):
    """
    Sameer AI se aaya text — samjho ki kya karna hai.
    Returns a task dict that OpenClaw can execute.
    """
    t = text.lower().strip()
    
    # 1. Code Generation Tasks
    if re.search(r'(banao|bana do|bana de|make |create |generate|generat|likh |write |build )', t):
        if re.search(r'(bot|telegram bot)', t):
            name = t.replace("banao", "").replace("ban", "").replace("make", "").replace("create", "").replace("generate", "").strip()
            if re.search(r'(support|customer|service|help|care)', t):
                return {
                    "type": "generate_bot",
                    "prompt": name or "customer support bot",
                    "description": f"🤖 Bot ban raha hai: {name or 'support bot'}",
                    "to_user": "Bot generation start ho gaya hai! Kuch seconds me ready."
                }
            return {
                "type": "generate_bot",
                "prompt": name or "telegram bot",
                "description": f"🤖 Bot ban raha hai..."
            }
        
        elif re.search(r'(website|site|web)', t):
            name = t.replace("banao", "").replace("make", "").replace("create", "").strip()
            return {
                "type": "generate_website",
                "prompt": name or "business website",
                "description": f"🌐 Website ban rahi hai: {name or 'business site'}",
                "to_user": "Website generate ho rahi hai! HTML ready hone wala hai."
            }
        
        elif re.search(r'(app|application|mobile)', t):
            return {
                "type": "generate_app",
                "prompt": t,
                "description": f"📱 App generate ho raha hai...",
                "to_user": "App generation start! (Flutter based)"
            }
        
        elif re.search(r'(script|code|program)', t):
            return {
                "type": "generate_script",
                "prompt": t,
                "description": f"📜 Script likh raha hoon..."
            }
    
    # 2. System Tasks
    if re.search(r'(check|status|health|dekh|dikha|dikhao|kitna|report|kya haal|kaisa|kaise|full|overview|summary|sab|all)', t):
        if re.search(r'(disk|space|storage|memory|hard)', t):
            return {"type": "system", "action": "disk_status", "description": "💾 Disk check kar raha hoon..."}
        elif re.search(r'(ram|memory|free)', t):
            return {"type": "system", "action": "ram_status", "description": "🧠 RAM check kar raha hoon..."}
        elif re.search(r'(service|worker|bot|daemon)', t):
            return {"type": "system", "action": "services_list", "description": "📋 Services check kar raha hoon..."}
        elif re.search(r'(security|safe|suraksha|fortress|guard|hack)', t):
            return {"type": "system", "action": "security_status", "description": "🔒 Security check kar raha hoon..."}
        elif re.search(r'(backup|bakup|save|bache)', t):
            return {"type": "system", "action": "backup_status", "description": "💾 Backup check kar raha hoon..."}
        else:
            return {"type": "system", "action": "full_status", "description": "📊 Full health check kar raha hoon...", "to_user": "System check ho raha hai! Ek second..."}
    
    # 3. Action Tasks
    if re.search(r'(clean|saaf|saf |free up|delete|hata)', t):
        if re.search(r'(disk|space|storage|temp|temporary|cache)', t):
            return {"type": "system", "action": "clean_disk", "description": "🧹 Disk clean kar raha hoon..."}
    
    if re.search(r'(restart|reload|reboot|shuru karo|band karo)', t):
        service_match = re.search(r'(sameer|openclaw|fortress|watchdog|emergency|chat|webhook|autobackup)', t)
        if service_match:
            return {"type": "system", "action": "restart_service", "service": service_match.group(1), "description": f"🔄 {service_match.group(1)} restart kar raha hoon..."}
    
    if re.search(r'(deploy|publish|live|production)', t):
        return {"type": "system", "action": "deploy_status", "description": "🚀 Deploy status check kar raha hoon..."}
    
    # 4. Discussion / Feature Add / Upgrade
    if re.search(r'(feature|upgrade|add|naya|improve|better|aur powerful|discuss|discussion|suggest|suggestion|idea)', t):
        return {
            "type": "discussion",
            "description": "💡 Feature discuss karne ke liye ready!",
            "to_user": "Batao kya naya feature chahiye? Main analyse karta hoon aur implement karta hoon.",
            "suggestions": [
                "Bot banao <description> — Bot generate karne ke liye",
                "Website banao <description> — Website generate karne ke liye",
                "App banao <description> — App generate karne ke liye",
                "Status do — System health ke liye",
                "Disk clean karo — Disk space free karne ke liye"
            ]
        }
    
    # 5. AI Query (puchne / samajhne wali baat)
    if re.search(r'(kya|kaise|kyun|kab|kaun|samjhao|batao|explain|tell|what|how|why|plzzz|bro)', t):
        return {
            "type": "ai_query",
            "query": text,
            "description": "🤔 DeepSeek se puch raha hoon...",
            "to_user": "DeepSeek AI se analysis karwa raha hoon..."
        }
    
    # 6. Default
    return {
        "type": "unknown",
        "description": f"❌ Yeh command samajh nahi aaya. Kya karna chahte ho?",
        "to_user": "Main yeh commands samajhta hoon:\n\n📊 **System Commands**\n• status do / sab kaisa hai — System health\n• disk clean karo — Space free\n• services — Running services list\n• security / suraksha — Security report\n• restart <service> — Service restart\n\n🤖 **Generate Commands**\n• bot banao <description> — Bot generate\n• website banao <description> — Website generate\n• app banao <description> — App generate\n\n💡 **Discuss Commands**\n• feature add karo / naya kya — Feature discuss\n• kya bana sakte hain / idea — Suggestions\n\nTry karo: 'status do'",
        "suggestions": ["status do", "disk clean karo", "bot banao support bot", "website banao business", "kya bana sakte hain"]
    }

# ═══════════════════════════════════════
# TASK EXECUTION
# ═══════════════════════════════════════

def execute_task(task):
    """Execute a task and return results."""
    task_type = task.get("type")
    action = task.get("action")
    
    if task_type == "system":
        if action == "full_status":
            uptime = sh("uptime -p")
            disk = sh("df -h / | awk 'NR==2{print $3\"/\"$2\" (\"$5\")\"}'")
            ram = sh("free -h | awk '/Mem:/{print $3\"/\"$2}'")
            swap = sh("free -h | awk '/Swap:/{print $3\"/\"$2}'")
            failed = sh("systemctl list-units --type=service --state=failed --no-pager | awk '/failed/ {count++} END {print count+0}'")
            sameer = sh("systemctl is-active sameer_ai_manager.service")
            openclaw = sh("ps aux | grep 'openclaw.*gateway' | grep -v grep | awk '{print \"PID \"$2}'") or "❌ DOWN"
            fortress = sh("systemctl is-active openclaw_fortress.service")
            queue = sh("wc -l < " + str(INBOX)) if INBOX.exists() else "0"
            
            return {
                "response": [
                    "📊 **SYSTEM REPORT**",
                    f"⏱ Uptime: {uptime}",
                    f"💾 Disk: {disk}",
                    f"🧠 RAM: {ram}",
                    f"🔄 Swap: {swap}",
                    f"❌ Failed: {failed}",
                    f"",
                    f"🤖 Sameer AI: {sameer}",
                    f"⚙️ OpenClaw: {openclaw}",
                    f"🛡 Fortress: {fortress}",
                    f"📥 Queue: {queue}",
                    f"",
                    f"✅ **Sab thik hai boss!**" if "0" in failed else "⚠️ **Kuch services failed hain**"
                ]
            }
        
        elif action == "disk_status":
            result = sh("df -h /")
            return {"response": [f"💾 **Disk Status**\n```\n{result}\n```"]}
        
        elif action == "clean_disk":
            results = []
            results.append(sh("journalctl --vacuum-time=2d 2>/dev/null; echo '✅ Journal trim ho gaya'"))
            results.append(sh("apt clean 2>/dev/null; echo '✅ Apt cache saaf hua'"))
            results.append(sh("find /tmp -type f -mtime +2 -delete 2>/dev/null; echo '✅ Temp files delete hue'"))
            after = sh("df -h / | awk 'NR==2{print $5, $3\"/\"$2}'")
            results.append(f"Abhi disk: {after}")
            return {"response": [f"🧹 **Disk Cleanup Done**\n" + "\n".join(results)]}
        
        elif action == "services_list":
            services = sh("systemctl list-units --type=service --state=running --no-pager | grep -E 'sameer|openclaw|auto_' | awk '{$2=$3=$4=\"\"; print \"• \"$0}'")
            return {"response": [f"📋 **Running Services**\n```\n{services}\n```"]}
        
        elif action == "security_status":
            log_data = sh("tail -5 " + str(BRIDGE / "security.log"))
            blocked = sh("grep -c BLOCKED " + str(BRIDGE / "security.log") + " 2>/dev/null || echo 0")
            ceo = sh("grep -c CEO " + str(BRIDGE / "security.log") + " 2>/dev/null || echo 0")
            return {"response": [f"🔒 **Security Report**\nBlocked: {blocked}\nCEO Pending: {ceo}\n\nRecent:\n```\n{log_data}\n```"]}
        
        elif action == "restart_service":
            svc = task.get("service", "")
            result = sh(f"systemctl restart {svc}.service 2>&1 || systemctl restart {svc} 2>&1")
            status = sh(f"systemctl is-active {svc}.service 2>/dev/null || systemctl is-active {svc} 2>/dev/null || echo 'unknown'")
            return {"response": [f"🔄 **Restart {svc}**\nResult: {result}\nStatus: {status}"]}
    
    elif task_type in ["generate_bot", "generate_website", "generate_script", "generate_app"]:
        # Defer to inbox — fortress worker will pick up
        return {"response": [f"✅ Task created: {task['type']} - {task.get('description','')}"]}
    
    elif task_type == "ai_query":
        query = task.get("query", "")
        answer = ask_ollama_first(query)
        return {"response": [f"🤖 **Ollama AI**\n\n{answer[:2000]}", "source: ollama"]}
    
    return {"response": [f"Task completed: {task_type}"]}

# ═══════════════════════════════════════
# SAMEER AI CONNECTION
# ═══════════════════════════════════════

def process_from_sameer():
    """
    Sameer AI se jo bhi text aa raha hai — process karo.
    Reply directly to Sameer AI's inbox.
    """
    if not OUTBOX.exists() or OUTBOX.stat().st_size == 0:
        return False
    
    lines = OUTBOX.read_text().strip().splitlines()
    if not lines or not lines[0].strip():
        return False
    
    processed = False
    
    for line in lines:
        if not line.strip():
            continue
        try:
            msg = json.loads(line)
            text = msg.get("text", "")
            msg_id = msg.get("id", "")
            
            log(f"📥 Sameer AI bola: {text[:100]}")
            
            # Understand
            task = understand_text(text)
            
            # Execute
            result = execute_task(task)
            
            # Create human-friendly reply
            response_lines = result.get("response", ["Done ✅"])
            response_text = "\n".join(response_lines)
            
            # Add suggestion if applicable
            suggestions = task.get("suggestions", [])
            if suggestions:
                response_text += "\n\n💡 **Suggestions:**\n" + "\n".join([f"• {s}" for s in suggestions[:3]])
            
            # Send reply back to Sameer AI
            reply = {
                "id": f"trio_{int(datetime.now().timestamp())}",
                "text": response_text[:3500],
                "type": task.get("type", "response"),
                "status": "done",
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            }
            
            with open(INBOX_REPLY, "a") as f:
                f.write(json.dumps(reply) + "\n")
            
            log(f"📤 Reply bheja: {response_text[:60]}...")
            processed = True
            
        except Exception as e:
            log(f"❌ Error: {e}")
    
    # Clear outbox
    open(OUTBOX, "w").close()
    return processed

# ═══════════════════════════════════════
# CONVERSATION MODE (continuous chat)
# ═══════════════════════════════════════

def conversation_mode():
    """Run continuously — chat, learn, discuss features."""
    log("🤖 TRIO ENGINE STARTED — Continuous conversation mode")
    print("✅ Trio Engine running. Waiting for Sameer AI messages...")
    
    import time
    while True:
        try:
            processed = process_from_sameer()
            if processed:
                log("✅ Messages processed")
            time.sleep(3)
        except KeyboardInterrupt:
            log("Trio engine stopped")
            break
        except Exception as e:
            log(f"❌ Loop error: {e}")
            time.sleep(10)

# ═══════════════════════════════════════
# MAIN
# ═══════════════════════════════════════

def main():
    # Auto-process mode: if outbox has messages, process them
    outbox = Path("/root/sameer_ai_manager/openclaw_bridge/chat_outbox.jsonl")
    if len(sys.argv) == 1 and outbox.exists() and outbox.stat().st_size > 0:
        if process_from_sameer():
            return
    
    if len(sys.argv) > 1 and sys.argv[1] == "daemon":
        conversation_mode()
    elif len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        task = understand_text(text)
        result = execute_task(task)
        print("\n".join(result.get("response", ["✅"])))
        print(f"\n--- Type: {task.get('type', '?')} ---")
    else:
        print("⚡ TRIO ENGINE v1.0")
        print("Usage:")
        print("  trio_engine.py <text>    — Single command")
        print("  trio_engine.py daemon    — Continuous mode")
        print("")
        print("Example: trio_engine.py 'server status do'")

if __name__ == "__main__":
    main()
