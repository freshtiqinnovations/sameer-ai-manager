
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
import subprocess
import shutil

BASE = Path("/root/sameer_ai_manager")
CUSTOMERS = Path("/root/workspaces/customers")

def run(cmd, timeout=60):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return r.returncode, (r.stdout + r.stderr)

def backup_file(path):
    path = Path(path)
    bdir = path.parent / "backups"
    bdir.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = bdir / f"{path.name}.safe_{stamp}"
    shutil.copy2(path, dest)
    return dest

def compile_file(path):
    return run(f"python3 -m py_compile {path}", timeout=40)

def restart_service(service):
    return run(f"systemctl restart {service} && systemctl status {service} --no-pager", timeout=60)

def safe_replace(path, old, new, service=None):
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    if old not in text:
        return False, "OLD_TEXT_NOT_FOUND"
    backup = backup_file(path)
    path.write_text(text.replace(old, new), encoding="utf-8")
    code, out = compile_file(path)
    if code != 0:
        shutil.copy2(backup, path)
        return False, "COMPILE_FAILED_ROLLBACK_DONE\n" + out
    if service:
        code, out = restart_service(service)
        if code != 0:
            shutil.copy2(backup, path)
            restart_service(service)
            return False, "RESTART_FAILED_ROLLBACK_DONE\n" + out
    return True, f"SAFE_PATCH_SUCCESS\nBackup: {backup}"


def safe_insert_before(path, marker, insert_text, service=None):
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    if marker not in text:
        return False, "MARKER_NOT_FOUND"
    if insert_text.strip() in text:
        return True, "ALREADY_EXISTS"
    backup = backup_file(path)
    path.write_text(text.replace(marker, insert_text + "\n" + marker), encoding="utf-8")
    code, out = compile_file(path)
    if code != 0:
        shutil.copy2(backup, path)
        return False, "COMPILE_FAILED_ROLLBACK_DONE\n" + out
    if service:
        code, out = restart_service(service)
        if code != 0:
            shutil.copy2(backup, path)
            restart_service(service)
            return False, "RESTART_FAILED_ROLLBACK_DONE\n" + out
    return True, f"SAFE_INSERT_SUCCESS\nBackup: {backup}"

def safe_append(path, append_text, service=None):
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    if append_text.strip() in text:
        return True, "ALREADY_EXISTS"
    backup = backup_file(path)
    path.write_text(text + "\n" + append_text + "\n", encoding="utf-8")
    code, out = compile_file(path)
    if code != 0:
        shutil.copy2(backup, path)
        return False, "COMPILE_FAILED_ROLLBACK_DONE\n" + out
    if service:
        code, out = restart_service(service)
        if code != 0:
            shutil.copy2(backup, path)
            restart_service(service)
            return False, "RESTART_FAILED_ROLLBACK_DONE\n" + out
    return True, f"SAFE_APPEND_SUCCESS\nBackup: {backup}"

def service_status(service):
    return run(f"systemctl status {service} --no-pager -l | head -40", timeout=40)
