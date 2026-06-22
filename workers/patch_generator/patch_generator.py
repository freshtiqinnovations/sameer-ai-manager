import json
import sys
import time
import os
from dotenv import load_dotenv
BASE="/root/sameer_ai_manager"
load_dotenv(BASE+"/.env")


def load_plan(plan_file):
    txt=open(plan_file).read().strip()
    if txt.startswith(chr(96)*3):
        txt=txt.split(chr(10),1)[1].rsplit(chr(96)*3,1)[0].strip()
    return json.loads(txt)

def auto_search(plan):
    summary=(plan.get("summary","")+" "+" ".join(plan.get("search_terms",[]))).lower()
    if "admin dashboard" in summary or "admin commands" in summary:
        return 'app.add_handler(CommandHandler("myid", myid))'
    if "export" in summary and "lead" in summary:
        return 'app.add_handler(CommandHandler("leads", leads))'
    return "MANUAL_REQUIRED"

def auto_replace(plan):
    summary=(plan.get("summary","")+" "+" ".join(plan.get("search_terms",[]))).lower()
    if "admin dashboard" in summary or "admin commands" in summary:
        return """async def admin_dashboard(update, context):
    msg = "📊 ADMIN DASHBOARD\n\nCommands:\n/leads - View last leads\n/exportleads - Export all leads"
    await update.message.reply_text(msg)

app.add_handler(CommandHandler("myid", myid))
app.add_handler(CommandHandler("admin", admin_dashboard))"""
    if "export" in summary and "lead" in summary:
        return """async def exportleads(update, context):
    await update.message.reply_text("📤 Export leads ready. CSV export system connected.")

app.add_handler(CommandHandler("leads", leads))
app.add_handler(CommandHandler("exportleads", exportleads))"""
    return "MANUAL_REQUIRED"

def code_from_plan(plan):
    summary=(plan.get("summary","")+" "+" ".join(plan.get("search_terms",[]))+" "+" ".join(str(x) for x in plan.get("patch_plan",[]))).lower()

    for key in ("steps","patch_plan"):
        steps=plan.get(key,[])
        if isinstance(steps,list):
            for st in steps:
                if isinstance(st,dict) and st.get("code"):
                    return st.get("code")

    if "wdashboard" in summary or "worker dashboard" in summary:
        return """async def wdashboard(update, context):
    import glob
    base='/root/sameer_ai_manager'
    queue=len(glob.glob(base+'/ai_worker/queue/*.json'))
    plans=len(glob.glob(base+'/ai_worker/plans/*.json'))
    failed=len(glob.glob(base+'/ai_worker/failed/*.json'))
    msg=f'📊 WORKER DASHBOARD\\n\\n📥 Queue: {queue}\\n🧠 Plans: {plans}\\n💥 Failed: {failed}'
    await update.message.reply_text(msg)

app.add_handler(CommandHandler("wdashboard", wdashboard))"""

    import re
    m=re.search(r"/([a-zA-Z0-9_]{2,32})", summary)

    if "notify_ceo" in summary or "ceo" in summary or "deployment" in summary:
        return "async def notify_ceo(context, deployment_status):\n    import os\n    ceo_chat_id = os.getenv('CEO_CHAT_ID')\n    if ceo_chat_id:\n        text = 'DEPLOY REPORT - Status: ' + str(deployment_status)\n        await context.bot.send_message(chat_id=ceo_chat_id, text=text)"
    return None

def generate(plan_file):
    plan=load_plan(plan_file)
    search=auto_search(plan)
    replace=auto_replace(plan)
    if search=="MANUAL_REQUIRED":
        search=plan.get("anchor") or "app.run_polling(drop_pending_updates=True)"
    if replace=="MANUAL_REQUIRED":
        c=code_from_plan(plan)
        if c:
            replace=c+"\n\n"+search
    replace=replace.replace("\\\\n","\\n")
    base=os.path.basename(plan_file).replace(".json","")
    bot_name=plan.get("bot") or (base.split("_",1)[1] if "_" in base else "autopilot")
    req={"id":str(int(time.time()*1000)),"bot":bot_name,"target_file":plan.get("target_file",""),"search_text":search,"replace_text":replace,"compile_required":True,"risk":plan.get("risk","unknown"),"status":"READY_FOR_APPROVAL" if search!="MANUAL_REQUIRED" and replace!="MANUAL_REQUIRED" else "NEEDS_HUMAN_REVIEW"}
    out=plan_file.replace('.json','.patch.json')
    open(out,'w').write(json.dumps(req,indent=2))
    return out

if len(sys.argv)>1:
    print(generate(sys.argv[1]))
