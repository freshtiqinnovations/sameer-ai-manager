import json,sys

def check(patch_file):
    d=json.load(open(patch_file))
    bad=[]
    s=d.get("search_text","")
    r=d.get("replace_text","")
    if not s or s=="MANUAL_REQUIRED": bad.append("BAD_SEARCH_TEXT")
    if not r or r=="MANUAL_REQUIRED": bad.append("BAD_REPLACE_TEXT")
    if "\\\"" in s or "\\\"" in r: bad.append("ESCAPED_QUOTES")
    if "placeholder" in r.lower() or "dummy" in r.lower() or "fake" in r.lower(): bad.append("FAKE_PLACEHOLDER")
    if "testing " in r.lower() or "test_worker_dashboard" in r.lower(): bad.append("TEST_ONLY_PATCH")
    if "dashboard" in (d.get("task") or "").lower() and "reply_text" in r.lower() and "os.listdir" not in r.lower(): bad.append("NO_LIVE_COUNTS")
    task=(d.get("task") or "").lower()
    if "dashboard" in task and "notify_ceo" in r.lower(): bad.append("TASK_MISMATCH")
    if "dashboard" in task and "worker_dashboard" not in r.lower(): bad.append("MISSING_DASHBOARD_FUNCTION")
    if "wdashboard" in task and "commandhandler" not in r.lower(): bad.append("MISSING_COMMAND_HANDLER")
    return {"ok":len(bad)==0,"issues":bad,"status":"READY" if not bad else "NEEDS_HUMAN_REVIEW"}

if len(sys.argv)>1:
    print(json.dumps(check(sys.argv[1]),indent=2))
