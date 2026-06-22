
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
import os,time,json,subprocess,datetime,shutil

BASE="/root/sameer_ai_manager/upgrade_engine"
LOG=f"{BASE}/reports/upgrade.log"

def log(x):
    with open(LOG,"a") as f:
        f.write(f"{datetime.datetime.now()} | {x}\n")

def sh(cmd):
    return subprocess.getoutput(cmd)

def safe_upgrade(bot,task):

    project=f"/root/workspaces/customers/{bot}"
    service=f"{bot}.service"

    if not os.path.exists(project):
        return f"BOT_NOT_FOUND: {bot}"

    backup=f"/root/backups/{bot}_safe_{int(time.time())}.tar.gz"

    log(f"START {bot} => {task}")

    # backup
    sh(f"tar -czf {backup} {project}")
    log(f"BACKUP_OK {backup}")

    # report
    before=sh(f"systemctl is-active {service}")
    log(f"STATUS_BEFORE {before}")

    # demo upgrade marker
    marker=f'{project}/UPGRADE_{int(time.time())}.txt'
    open(marker,"w").write(task)

    # compile test
    botpy=f"{project}/bot.py"

    if os.path.exists(botpy):
        compile_check=sh(f"/root/sameer_ai_manager/venv/bin/python -m py_compile {botpy}")

        if compile_check.strip():
            log(f"COMPILE_FAILED {compile_check}")

            sh(f"rm -rf {project}")
            sh(f"tar -xzf {backup} -C /")

            sh(f"systemctl restart {service}")

            log("ROLLBACK_DONE")

            return "ROLLBACK_DONE"

    # restart
    sh(f"systemctl restart {service}")
    time.sleep(5)

    after=sh(f"systemctl is-active {service}")
    log(f"STATUS_AFTER {after}")

    if after != "active":

        sh(f"rm -rf {project}")
        sh(f"tar -xzf {backup} -C /")
        sh(f"systemctl restart {service}")

        log("SERVICE_FAIL_ROLLBACK")

        return "SERVICE_FAIL_ROLLBACK"

    log("UPGRADE_SUCCESS")

    return "UPGRADE_SUCCESS"

if __name__ == "__main__":
    print(safe_upgrade(
        "freshtiq_ai_travel_pro",
        "premium_system_test"
    ))
