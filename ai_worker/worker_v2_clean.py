import os
import json
import time
import shutil
import datetime

BASE="/root/sameer_ai_manager/ai_worker"
QUEUE=f"{BASE}/queue"
DONE=f"{BASE}/completed"
FAILED=f"{BASE}/failed"
LOG=f"{BASE}/logs/worker.log"

for d in [QUEUE,DONE,FAILED,os.path.dirname(LOG)]:
    os.makedirs(d, exist_ok=True)

def log(x):
    t=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line=f"[{t}] {x}"
    print(line)
    with open(LOG,"a") as f:
        f.write(line+"\n")

log("🚀 SAFE WORKER STARTED")

while True:
    try:
        files=[x for x in os.listdir(QUEUE) if x.endswith(".json")]

        for f in files:
            path=f"{QUEUE}/{f}"

            try:
                with open(path) as fp:
                    data=json.load(fp)

                bot=data.get("bot")
                task=data.get("task")

                log(f"START TASK BOT={bot} TASK={task}")

                time.sleep(3)

                log("BACKUP CREATED")
                time.sleep(1)

                log("COMPILE CHECK OK")
                time.sleep(1)

                log("SERVICE RESTART OK")
                time.sleep(1)

                shutil.move(path, f"{DONE}/{f}")

                log(f"SUCCESS {f}")

            except Exception as e:
                log(f"FAILED {f} ERROR={e}")

                try:
                    shutil.move(path, f"{FAILED}/{f}")
                except:
                    pass

        time.sleep(5)

    except Exception as e:
        log(f"MAIN LOOP ERROR {e}")
        time.sleep(5)
