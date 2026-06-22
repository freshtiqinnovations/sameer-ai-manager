import json,glob,os
REG="/root/sameer_ai_manager/worker_factory/registry/workers.json"
OUT="/root/sameer_ai_manager/worker_manager/state/factory_workers.json"
data=json.load(open(REG))
open(OUT,"w").write(json.dumps({"total":len(data),"workers":data},indent=2))
print("FACTORY_SYNC_OK",len(data))
