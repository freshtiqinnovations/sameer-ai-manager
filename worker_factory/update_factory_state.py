import json,time
REG="/root/sameer_ai_manager/worker_factory/registry/workers.json"
STATE="/root/sameer_ai_manager/worker_factory/factory_state.json"
data=json.load(open(REG))
status={}
for w in data:
 status[w.get("status","unknown")]=status.get(w.get("status","unknown"),0)+1
out={"time":time.time(),"total_workers":len(data),"status_count":status,"mode":"AUTO_WORKER_NETWORK"}
open(STATE,"w").write(json.dumps(out,indent=2))
print("FACTORY_STATE_UPDATED")
print(json.dumps(out,indent=2))
