
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
UNIFIED CONNECTOR v1.0
═══════════════════════
Connects all 3 systems into 1 pipeline:
  TU (Telegram) → Sameer AI → Dream Team → Secret Agents → OpenClaw → Response
  Everything flows through ONE channel.
"""
import json, os, sys, time, subprocess
from pathlib import Path
from datetime import datetime, timezone

BRIDGE = Path("/root/sameer_ai_manager/openclaw_bridge")
AGENTS = Path("/root/.agents")
LOG = BRIDGE / "unified_connector.log"

def log(msg):
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    with open(LOG, "a") as f:
        f.write(f"[{ts}] {msg}\n")

def sh(cmd):
    return subprocess.getoutput(cmd)

def pipe_through_systems(text):
    """
    When Sameer AI gets a message, pipe it through all systems:
    1. Trio Engine → understand intent
    2. Dream Team → execute or delegate
    3. Secret Agents → background monitoring (always on)
    4. Return response via chat_inbox
    """
    msg_id = f"sys_{int(time.time())}"
    
    # Step 1: Trio Engine — understand the command
    try:
        sys.path.insert(0, str(BRIDGE))
        from trio_engine import understand_text, execute_task
        task = understand_text(text)
        log(f"Trio: {task.get('type')} — {task.get('description','')[:50]}")
    except:
        task = {"type": "unknown"}
    
    # Step 2: Dream Team — if system command, delegate
    if task.get("type") in ["system", "discussion", "status"]:
        try:
            from dream_team import DreamTeam
            team = DreamTeam()
            dream_response = team.parse_and_delegate(text)
            return dream_response
        except Exception as e:
            log(f"Dream Team error: {e}")
    
    # Step 3: If it's a generate command, go direct
    if task.get("type") in ["generate_bot", "generate_website"]:
        return f"✅ {task.get('description','Task created')}"
    
    # Step 4: Secret Agents (always running in background, no action needed)
    
    return None  # Let Sameer AI handle it normally

def daemon():
    """Run continuously — bridge between all systems."""
    log("🔄 UNIFIED CONNECTOR STARTED")
    
    while True:
        try:
            # Read Sameer AI's outbox
            outbox = BRIDGE / "chat_outbox.jsonl"
            if outbox.exists() and outbox.stat().st_size > 0:
                lines = outbox.read_text().strip().splitlines()
                kept = []
                for line in lines:
                    if not line.strip(): continue
                    try:
                        msg = json.loads(line)
                        text = msg.get("text", "")
                        
                        if text:
                            log(f"📥 Processing: {text[:50]}")
                            result = pipe_through_systems(text)
                            
                            if result:
                                # Write to Sameer AI inbox
                                reply = {
                                    "id": f"con_{int(time.time())}",
                                    "text": str(result)[:3500],
                                    "status": "done",
                                    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                                }
                                inbox = BRIDGE / "chat_inbox.jsonl"
                                with open(inbox, "a") as f:
                                    f.write(json.dumps(reply) + "\n")
                                log(f"📤 Reply sent: {str(result)[:60]}")
                            else:
                                kept.append(line)
                    except:
                        kept.append(line)
                
                if kept:
                    outbox.write_text("\n".join(k for k in kept if k.strip()) + "\n")
                else:
                    outbox.write_text("")
            
            # Also run Dream Team processing
            subprocess.getoutput("python3 /root/sameer_ai_manager/openclaw_bridge/dream_team.py >/dev/null 2>&1")
            
            time.sleep(2)
        except KeyboardInterrupt:
            break
        except:
            time.sleep(5)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "daemon":
        daemon()
    else:
        print("🔗 UNIFIED CONNECTOR")
        print("Usage: unified_connector.py daemon")
