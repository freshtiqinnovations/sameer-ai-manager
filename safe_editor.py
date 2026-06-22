
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
from pathlib import Path
from datetime import datetime
import shutil, subprocess

def run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def backup(path):
    p = Path(path)
    bdir = p.parent / "backups"
    bdir.mkdir(exist_ok=True)
    b = bdir / f"{p.name}.safe_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(p, b)
    return b

def safe_compile(path):
    return run(f"python3 -m py_compile {path}")

def safe_restart(service):
    return run(f"systemctl restart {service} && systemctl status {service} --no-pager -l | head -25")

def safe_replace(path, old, new, service=None):
    p = Path(path)
    s = p.read_text()
    if old not in s:
        return False, "OLD_TEXT_NOT_FOUND"
    b = backup(p)
    p.write_text(s.replace(old, new, 1))
    c = safe_compile(p)
    if c.returncode != 0:
        shutil.copy2(b, p)
        return False, "COMPILE_FAILED_ROLLBACK\n" + c.stderr
    if service:
        r = safe_restart(service)
        if r.returncode != 0:
            shutil.copy2(b, p)
            safe_restart(service)
            return False, "RESTART_FAILED_ROLLBACK\n" + r.stdout + r.stderr
    return True, "SAFE_REPLACE_OK\nBackup: " + str(b)

def safe_insert_before(path, marker, text, service=None):
    p = Path(path)
    s = p.read_text()
    if marker not in s:
        return False, "MARKER_NOT_FOUND"
    if text.strip() in s:
        return True, "ALREADY_EXISTS"
    b = backup(p)
    p.write_text(s.replace(marker, text + "\n" + marker, 1))
    c = safe_compile(p)
    if c.returncode != 0:
        shutil.copy2(b, p)
        return False, "COMPILE_FAILED_ROLLBACK\n" + c.stderr
    if service:
        r = safe_restart(service)
        if r.returncode != 0:
            shutil.copy2(b, p)
            safe_restart(service)
            return False, "RESTART_FAILED_ROLLBACK\n" + r.stdout + r.stderr
    return True, "SAFE_INSERT_OK\nBackup: " + str(b)
