import json,sys,os

def find_patch(report_file):
    r=json.load(open(report_file))
    plan=r.get("plan_path","")
    patch=plan.replace(".json",".patch.json")
    if os.path.exists(patch):
        return patch
    return ""

if len(sys.argv)>1:
    print(find_patch(sys.argv[1]))
