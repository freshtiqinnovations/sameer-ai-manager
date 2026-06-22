import time,os
LOG="/root/sameer_ai_manager/worker_factory/generated/demo_service_worker.log"
while True:
 open(LOG,"a").write(str(time.time())+" demo_service_worker alive\n")
 time.sleep(60)
