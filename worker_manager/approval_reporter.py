import os,json,time,sys
PENDING="/root/sameer_ai_manager/approval_queue/pending"
os.makedirs(PENDING,exist_ok=True)

def _infer_mode(task_text, dry_run=None, mode=None):
    if mode:
        return str(mode).strip().upper()
    if isinstance(dry_run, dict) and dry_run.get("mode"):
        return str(dry_run.get("mode")).strip().upper()
    t=str(task_text or "").lower()
    if any(x in t for x in ["report only", "no patch", "no queue", "no restart", "plan only", "do not patch"]):
        return "REPORT_ONLY"
    return "APPROVAL_REQUIRED"

def _infer_details(task_text, dry_run=None, details=None):
    if details:
        return str(details)
    if isinstance(dry_run, dict) and dry_run.get("details"):
        return str(dry_run.get("details"))
    return str(task_text or "")

def create_report(bot,task,plan_path,dry_run,mode=None,details=None):
    rid=str(int(time.time()*1000))
    mode=_infer_mode(task, dry_run, mode)
    details=_infer_details(task, dry_run, details)
    data={"id":rid,"bot":bot,"task":task,"details":details,"mode":mode,"plan_path":plan_path,"dry_run":dry_run,"status":"pending_approval","created":time.time()}
    path=f"{PENDING}/{rid}.json"
    open(path,"w").write(json.dumps(data,indent=2))
    return path

if __name__=="__main__":
    bot=sys.argv[1]; task=sys.argv[2]; plan=sys.argv[3]; dry=json.loads(sys.argv[4])
    print(create_report(bot,task,plan,dry))
