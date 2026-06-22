
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
AUTO DEPLOYER — Generate → Save → Test → Deploy in one command.
Takes code from Code Factory and deploys it as a live service.
"""
import json, subprocess, os, sys, time
from pathlib import Path
from datetime import datetime, timezone

BRIDGE = Path("/root/sameer_ai_manager/openclaw_bridge")
OUTPUT_DIR = Path("/root/auto_deployed")
LOG = BRIDGE / "deployer.log"

def log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    with open(LOG, "a") as f:
        f.write(f"[{ts}] {msg}\n")
    print(f"[{ts}] {msg}")

def sh(cmd):
    return subprocess.getoutput(cmd).strip()

def deploy_bot(code, name="custom_bot", token="YOUR_BOT_TOKEN"):
    """Save Python bot code and create systemd service."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save code
    filepath = OUTPUT_DIR / f"{name}.py"
    filepath.write_text(code)
    os.chmod(filepath, 0o755)
    
    # Create systemd service
    service_content = f"""[Unit]
Description=Auto-deployed bot: {name}
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory={OUTPUT_DIR}
ExecStart=/usr/bin/python3 {filepath}
Restart=always
RestartSec=5
Environment=BOT_TOKEN={token}

[Install]
WantedBy=multi-user.target
"""
    service_path = Path(f"/etc/systemd/system/auto_{name}.service")
    service_path.write_text(service_content)
    
    # Enable and start
    sh(f"systemctl daemon-reload && systemctl enable auto_{name}.service && systemctl start auto_{name}.service")
    
    # Verify
    status = sh(f"systemctl is-active auto_{name}.service")
    
    log(f"✅ Deployed bot '{name}' → {status}")
    return {
        "name": name,
        "file": str(filepath),
        "service": f"auto_{name}.service",
        "status": status
    }

def deploy_website(code, name="custom_website"):
    """Save HTML to web server directory."""
    web_dir = Path("/var/www/html/auto_deployed")
    web_dir.mkdir(parents=True, exist_ok=True)
    
    filepath = web_dir / f"{name}.html"
    filepath.write_text(code)
    
    log(f"✅ Website deployed: {name}.html")
    return {
        "name": name,
        "url": f"http://localhost/auto_deployed/{name}.html",
        "file": str(filepath)
    }

def deploy_script(code, name="custom_script"):
    """Save and make executable."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    filepath = OUTPUT_DIR / name
    filepath.write_text(code)
    os.chmod(filepath, 0o755)
    
    log(f"✅ Script deployed: {name}")
    return {"name": name, "file": str(filepath)}

def main():
    if len(sys.argv) < 3:
        print("Usage: auto_deployer.py <bot|website|script> <filepath> [name] [token]")
        return
    
    action = sys.argv[1]
    filepath = sys.argv[2]
    name = sys.argv[3] if len(sys.argv) > 3 else f"deploy_{int(time.time())}"
    token = sys.argv[4] if len(sys.argv) > 4 else "YOUR_BOT_TOKEN"
    
    code = Path(filepath).read_text()
    
    if action == "bot":
        result = deploy_bot(code, name, token)
    elif action == "website":
        result = deploy_website(code, name)
    elif action == "script":
        result = deploy_script(code, name)
    else:
        print(f"Unknown action: {action}")
        return
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
