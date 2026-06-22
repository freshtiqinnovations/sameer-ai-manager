import json,sys,time
REG="/root/sameer_ai_manager/worker_factory/registry/workers.json"
name=sys.argv[1] if len(sys.argv)>1 else "demo_worker"
data=json.load(open(REG))
if not any(w.get("worker_name")==name for w in data):
 data.append({"worker_name":name,"service":"future_"+name+".service","status":"generated","created":time.strftime("%Y-%m-%d")})
 open(REG,"w").write(json.dumps(data,indent=2))
print("REGISTERED",name)
