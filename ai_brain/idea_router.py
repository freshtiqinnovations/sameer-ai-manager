import os
import json
import time
import datetime

QUEUE="/root/sameer_ai_manager/ai_worker/queue"

os.makedirs(QUEUE,exist_ok=True)

def create_upgrade_task(bot,task):

    ts=str(int(time.time()*1000))

    data={
        "time": str(datetime.datetime.now()),
        "bot": bot,
        "task": task,
        "status": "queued"
    }

    path=f"{QUEUE}/{ts}.json"

    with open(path,"w") as f:
        json.dump(data,f,indent=2)

    return path
