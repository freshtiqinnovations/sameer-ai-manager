import json,time,sys,os
name=sys.argv[1] if len(sys.argv)>1 else "demo_worker"
out=f"/root/sameer_ai_manager/worker_factory/generated/{name}.json"
data={"worker_name":name,"created":time.time(),"status":"generated"}
open(out,"w").write(json.dumps(data,indent=2))
print("WORKER_GENERATED",out)
