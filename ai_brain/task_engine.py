import os, json, datetime

BASE="/root/sameer_ai_manager/ai_brain/tasks"

def save_idea(text):
    ts=datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path=f"{BASE}/{ts}.json"

    data={
        "time": ts,
        "idea": text,
        "status": "pending"
    }

    with open(path,"w") as f:
        json.dump(data,f,indent=2)

    return path

def list_pending():
    out=[]
    for x in os.listdir(BASE):
        if x.endswith(".json"):
            p=f"{BASE}/{x}"
            try:
                d=json.load(open(p))
                if d.get("status")=="pending":
                    out.append(d)
            except:
                pass
    return out
