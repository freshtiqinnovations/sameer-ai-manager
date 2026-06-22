import os, json, subprocess, urllib.request
from datetime import datetime

BASE="/root/.openclaw/workspace/memory_core"
ENV_FILES=["/root/sameer_ai_manager/.env","/root/.openclaw/.env","/root/openclaw/openclaw.env"]
CHAT_MEM="/root/.openclaw/workspace/memory_core/CONVERSATION_MEMORY.md"

def read_files():
    names=["MASTER_MEMORY.md","PROJECT_REGISTRY.md","SERVICE_REGISTRY.md","CURRENT_STATUS.md","LESSONS_LEARNED.md","KNOWN_BOTS.md","ENGINEER_RULES.md","OPENCLAW_LEARNED.md"]
    out=[]
    for n in names:
        p=os.path.join(BASE,n)
        if os.path.exists(p):
            out.append(f"\n--- {n} ---\n"+open(p,errors="ignore").read()[:3000])
    if os.path.exists(CHAT_MEM):
        out.append("\n--- RECENT CHAT MEMORY ---\n"+open(CHAT_MEM,errors="ignore").read()[-3000:])
    return "\n".join(out)[:18000]

def sh(cmd):
    try:
        return subprocess.getoutput(cmd)[:2500]
    except Exception as e:
        return str(e)

def evidence(q):
    t=q.lower()
    out=[]
    if any(x in t for x in ["status","service","active","bot","project","website","app","server","vps","sameer","freshtiq","salama","trader","openclaw"]):
        out.append("RUNNING SERVICES:\n"+sh("systemctl list-units --type=service --state=running --no-pager --no-legend | egrep 'sameer|openclaw|freshtiq|salama|autopilot|trader|restaurant' || true"))
        out.append("CUSTOMER PROJECTS:\n"+sh("find /root/workspaces/customers -maxdepth 2 -type d 2>/dev/null | egrep 'freshtiq|salama|autopilot|trader|restaurant|bot|erp|travel' | head -150"))
        out.append("DISK/RAM:\n"+sh("df -h / && free -h && uptime"))
        out.append("SAMEER AI REAL GIT SUMMARY:\n"+sh("cd /root/sameer_ai_manager && echo TOTAL_DIRTY=$(git status --short | wc -l) && echo SOURCE_DIRTY=$(git status --short | egrep -v 'venv/|full_backup/|backups/|__pycache__|\\.pyc|\\.log|\\.jsonl|\\.bak' | wc -l) && git status --short | awk '{print $2}' | cut -d/ -f1-2 | sort | uniq -c | sort -nr | head -20"))
    if any(x in t for x in ["dirty","git","backup","commit","source"]):
        out.append("GIT CLEAN SUMMARY:\n"+sh("cd /root/sameer_ai_manager && git status --short | egrep -v 'venv/|full_backup/|backups/|__pycache__|\\.pyc|\\.log|\\.jsonl' | head -80"))
    return "\n\n".join(out)[:9000]


def ollama_ask(prompt):
    try:
        k = key()
        if not k:
            return "DeepSeek API key nahi mili. .env me DEEPSEEK_API_KEY set karo."
        prompt = prompt[-12000:]
        data=json.dumps({
            "model":"deepseek-chat",
            "messages":[
                {"role":"system","content":"Tum Sameer bhai ke Hinglish AI agent ho. Short, practical, kaam wali baat karo. Raw JSON/debug mat dikhao."},
                {"role":"user","content":prompt}
            ],
            "temperature":0.3,
            "max_tokens":900
        }).encode()
        req=urllib.request.Request(
            "https://api.deepseek.com/chat/completions",
            data=data,
            headers={"Content-Type":"application/json","Authorization":"Bearer "+k}
        )
        with urllib.request.urlopen(req,timeout=90) as r:
            j=json.loads(r.read())
        return j["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return "DeepSeek error: " + str(e)[:250]

def key():
    k=os.getenv("DEEPSEEK_API_KEY")
    if k: return k
    for f in ENV_FILES:
        if os.path.exists(f):
            for line in open(f,errors="ignore"):
                if line.startswith("DEEPSEEK_API_KEY="):
                    return line.split("=",1)[1].strip().strip('"').strip("'")
    return ""

def save_chat(q,a):
    os.makedirs(os.path.dirname(CHAT_MEM),exist_ok=True)
    with open(CHAT_MEM,"a") as f:
        f.write(f"\n[{datetime.now()}]\nUSER: {q}\nAI: {a[:1000]}\n")


def ask(q):
    q=(q or "").strip()
    low=q.lower()

    try:
        if low in ["status","health","report","services","backup"] or low.startswith("restart "):
            import command_center, json
            r=command_center.execute(q)
            ans=json.dumps(r, ensure_ascii=False, indent=2)
            save_chat(q, ans)
            return ans[:3500]
    except Exception as e:
        pass

    try:
        if low in ["factory","factory status","/factory","brain status","/brain_status"]:
            import factory_brain
            r=factory_brain.factory_status()
            ans=r["display"] if isinstance(r,dict) and "display" in r else str(r)
            save_chat(q, ans)
            return ans[:3500]
    except Exception as e:
        pass

    # Long engineering / Android / UI rebuild prompts must go to DeepSeek, not smart_router.
    engineer_words=["task:","patch","fix","rebuild","redesign","android","apk","ui","xml","material","binance","playstore","gradle","java","kotlin","github"]
    force_deepseek=any(x in low for x in engineer_words)

    try:
        work=["banao","build","create","generate","app","bot","website","code"]
        if any(x in low for x in work) and not force_deepseek:
            import smart_router, json
            r=smart_router.route(q)
            ans="TASK ROUTED\n"+json.dumps(r, ensure_ascii=False, indent=2)
            save_chat(q, ans)
            return ans[:3500]
    except Exception as e:
        pass

    mem=read_files()
    try:
        rules=open("/root/sameer_ai_manager/openclaw_bridge/ENGINEER_RULES.md").read()
    except Exception:
        rules=""
    ev=evidence(q)
    prompt=f"""You are Sameer OpenClaw Operator.\n\nENGINEER RULES:\n{rules}\n\n

MEMORY:
{mem}

REAL VPS EVIDENCE:
{ev}

USER:
{q}
"""
    ans=ollama_ask(prompt)
    save_chat(q, ans)
    return ans
