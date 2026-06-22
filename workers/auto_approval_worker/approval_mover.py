import os,json,shutil,sys
P="/root/sameer_ai_manager/approval_queue/pending"
A="/root/sameer_ai_manager/approval_queue/approved"
R="/root/sameer_ai_manager/approval_queue/rejected"
def move(report_id,status,note=""):
    src=os.path.join(P,report_id+".json")
    if not os.path.exists(src): return "REPORT_NOT_FOUND"
    d=json.load(open(src)); d["status"]=status; d["note"]=note
    dst=os.path.join(A if status.startswith("approved") else R, report_id+".json")
    open(dst,"w").write(json.dumps(d,indent=2)); os.remove(src); return dst
if len(sys.argv)>2:
    print(move(sys.argv[1],sys.argv[2]," ".join(sys.argv[3:])))
