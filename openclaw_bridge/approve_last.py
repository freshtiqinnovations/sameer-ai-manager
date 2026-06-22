#!/usr/bin/env python3
import json, sys, time
from pathlib import Path
BRIDGE=Path("/root/sameer_ai_manager/openclaw_bridge")
DONE=BRIDGE/"tasks_done.jsonl"
INBOX=BRIDGE/"tasks_inbox.jsonl"
rows=[]
for line in DONE.read_text().splitlines():
    try: rows.append(json.loads(line))
    except: pass
pending=[r for r in rows if r.get("result",{}).get("status")=="pending_approval"]
if not pending:
    print("NO_PENDING_APPROVAL"); sys.exit(1)
t=pending[-1]
t["approved"]=True
t["id"]="approved_"+str(int(time.time()))
t["retries"]=0
t["source"]="manual_approval"
t.pop("completed_at",None)
t.pop("result",None)
with open(INBOX,"a") as f:
    f.write(json.dumps(t)+"\n")
print("APPROVED_REQUEUED", t["type"], t["id"])
