import os
import sys
import json
import time
sys.path.append("/root/sameer_ai_manager")
from ai_brain.auto_coder import plan as ai_plan

PLAN_DIR="/root/sameer_ai_manager/ai_worker/plans"
os.makedirs(PLAN_DIR, exist_ok=True)

def run(bot, task):
    plan_text=ai_plan(bot, task)
    path=f"{PLAN_DIR}/{int(time.time())}_{bot}.json"
    open(path,"w").write(json.dumps(plan_text,indent=2) if isinstance(plan_text,dict) else str(plan_text))
    return path

if __name__=="__main__":
    bot=sys.argv[1]
    task=" ".join(sys.argv[2:])
    print(run(bot, task))
