import sys
sys.path.append("/root/sameer_ai_manager")
import json,sys
from ai_brain.patch_engine import safe_live_patch

def deploy(patch_file):
    d=json.load(open(patch_file))
    if d.get("status")!="READY_FOR_APPROVAL":
        return {"ok":False,"reason":"NOT_APPROVED"}
    return safe_live_patch(d["bot"],d["search_text"],d["replace_text"])

if len(sys.argv)>1:
    print(deploy(sys.argv[1]))
