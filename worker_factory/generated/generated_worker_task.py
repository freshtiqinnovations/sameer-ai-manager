import time,json,os
OUT="/root/sameer_ai_manager/worker_manager/state/generated_worker_output.json"
data={"worker":"generated_worker","task":"factory_self_check","status":"completed","time":time.time()}
open(OUT,"w").write(json.dumps(data,indent=2))
print("GENERATED_WORKER_TASK_DONE")
