
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
import os
import json
import time
import shutil
import pathlib
import subprocess

BASE="/root/sameer_ai_manager"
PLAN_DIR=BASE+"/ai_worker/plans"
PATCH_DIR=BASE+"/ai_worker/patches"
BACKUP_DIR="/root/backups/ai_patch_engine"

BOT_MAP={
 "autopilot_hub_bot":{"path":"/root/monster_bot","main":"admin_panel.py","service":"autopilot_hub_bot.service"},
 "sameer_ai_manager":{"path":"/root/sameer_ai_manager","main":"bot.py","service":"sameer_ai_manager.service"},
 "freshtiq":{"path":"/root/workspaces/customers/freshtiq_ai_travel_pro","main":"bot.py","service":"freshtiq_ai_travel_pro.service"},
 "salama":{"path":"/root/workspaces/customers/el_salama_radiator_factory","main":"bot.py","service":"salama_radiator_bot.service"}
}

def sh(cmd):
    return subprocess.getoutput(cmd).strip()

def ensure_dirs():
    os.makedirs(PLAN_DIR, exist_ok=True)
    os.makedirs(PATCH_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)

def backup_project(bot, project):
    ts=int(time.time())
    out=f"{BACKUP_DIR}/{bot}_{ts}.tar.gz"
    rc=subprocess.call(f"tar -czf {out} {project} 2>/dev/null", shell=True)
    if rc not in (0,1): raise Exception("BACKUP_FAILED")
    # Auto-retention: keep latest 5 per bot
    import glob
    files=sorted(glob.glob(f"{BACKUP_DIR}/{bot}_*.tar.gz"), key=os.path.getmtime)
    while len(files)>5:
        os.remove(files.pop(0))
    return out

def validate_bot(bot):
    info=BOT_MAP.get(bot)
    if not info:
        raise Exception("UNKNOWN_BOT "+bot)
    project=info["path"]
    main=pathlib.Path(project, info["main"])
    if not os.path.isdir(project):
        raise Exception("PROJECT_NOT_FOUND "+project)
    if not main.exists():
        raise Exception("MAIN_FILE_NOT_FOUND "+str(main))
    return info, project, main

def compile_file(main):
    out=sh(f"python3 -m py_compile {main}")
    if out:
        raise Exception("COMPILE_FAILED "+out[:700])
    return True

def restart_service(service):
    subprocess.check_call(f"systemctl restart {service}", shell=True)
    time.sleep(2)
    status=sh(f"systemctl is-active {service}")
    if status!="active":
        raise Exception("SERVICE_NOT_ACTIVE "+service+"="+status)
    return status

def dry_run(bot):
    ensure_dirs()
    info, project, main = validate_bot(bot)
    backup = backup_project(bot, project)
    compile_file(main)
    return {"ok":True,"bot":bot,"main":str(main),"service":info["service"],"backup":backup,"mode":"dry_run"}

if __name__=="__main__":
    import sys
    bot=sys.argv[1] if len(sys.argv)>1 else "autopilot"
    mode=sys.argv[2] if len(sys.argv)>2 else "dry_run"
    if mode=="dry_run":
        print(json.dumps(dry_run(bot), indent=2))
    else:
        print(json.dumps({"ok":False,"error":"UNKNOWN_MODE"}, indent=2))


def apply_text_patch(bot, search_text, replace_text):
    info, project, main = validate_bot(bot)
    backup = backup_project(bot, project)
    src = main.read_text(errors="ignore")
    if search_text not in src:
        if "app.run_polling" in search_text:
            lines=src.splitlines()
            for i,line in enumerate(lines):
                if "app.run_polling" in line:
                    lines[i]=replace_text
                    src="\\n".join(lines)+"\\n"
                    break
            else:
                raise Exception("SEARCH_NOT_FOUND")
        else:
            raise Exception("SEARCH_NOT_FOUND")
    else:
        src = src.replace(search_text, replace_text, 1)
    main.write_text(src)
    compile_file(main)
    restart_service(info["service"])
    return {"ok":True,"backup":backup,"file":str(main)}


def apply_file_patch(file_path, search_text, replace_text):
    f=pathlib.Path(file_path)
    if not f.exists():
        raise Exception("FILE_NOT_FOUND "+str(f))
    backup=str(f)+".bak_"+str(int(time.time()))
    shutil.copy2(f, backup)
    src=f.read_text(errors="ignore")
    if search_text not in src:
        raise Exception("SEARCH_NOT_FOUND")
    f.write_text(src.replace(search_text, replace_text, 1))
    return {"ok":True,"file":str(f),"backup":backup}


def rollback_file(file_path, backup_path):
    f=pathlib.Path(file_path)
    b=pathlib.Path(backup_path)
    if not b.exists():
        raise Exception("BACKUP_NOT_FOUND")
    shutil.copy2(b,f)
    return {"ok":True,"restored":str(f),"from":str(b)}


def verify_service(service):
    status=sh(f"systemctl is-active {service}")
    return {"service":service,"status":status,"ok":status=="active"}


def safe_live_patch(bot, search_text, replace_text):
    info, project, main = validate_bot(bot)
    backup_file = str(main)+".safe_"+str(int(time.time()))
    shutil.copy2(main, backup_file)
    try:
        result = apply_text_patch(bot, search_text, replace_text)
        compile_file(main)
        restart_service(info["service"])
        verify = verify_service(info["service"])
        if not verify["ok"]:
            raise Exception("VERIFY_FAILED")
        result["verify"]=verify
        result["safe_backup_file"]=backup_file
        return result
    except Exception as e:
        rollback_file(str(main), backup_file)
        restart_service(info["service"])
        raise Exception("SAFE_PATCH_FAILED_ROLLED_BACK "+str(e))

def rollback_bot_file(bot, backup_file):
 info, project, main = validate_bot(bot)
 result = rollback_file(str(main), backup_file)
 compile_file(main)
 restart_service(info["service"])
 verify = verify_service(info["service"])
 result["bot"] = bot
 result["service"] = info["service"]
 result["verify"] = verify
 return result
