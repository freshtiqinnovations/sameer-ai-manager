import json,glob,os,time
FAILED="/root/sameer_ai_manager/ai_worker/failed"
files=sorted(glob.glob(FAILED+"/*.json"),reverse=True)[:10]
print("FAILURE_FILES",len(files))
for f in files:
 print(os.path.basename(f))
