import json
REG="/root/sameer_ai_manager/worker_factory/registry/workers.json"
data=json.load(open(REG))
active=sum(1 for x in data if x["status"]=="active")
planned=sum(1 for x in data if x["status"]=="planned")
print("FACTORY_STATUS")
print("TOTAL",len(data))
print("ACTIVE",active)
print("PLANNED",planned)
