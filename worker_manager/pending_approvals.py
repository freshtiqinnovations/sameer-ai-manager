import os,json
P="/root/sameer_ai_manager/approval_queue/pending"
def main():
    files=sorted([x for x in os.listdir(P) if x.endswith(".json")])
    if not files:
        print("NO_PENDING_APPROVALS"); return
    for f in files:
        d=json.load(open(os.path.join(P,f)))
        print(f"{d.get('id')} | {d.get('bot')} | {d.get('task')} | {d.get('status')}")
main()
