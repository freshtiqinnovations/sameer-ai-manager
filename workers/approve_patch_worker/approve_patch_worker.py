import os
import sys
import json
import time
import shutil
sys.path.append("/root/sameer_ai_manager")
from ai_brain.patch_engine import safe_live_patch

PENDING="/root/sameer_ai_manager/approval_queue/pending"
APPROVED="/root/sameer_ai_manager/approval_queue/approved"
REJECTED="/root/sameer_ai_manager/approval_queue/rejected"
LOG="/root/sameer_ai_manager/workers/approve_patch_worker/approve_patch_worker.log"

for d in [PENDING,APPROVED,REJECTED,os.path.dirname(LOG)]:
    os.makedirs(d, exist_ok=True)

def log(x):
    open(LOG,"a").write(str(time.time())+" | "+str(x)+"\n")

def approve(report_id, search_text, replace_text):
    src=os.path.join(PENDING, report_id+".json")
    if not os.path.exists(src):
        raise Exception("REPORT_NOT_FOUND")
    data=json.load(open(src))
    bot=data.get("bot")
    if not bot:
        raise Exception("BOT_MISSING")
    result=safe_live_patch(bot, search_text, replace_text)
    data["patch_result"]=result
    data["status"]="approved_applied"
    dst=os.path.join(APPROVED, report_id+".json")
    open(dst,"w").write(json.dumps(data,indent=2))
    shutil.move(src, src+".done")
    log("APPROVED_APPLIED "+report_id)
    return dst

if len(sys.argv)>3:
    rid=sys.argv[1]
    search=sys.argv[2]
    replace=sys.argv[3]
    print(approve(rid, search, replace))
