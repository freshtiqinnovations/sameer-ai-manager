import json
REG="/root/sameer_ai_manager/worker_factory/registry/workers.json"
data=json.load(open(REG))
print("TOTAL_WORKERS",len(data))
print("---")
for w in data:
 print(w["worker_name"],"|",w["service"],"|",w["status"])
