import json,time,sys,os
name=sys.argv[1] if len(sys.argv)>1 else "new_worker"
BASE="/root/sameer_ai_manager/worker_factory"
GEN=BASE+"/generated"
os.makedirs(GEN,exist_ok=True)
py=f"{GEN}/{name}.py"
open(py,"w").write("import time\nwhile True:\n time.sleep(60)\n")
print("WORKER_FILE_CREATED",py)
