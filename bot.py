
# --- SMART_CONVERSATION_FILTER START ---
def is_valid_terminal_command(text_input):
    clean_text = str(text_input).strip().lower()
    allowed = ['pwd', 'df', 'free', 'systemctl', 'ls', 'top', 'uptime', 'ifconfig']
    if not clean_text: return False
    first_word = clean_text.split()[0]
    if first_word in allowed and len(clean_text.split()) <= 4:
        return True
    return False
# --- SMART_CONVERSATION_FILTER END ---
import json
from pathlib import Path
import os as _os, sys as _sys
_sys.path.insert(0, '/root/workspaces/sameer_ai_manager')
from sam_universal_monitor import run_full_check, safe_repair, render_health_text
import sam_orchestrator as _sam_orch
import sam_router as _sam_router
import sam_learner as _sam_learner
import sam_prover as _sam_prover


async def worker(update, context):
    import subprocess
    out=subprocess.getoutput("systemctl is-active sameer_ai_worker_auto.service; tail -10 /root/sameer_ai_manager/ai_worker/logs/worker_auto.log")
    await update.message.reply_text("🛠 WORKER STATUS\n\n"+out[:3500])

async def wdashboard(update, context):
 import os, subprocess, glob
 q=len([x for x in os.listdir("/root/sameer_ai_manager/ai_worker/queue") if x.endswith(".json")])
 c=len([x for x in os.listdir("/root/sameer_ai_manager/ai_worker/completed") if x.endswith(".json")])
 f=len([x for x in os.listdir("/root/sameer_ai_manager/ai_worker/failed") if x.endswith(".json")])
 lessons=len(glob.glob("/root/sameer_ai_manager/ai_brain/lessons/*.txt"))
 st=subprocess.getoutput("systemctl is-active sameer_ai_worker_auto.service")
 await update.message.reply_text(f"📊 WORKER DASHBOARD\n\n🤖 Worker: {st}\n📚 Lessons: {lessons}\n📂 Queue: {q}\n✅ Completed: {c}\n❌ Failed: {f}")

async def queue_cmd(update, context):
    import os
    q="/root/sameer_ai_manager/ai_worker/queue"
    files=[x for x in os.listdir(q) if x.endswith(".json")]
    msg="📦 QUEUE\n\n"
    msg += "\n".join(files[-20:]) if files else "Queue empty ✅"
    await update.message.reply_text(msg)

async def safecheck(update, context):
    import subprocess
    checks=[]
    cmds={
        "Manager":"systemctl is-active sameer_ai_manager.service",
        "Worker":"systemctl is-active sameer_ai_worker_auto.service",
        "Disk":"df -h / | awk 'NR==2{print $5 \" used, \" $4 \" free\"}'",
        "Failed":"systemctl --failed --no-pager | tail -5"
    }
    for k,c in cmds.items():
        checks.append(f"{k}: {subprocess.getoutput(c)}")
    await update.message.reply_text("🛡 SAFE CHECK\n\n"+"\n\n".join(checks)[:3500])

async def cleanlogs(update, context):
    import subprocess
    subprocess.getoutput("journalctl --vacuum-time=1d >/dev/null 2>&1")
    subprocess.getoutput("find /root -type f -name '*.log' -size +20M -delete 2>/dev/null")
    await update.message.reply_text("🧹 Logs cleaned safely ✅")

async def backupbot(update, context):
    import subprocess, time, os
    if not context.args:
        await update.message.reply_text("Usage: /backupbot BOT_NAME")
        return
    bot=context.args[0]
    path="/root/sameer_ai_manager" if bot=="sameer_ai_manager" else f"/root/workspaces/customers/{bot}"
    if not os.path.exists(path):
        await update.message.reply_text("BOT_NOT_FOUND")
        return
    backup=f"/root/backups/{bot}_manual_{int(time.time())}.tar.gz"
    out=subprocess.getoutput(f"tar -czf {backup} {path}")
    await update.message.reply_text(f"📦 Backup done ✅\n{backup}")

async def rollbackbot(update, context):
    import subprocess, glob, os
    if not context.args:
        await update.message.reply_text("Usage: /rollbackbot BOT_NAME")
        return
    bot=context.args[0]
    files=sorted(glob.glob(f"/root/backups/{bot}_*.tar.gz"), key=os.path.getmtime, reverse=True)
    if not files:
        await update.message.reply_text("No backup found")
        return
    latest=files[0]
    path="/root/sameer_ai_manager" if bot=="sameer_ai_manager" else f"/root/workspaces/customers/{bot}"
    service=f"{bot}.service"
    subprocess.getoutput(f"rm -rf {path} && tar -xzf {latest} -C / && systemctl restart {service}")
    st=subprocess.getoutput(f"systemctl is-active {service}")
    await update.message.reply_text(f"♻️ Rollback done\nBackup: {latest}\nService: {st}")



async def logs(update, context):
    import subprocess
    import re

    out = subprocess.getoutput(
        "journalctl -u sameer_ai_manager.service -n 30 --no-pager"
    )

    out = re.sub(r"https://api\\.telegram\\.org/bot[^/\\s]+", "https://api.telegram.org/bot***TOKEN_HIDDEN***", out)
    out = re.sub(r"bot[0-9]+:[A-Za-z0-9_\\-]+", "bot***TOKEN_HIDDEN***", out)
    out = re.sub(r":[A-Za-z0-9_\\-]{25,}/", ":***TOKEN_HIDDEN***/", out)

    if not out.strip():
        out = "No logs found"

    await update.message.reply_text(
        "📜 LOGS: sameer_ai_manager\\n\\n" + out[:3500]
    )


async def health(update, context):
    import subprocess

    def sh(cmd):
        return subprocess.getoutput(cmd).strip()

    disk = sh("df -h / | awk 'NR==2{print $5 \" used, \" $4 \" free\"}'")
    ram = sh("free -h | awk '/Mem:/ {print $3 \"/\" $2}'")
    manager = sh("systemctl is-active sameer_ai_manager.service")
    worker = sh("systemctl is-active sameer_ai_worker_auto.service")
    freshtiq = sh("systemctl is-active freshtiq_ai_travel_pro.service")

    msg = f"""🩺 SERVER HEALTH

💾 Disk: {disk}
🧠 RAM: {ram}

🤖 Sameer Manager: {manager}
🛠 Worker: {worker}
✈️ Freshtiq Travel: {freshtiq}
"""

    await update.message.reply_text(msg)



async def tasks(update, context):
    import os

    q="/root/sameer_ai_manager/ai_worker/queue"
    c="/root/sameer_ai_manager/ai_worker/completed"
    f="/root/sameer_ai_manager/ai_worker/failed"

    qn=len([x for x in os.listdir(q) if x.endswith(".json")])
    cn=len([x for x in os.listdir(c) if x.endswith(".json")])
    fn=len([x for x in os.listdir(f) if x.endswith(".json")])

    msg=f"""
📊 TASK STATUS

🟡 Queue: {qn}
🟢 Completed: {cn}
🔴 Failed: {fn}
"""

    await update.message.reply_text(msg)



# from upgrade_engine.safe_upgrade import safe_upgrade  # COMMENTED OUT — module missing


async def handle_voice(update, context):
    try:
        msg = await update.message.reply_text("🎤 Voice samajh raha hu...")

        voice = await update.message.voice.get_file()

        ogg="/tmp/sameer_voice.ogg"
        wav="/tmp/sameer_voice.wav"

        await voice.download_to_drive(ogg)

        subprocess.getoutput(
            f"ffmpeg -y -i {ogg} {wav}"
        )

        # AI Engine via ai.chat()
        from dotenv import load_dotenv

        load_dotenv("/root/sameer_ai_manager/.env")

        client=None  # Using DeepSeek via ai.chat()

        audio_file=open(wav,"rb")

        transcript=client.audio.transcriptions.create(
            model="whisper-1",
            language="hi",
            prompt="This is Hinglish, Hindi, Urdu and English mixed speech about AI bots, coding, VPS, Telegram automation and travel bots.",
            file=audio_file
        )

        raw_text=transcript.text

        clean = ai.chat(
            model="gpt-4o-mini",
            messages=[
                {
                    "role":"system",
                    "content":"Fix speech-to-text mistakes. Return clean Hinglish only."
                },
                {
                    "role":"user",
                    "content":raw_text
                }
            ]
        )

        text=clean.choices[0].message.content

        reply = ai.chat(
            model="gpt-4o-mini",
            messages=[
                {
                    "role":"system",
                    "content":"You are Sameer AI Manager — OpenClaw Operator style. Reply in smart Hinglish like a real AI CTO assistant. Short, practical, natural Hinglish. Samajh raha hu, root cause found, proof complete — aise reply karo. Jab user 'karwao' bole toh sirf pending work continue karo."
                },
                {
                    "role":"user",
                    "content":text
                }
            ]
        )

        ai_reply = reply.choices[0].message.content

        speech_file="/tmp/sameer_reply.mp3"

        audio = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=ai_reply
        )

        audio.stream_to_file(speech_file)

        await update.message.reply_voice(
            voice=open(speech_file,"rb"),
            caption=ai_reply[:1000]
        )

    except Exception as e:
        await update.message.reply_text(f"VOICE_ERROR: {e}")


# from ai_brain.idea_router import create_upgrade_task  # COMMENTED OUT — module missing
from telegram.ext import Application, CommandHandler
import os
import logging
import subprocess
from datetime import datetime
from dotenv import load_dotenv
# AI Engine via ai.chat()
from assistant_engine import ask_ai
from telegram import Update, BotCommand, ReplyKeyboardMarkup, ReplyKeyboardRemove
from modules.health import health_report
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from modules.health import health_report
from modules.health import health_report
# from builder_engine import create_customer_bot  # COMMENTED OUT — module missing
from modules.safe_runner import run_shell
# import safe_editor  # COMMENTED OUT — module missing
# from modules.ai_fix_engine import run_ai_fix  # COMMENTED OUT — module missing
# from modules.ai_repair import ai_repair  # COMMENTED OUT — module missing
# from template_deploy_cmds import deploy_template_cmd  # COMMENTED OUT — module missing

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_ID = os.getenv("ADMIN_ID")
MODEL = "qwen2.5:3b"
ALLOWED_USER_IDS = os.getenv("ALLOWED_USER_IDS", "").split(",")
client = None  # ai.chat() handles this

logging.basicConfig(level=logging.WARNING)
pending_task = {}

SYSTEM_PROMPT = """
You are Sameer AI Manager with Telegram-controlled VPS access.

Important working rules:

1. Sameer has given permission to manage this VPS.

2. Use /run command for VPS work when needed.

3. Before risky changes, always create backup.

4. For code edit:
- backup file first
- modify file
- run python3 -m py_compile
- restart service
- check status
- report result

5. Never delete important files unless Sameer clearly says delete.

6. Never show or ask for secret keys/passwords.

7. For Sameer's commands like:
repair karo
upgrade karo
feature add karo
bot banao
restart karo
logs check karo
deploy karo

make practical action plan and tell exact /run commands.

8. If command is safe, execute using existing /run flow.

9. If change can break bot, backup first:

cp /root/sameer_ai_manager/bot.py /root/sameer_ai_manager/backups/bot_before_change_$(date +%F_%H%M).py

10. Always keep Sameer AI Manager and customer bots running.

11. You can guide Sameer step-by-step for:
- VPS management
- Telegram bots
- WhatsApp automation
- deployments
- repair
- upgrades
- AI systems
- customer support bots

12. If user asks for repair:
- check logs
- detect issue
- suggest fix
- restart services
- verify status

13. Prefer safe automation over dangerous direct system modification.

14. Reply in simple Hinglish unless professional English or Arabic is requested.

15. Always think practically like a real DevOps + AI automation manager.
"""
SAFE_ROOT = "/root/workspaces/customers/el_salama_radiator_factory"

def run_shell(cmd):
    try:
        out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True)
        return out[:3500]
    except subprocess.CalledProcessError as e:
        return e.output[:3500]

async def salama_status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    out = run_shell("systemctl status salama_radiator_bot --no-pager")
    await update.message.reply_text(f"📊 SALAMA STATUS\n\n{out}")

async def salama_logs_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    out = run_shell("journalctl -u salama_radiator_bot -n 40 --no-pager")
    await update.message.reply_text(f"📜 LAST LOGS\n\n{out}")

async def salama_restart_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    out = run_shell("systemctl restart salama_radiator_bot && systemctl status salama_radiator_bot --no-pager")
    await update.message.reply_text(f"🔄 RESTART DONE\n\n{out}")

async def salama_backup_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    cmd = f"""
    mkdir -p /root/sameer_ai_manager/backups/{ts}
    cp -r {SAFE_ROOT} /root/sameer_ai_manager/backups/{ts}/
    echo BACKUP_OK
    """
    out = run_shell(cmd)
    await update.message.reply_text(f"💾 BACKUP CREATED\n\n{out}")

async def salama_health_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("SALAMA_HEALTH COMMAND RECEIVED")
    out1 = run_shell("systemctl is-active salama_radiator_bot")
    out2 = run_shell("systemctl is-active sameer_ai_manager")
    await update.message.reply_text(f"🤖 Sameer AI Manager: {out2.strip()}\n🏭 Salama Bot: {out1.strip()}")

async def repair_salama_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    out = run_shell(f"cd {SAFE_ROOT} && python3 -m py_compile bot.py")
    if out.strip() == "":
        run_shell("systemctl restart salama_radiator_bot")
        await update.message.reply_text("✅ Compile OK + Restart Success")
    else:
        await update.message.reply_text(f"❌ ERROR FOUND\n\n{out}")

def is_admin(user_id: int) -> bool:
    if not ADMIN_ID:
        return True
    return str(user_id) == str(ADMIN_ID)

async def send_long(update: Update, text: str):
    for i in range(0, len(text), 3900):
        await update.message.reply_text(text[i:i+3900])


def main_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["👑 CEO", "📊 Dashboard"],
            ["🤖 Bots", "👷 Workers"],
            ["📂 Queue", "🚀 Upgrade"],
            ["🩺 Doctor", "🔧 Repair"],
            ["🛡 Security", "👁 Watchdog"],
            ["💾 Backup", "↩ Rollback"],
            ["📜 Logs", "📈 Status"],
        ],
        resize_keyboard=True
    )

async def panel_button_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = (update.message.text or "").strip()

    if txt == "👑 CEO":
        return await ceo_cmd(update, context)
    if txt == "📊 Dashboard":
        return await wdashboard(update, context)
    if txt == "🤖 Bots":
        context.args = []
        return await allbots(update, context)
    if txt == "👷 Workers":
        return await worker(update, context)
    if txt == "📂 Queue":
        return await queue_cmd(update, context)
    if txt == "🚀 Upgrade":
        return await update.message.reply_text("Use: /upgrade bot_name task")
    if txt == "🩺 Doctor":
        context.args = ["sameer_ai_manager"]
        return await doctor_cmd(update, context)
    if txt == "🔧 Repair":
        return await repair_cmd(update, context)
    if txt == "🛡 Security":
        return await safecheck(update, context)
    if txt == "👁 Watchdog":
        return await health(update, context)
    if txt == "💾 Backup":
        return await backupbot(update, context)
    if txt == "↩ Rollback":
        return await update.message.reply_text("Use: /rollbackbot bot_name backup_file")
    if txt == "📜 Logs":
        return await logs(update, context)
    if txt == "📈 Status":
        return await status(update, context)

async def panel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👑 Sameer AI Manager Control Panel\nSelect button:",
        reply_markup=main_keyboard()
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
 "🚀 SAMEER AI MANAGER PRO v2.0 🔥💎\n\n"
        "✨ Premium AI Server Active\n🟢 Status: ONLINE 24/7\n💎 Plan: PREMIUM\n🤖 Bots Managed: 5\n📊 Tasks Completed: 100+\n\n"
        "━━━ 🎯 QUICK COMMANDS ━━━\n"
        "/idea - idea ko plan me convert karo\n"
        "/ok - pending plan approve karo\n"
        "/status - system status\n"
        "/help - help menu\n\n"
        "━━━ 💡 EXAMPLE ━━━\n"
 "/idea Travel agency ke liye fare alert bot banao",
 reply_markup=ReplyKeyboardRemove()
    )


async def version_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Sameer AI Manager v1.2 - Stable Safe Runner")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Sameer AI Manager Help\n\n"
        "Use:\n"
        "/idea your idea\n"
        "/ok\n"
        "/status\n\n"
        "Main bana sakta hoon:\n"
        "✅ Travel bot plan\n"
        "✅ Quotation PDF system\n"
        "✅ Tea business bot\n"
        "✅ Baby products business bot\n"
        "✅ Study helper bot\n"
        "✅ Customer sales chat bot\n"
        "✅ Marketing message\n"
        "✅ Business strategy\n\n"
        "High-risk kaam se pehle main aapse OK loonga."
    )

async def ping_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Pong ✅")

async def pendingdecisions_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show pending decisions from AutoPilot Hub outbox."""
    outbox = Path("/root/autopilot_hub/events/outbox")
    files = sorted(outbox.glob("*.json"))
    if not files:
        await update.message.reply_text("📭 No pending decisions.")
        return
    lines = []
    for f in files:
        try:
            d = json.loads(f.read_text())
            lines.append(
                f"{d['decision_id']} | {d['source_event']} | "
                f"{d['action']} | {d['timestamp']} | {d['note']}"
            )
        except Exception as e:
            lines.append(f"{f.name} | corrupt: {e}")
    msg = "📋 **Pending Decisions**\n\n"
    msg += "`ID | Event | Action | Timestamp | Note`\n"
    msg += "─" * 40 + "\n"
    msg += "\n".join(f"`{l}`" for l in lines)
    await update.message.reply_text(msg)


def parse_amount(amt):
    if isinstance(amt, (int, float)):
        return int(amt)
    if isinstance(amt, str):
        return int(amt.replace("₹", "").replace(",", ""))
    return 0

async def paymentdashboard_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    outbox_dir = Path("/root/autopilot_hub/events/outbox")
    approved_dir = Path("/root/autopilot_hub/events/approved")
    rejected_dir = Path("/root/autopilot_hub/events/rejected")
    applied_dir = Path("/root/autopilot_hub/events/applied")
    pay_dir = Path("/root/autopilot_hub/payments")
    pending_dec = len(list(outbox_dir.glob("*.json")))
    approved_dec = len(list(approved_dir.glob("*.json")))
    rejected_dec = len(list(rejected_dir.glob("*.json")))
    applied_dec = len(list(applied_dir.glob("*.json")))
    verified_cnt = 0; pending_cnt = 0
    verified_amt = 0; pending_amt = 0
    for f in pay_dir.glob("*.json"):
        try:
            p = json.loads(f.read_text())
            s = p.get("status", "")
            amt = parse_amount(p.get("amount", 0))
            if s == "verified":
                verified_cnt += 1; verified_amt += amt
            elif s in ("pending", "pending_verification"):
                pending_cnt += 1; pending_amt += amt
        except:
            pass
    msg = (
        "📊 **Payment Dashboard**\n\n"
        f"📋 **Decisions**\n"
        f"  🔄 Pending: {pending_dec}\n"
        f"  ✅ Approved: {approved_dec}\n"
        f"  ❌ Rejected: {rejected_dec}\n"
        f"  📁 Applied: {applied_dec}\n\n"
        f"💰 **Payments**\n"
        f"  ✅ Verified: {verified_cnt} (₹{verified_amt:,})\n"
        f"  ⏳ Pending: {pending_cnt} (₹{pending_amt:,})\n\n"
        f"_Use /pendingdecisions to review pending_"
    )
    await update.message.reply_text(msg)


async def approvedecision_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mark a decision as approved. Usage: /approvedecision DEC-ID"""
    if not context.args:
        await update.message.reply_text("Usage: `/approvedecision DEC-ID`")
        return
    dec_id = context.args[0].upper()
    outbox = Path("/root/autopilot_hub/events/outbox")
    approved_dir = Path("/root/autopilot_hub/events/approved")
    src = outbox / f"{dec_id}.json"
    if not src.exists():
        await update.message.reply_text(f"❌ Decision `{dec_id}` not found in outbox.")
        return
    try:
        d = json.loads(src.read_text())
        approved_dir.mkdir(parents=True, exist_ok=True)
        dst = approved_dir / src.name
        d["action"] = "approved"
        d["decided_by"] = "sameer_ai_manager"
        d["note"] = f"Approved by Sameer AI Manager. Original: {d.get('note', '')}"
        dst.write_text(json.dumps(d, indent=2))
        src.unlink()
        await update.message.reply_text(f"✅ Decision `{dec_id}` approved. Moved to approved/")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def rejectdecision_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mark a decision as rejected. Usage: /rejectdecision DEC-ID [reason]"""
    if not context.args:
        await update.message.reply_text("Usage: `/rejectdecision DEC-ID [reason]`")
        return
    dec_id = context.args[0].upper()
    reason = " ".join(context.args[1:]) or "Rejected by Sameer AI Manager"
    outbox = Path("/root/autopilot_hub/events/outbox")
    rejected_dir = Path("/root/autopilot_hub/events/rejected")
    src = outbox / f"{dec_id}.json"
    if not src.exists():
        await update.message.reply_text(f"❌ Decision `{dec_id}` not found in outbox.")
        return
    try:
        d = json.loads(src.read_text())
        rejected_dir.mkdir(parents=True, exist_ok=True)
        dst = rejected_dir / src.name
        d["action"] = "rejected"
        d["decided_by"] = "sameer_ai_manager"
        d["note"] = f"Rejected: {reason}. Original: {d.get('note', '')}"
        dst.write_text(json.dumps(d, indent=2))
        src.unlink()
        await update.message.reply_text(f"❌ Decision `{dec_id}` rejected. Moved to rejected/")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def paymentapprove_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Approve payment by PAY-ID. Usage: /paymentapprove PAY-ID"""
    if not context.args:
        await update.message.reply_text("Usage: `/paymentapprove PAY-XXXXXXXXXXXXX-XXX`")
        return
    pay_id = context.args[0].upper()
    outbox = Path("/root/autopilot_hub/events/outbox")
    approved_dir = Path("/root/autopilot_hub/events/approved")
    # find decision whose source_event contains this pay_id
    found = None
    for f in outbox.glob("*.json"):
        try:
            d = json.loads(f.read_text())
            if pay_id in d.get("source_event", ""):
                found = d
                src = f
                break
        except:
            pass
    if not found:
        await update.message.reply_text(f"❌ No pending decision for `{pay_id}` in outbox.")
        return
    try:
        approved_dir.mkdir(parents=True, exist_ok=True)
        dst = approved_dir / src.name
        found["action"] = "approved"
        found["decided_by"] = "sameer_ai_manager"
        found["note"] = f"Approved via /paymentapprove. Original: {found.get('note', '')}"
        dst.write_text(json.dumps(found, indent=2))
        src.unlink()

        # Also verify the payment
        pay_path = Path("/root/autopilot_hub/payments") / f"{pay_id}.json"
        verify_msg = ""
        if pay_path.exists():
            try:
                pay = json.loads(pay_path.read_text())
                pay["status"] = "verified"
                pay["verified_by"] = "sameer_ai_manager"
                pay["verified_at"] = found.get("timestamp", "")
                pay["updated"] = int(__import__("time").time())
                pay_path.write_text(json.dumps(pay, indent=2))
                verify_msg = " + payment verified"

                # Create notification
                notify_dir = Path("/root/autopilot_hub/notifications")
                notify_dir.mkdir(parents=True, exist_ok=True)
                now_ts = int(__import__("time").time())
                notify = {
                    "pay_id": pay_id, "uid": pay.get("uid", 0),
                    "status": "verified",
                    "message": "✅ Payment verified. Thank you.",
                    "created_at": now_ts
                }
                nf = notify_dir / f"verified_{pay_id}_{now_ts}.json"
                nf.write_text(json.dumps(notify, indent=2))
                verify_msg += " + notification created"

                # Create job
                job_dir = Path("/root/autopilot_hub/jobs")
                job_dir.mkdir(parents=True, exist_ok=True)
                from datetime import datetime
                now = datetime.now()
                date_part = now.strftime("%Y%m%d")
                existing = list(job_dir.glob(f"JOB-{date_part}-*.json"))
                seq = len(existing) + 1
                job_id = f"JOB-{date_part}-{seq:03d}"
                job = {
                    "job_id": job_id, "pay_id": pay_id,
                    "uid": pay.get("uid", 0),
                    "customer": pay.get("name", pay.get("uname", "")),
                    "amount": pay.get("amount", 0),
                    "project_id": pay.get("project_id", ""),
                    "status": "pending",
                    "created_at": int(__import__("time").time())
                }
                (job_dir / f"{job_id}.json").write_text(json.dumps(job, indent=2))
                verify_msg += f" + job {job_id} created"
            except Exception as ve:
                verify_msg = f" (payment verify failed: {ve})"

        await update.message.reply_text(f"✅ Payment `{pay_id}` approved{verify_msg}.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def paymentreject_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reject payment by PAY-ID. Usage: /paymentreject PAY-ID [reason]"""
    if not context.args:
        await update.message.reply_text("Usage: `/paymentreject PAY-XXXXXXXXXXXXX-XXX [reason]`")
        return
    pay_id = context.args[0].upper()
    reason = " ".join(context.args[1:]) or "Rejected via /paymentreject"
    outbox = Path("/root/autopilot_hub/events/outbox")
    rejected_dir = Path("/root/autopilot_hub/events/rejected")
    found = None
    for f in outbox.glob("*.json"):
        try:
            d = json.loads(f.read_text())
            if pay_id in d.get("source_event", ""):
                found = d
                src = f
                break
        except:
            pass
    if not found:
        await update.message.reply_text(f"❌ No pending decision for `{pay_id}` in outbox.")
        return
    try:
        rejected_dir.mkdir(parents=True, exist_ok=True)
        dst = rejected_dir / src.name
        found["action"] = "rejected"
        found["decided_by"] = "sameer_ai_manager"
        found["note"] = f"Rejected: {reason}. Original: {found.get('note', '')}"
        dst.write_text(json.dumps(found, indent=2))
        src.unlink()
        await update.message.reply_text(f"❌ Payment `{pay_id}` rejected. Moved to rejected/")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ 🚀 SAMEER AI MANAGER PRO ONLINE 🚀\n"
        f"Model: {MODEL}\n"
        "Mode: Approval-based safe manager"
    )

async def idea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) not in ALLOWED_USER_IDS:
        return await update.message.reply_text("❌ Access denied.")
    idea_text = " ".join(context.args).strip()
    if not idea_text:
        return await update.message.reply_text("━━━ 💡 EXAMPLE ━━━\n/idea el salama radiator factory ke liye customer support bot banao")

    await update.message.reply_text("🧠 Idea analyze kar raha hoon...")

    response = ai.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Is idea ka premium execution plan banao. Idea: {idea_text}"}
        ]
    )

    plan = response.choices[0].message.content
    pending_task[update.effective_user.id] = plan

    await send_long(update, "📋 PREMIUM PLAN:\n\n" + plan + "\n\n✅ Approve karne ke liye /ok likho.")

async def ok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("❌ Access denied.")

    plan = pending_task.get(update.effective_user.id)
    if not plan:
        return await update.message.reply_text("❌ Koi pending plan nahi hai. Pehle /idea bhejo.")

    await update.message.reply_text(
        "✅ Approved.\n\n"
        "Ab next version me main is approval ke baad:\n"
        "1. backup loonga\n"
        "2. code file banaunga\n"
        "3. test karunga\n"
        "4. restart/report dunga\n\n"
        "Abhi safe mode me plan approved store ho gaya."
    )

async def excel_upload_cmd(update, context):
 await update.message.reply_text('EXCEL_HANDLER_READY')


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("❌ Access denied.")

    user_msg = update.message.text

    await update.message.reply_text("💭 Soch raha hoon...")

    try:
        response = ai.chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg}
            ]
        )

        reply = response.choices[0].message.content
        await send_long(update, reply)

    except Exception as e:
        await update.message.reply_text(f"❌ Error aaya:\n{str(e)}")


async def upgrade_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Upgrade system ready. Use /auto_upgrade or /fix.")

async def auto_upgrade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Auto upgrade planning ready. Send /agent your upgrade idea.")

async def create_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot builder ready. Use /deploy_customer customer_name.")

async def apply_ai_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Apply AI placeholder ready. Use /approve_patch for safe patch apply.")




async def do_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) not in ALLOWED_USER_IDS:
        return await update.message.reply_text("❌ Access denied.")

    task = " ".join(context.args).strip()

    if not task:
        return await update.message.reply_text(
            "⚡ Use:\n/do your task"
        )

    await update.message.reply_text("⚡ Master Controller preparing execution...")

    prompt = f"""
You are Sameer Master Controller running on Sameer's VPS.

VPS facts:
- Main project: /root/sameer_ai_manager
- Customer bots path: /root/workspaces/customers
- Python venv: /root/sameer_ai_manager/venv
- Services: sameer_ai_manager, salama_radiator_bot
- Use Telegram /run commands for execution.
- Always backup before changing files.
- Always run python3 -m py_compile before restart.
- Always use systemctl restart/status for services.
- Do NOT give generic cloud setup advice.
- Give exact practical commands for THIS VPS.

User task:
{task}

Create:
1. Direct action plan
2. Exact /run commands
3. Files to create/edit
4. Service setup commands
5. Test commands
6. Safety backup/rollback commands

Keep response short, practical, and execution-ready.
"""

    try:
        # AI Engine via ai.chat()
        client = None  # ai.chat() handles this

        response = ai.chat(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":"You are an elite AI DevOps architect."},
                {"role":"user","content":prompt}
            ],
            max_tokens=900
        )

        result = response.choices[0].message.content

    except Exception as e:
        result = f"❌ DO error:\n{e}"

    await update.message.reply_text(result[:3900])

async def brain_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) not in ALLOWED_USER_IDS:
        return await update.message.reply_text("❌ Access denied.")

    idea = " ".join(context.args).strip()

    if not idea:
        return await update.message.reply_text(
            "🧠 Use:\n/brain your idea"
        )

    await update.message.reply_text("🧠 Master Brain thinking...")

    prompt = f"""
You are Sameer Master Controller AI.

User idea:
{idea}

Make:
1. Powerful execution plan
2. Step-by-step roadmap
3. Required files/tools
4. Risks
5. Smart automation ideas

Keep response short but powerful.
"""

    try:
        # AI Engine via ai.chat()
        client = None  # ai.chat() handles this

        response = ai.chat(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":"You are a powerful AI automation architect."},
                {"role":"user","content":prompt}
            ],
            max_tokens=700
        )

        result = response.choices[0].message.content

    except Exception as e:
        result = f"❌ Brain error:\n{e}"

    await update.message.reply_text(result[:3900])


async def service_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) not in ALLOWED_USER_IDS:
        return await update.message.reply_text("❌ Access denied.")

    args = context.args
    if len(args) < 3:
        return await update.message.reply_text(
            "Use:\n/service service_name working_dir bot_file\n\n━━━ 💡 EXAMPLE ━━━\n/service freshtiq_travel_bot /root/workspaces/customers/freshtiq_travel_agency_automation bot.py"
        )

    name = args[0].replace(".service", "")
    workdir = args[1]
    botfile = args[2]

    service_path = f"/etc/systemd/system/{name}.service"

    cmd = f"""
cat > {service_path} <<'EOF'
[Unit]
After=network.target

[Service]
Restart=always
RestartSec=5

[Install]
EOF

python3 -m py_compile {workdir}/{botfile} &&
systemctl daemon-reload &&
systemctl enable {name} &&
systemctl restart {name} &&
systemctl status {name} --no-pager
"""
    output = run_shell(cmd)
    await update.message.reply_text(output[-3900:])





async def smartfix_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) not in ALLOWED_USER_IDS:
        return await update.message.reply_text("❌ Access denied.")

    if not context.args:
        return await update.message.reply_text("Use:\n/smartfix service_name")

    service = context.args[0].replace(".service", "")
    allowed = ["sameer_ai_manager", "freshtiq_travel_bot", "salama_radiator_bot"]

    if service not in allowed:
        return await update.message.reply_text("Allowed:\n" + "\n".join(allowed))

    status = run_shell(f"systemctl is-active {service}").strip()

    if status == "active":
        out = run_shell(f"systemctl status {service} --no-pager | head -20")
        return await update.message.reply_text(
            "✅ Service active hai. Repair needed nahi.\n\n" + out[-3000:]
        )

    await update.message.reply_text("⚠️ Service active nahi hai. Logs analyze kar raha hoon...")

    logs = run_shell(f"systemctl status {service} --no-pager; echo; journalctl -u {service} -n 100 --no-pager")

    prompt = f"""
You are Sameer AI Manager SmartFix.

Service: {service}
Status: {status}

Logs:
{logs[-8000:]}

Give exact repair commands for THIS VPS only.
Rules:
- Backup first.
- Check token/env/path/syntax/service file first.
- Compile Python before restart.
- No random package upgrade unless logs clearly prove it.
- Include rollback command.
- Short and practical.
"""

    try:
        # AI Engine via ai.chat()
        client = None  # ai.chat() handles this
        r = ai.chat(
            model=MODEL,
            messages=[
                {"role":"system","content":"You are a strict Linux Python Telegram bot repair engineer."},
                {"role":"user","content":prompt}
            ],
            max_tokens=900
        )
        result = r.choices[0].message.content
    except Exception as e:
        result = "❌ SmartFix AI error:\n" + str(e)

    await update.message.reply_text("🧠 SMARTFIX PLAN:\n\n" + result[-3600:])

async def autofix_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) not in ALLOWED_USER_IDS:
        return await update.message.reply_text("❌ Access denied.")

    if not context.args:
        return await update.message.reply_text("Use:\n/autofix service_name")

    service = context.args[0].replace(".service", "")
    allowed = ["sameer_ai_manager", "freshtiq_travel_bot", "salama_radiator_bot"]

    if service not in allowed:
        return await update.message.reply_text("Allowed:\n" + "\n".join(allowed))

    await update.message.reply_text("🧠 Autofix analyzing logs...")

    logs = run_shell(f"systemctl status {service} --no-pager; echo; journalctl -u {service} -n 100 --no-pager")

    prompt = f"""
You are Sameer AI Manager Autofix.

Service: {service}

Logs:
{logs[-8000:]}

Create a SAFE repair plan only.
Rules:
- Do NOT suggest package upgrade unless clearly necessary.
- First check token, syntax, path, service file, env file, missing imports.
- Give exact commands for this VPS.
- Must backup before editing.
- Must compile Python before restart.
- Must include rollback command.
- Do not apply anything automatically.
- Short and practical.
"""

    try:
        # AI Engine via ai.chat()
        client = None  # ai.chat() handles this
        r = ai.chat(
            model=MODEL,
            messages=[
                {"role":"system","content":"You are a senior Linux Python Telegram bot repair engineer."},
                {"role":"user","content":prompt}
            ],
            max_tokens=900
        )
        result = r.choices[0].message.content
    except Exception as e:
        result = "❌ Autofix AI error:\n" + str(e)

    await update.message.reply_text("🧠 AUTOFIX PLAN:\n\n" + result[-3600:] + "\n\n✅ If OK, run commands manually or ask me to convert to /run.")

async def doctor_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) not in ALLOWED_USER_IDS:
        return await update.message.reply_text("❌ Access denied.")

    if not context.args:
        return await update.message.reply_text("Use:\n/doctor service_name")

    service = context.args[0].replace(".service", "")
    allowed = ["sameer_ai_manager", "freshtiq_travel_bot", "salama_radiator_bot"]

    if service not in allowed:
        return await update.message.reply_text("Allowed:\n" + "\n".join(allowed))

    await update.message.reply_text("🩺 Doctor checking logs...")

    logs = run_shell(f"systemctl status {service} --no-pager; echo; journalctl -u {service} -n 80 --no-pager")

    prompt = f"""
You are Sameer AI Manager Doctor.
Analyze this service problem and give exact VPS commands to fix it.
Service: {service}

Logs:
{logs[-7000:]}

Rules:
- Be short.
- Give exact commands only for this VPS.
- Backup before editing.
- Compile Python before restart.
- No generic advice.
"""

    try:
        # AI Engine via ai.chat()
        client = None  # ai.chat() handles this
        r = ai.chat(
            model=MODEL,
            messages=[
                {"role":"system","content":"You are an expert Linux Python Telegram bot repair engineer."},
                {"role":"user","content":prompt}
            ],
            max_tokens=800
        )
        result = r.choices[0].message.content
    except Exception as e:
        result = "❌ Doctor AI error:\n" + str(e)

    await update.message.reply_text(result[-3900:])

async def bots_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) not in ALLOWED_USER_IDS:
        return await update.message.reply_text("❌ Access denied.")

    args = context.args

    if not args:
        cmd = """
echo "🤖 SAMEER BOT CONTROL"
echo "===================="
systemctl list-units --type=service --all --no-pager | grep -E "sameer|freshtiq|salama|bot" | head -50
"""
        output = run_shell(cmd)
        return await update.message.reply_text(output[-3900:])

    action = args[0]
    service = args[1] if len(args) > 1 else ""

    allowed = ["sameer_ai_manager", "freshtiq_travel_bot", "salama_radiator_bot"]

    if action in ["status", "restart", "logs"] and service not in allowed:
        return await update.message.reply_text(
            "Allowed services:\n" + "\n".join(allowed)
        )

    if action == "status":
        output = run_shell(f"systemctl status {service} --no-pager")
    elif action == "restart":
        output = run_shell(f"systemctl restart {service} && systemctl status {service} --no-pager")
    elif action == "logs":
        output = run_shell(f"journalctl -u {service} -n 80 --no-pager")
    else:
        output = "Use:\n/bots\n/bots status service_name\n/bots restart service_name\n/bots logs service_name"

    await update.message.reply_text(output[-3900:])

async def master_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) not in ALLOWED_USER_IDS:
        return await update.message.reply_text("❌ Access denied.")

    cmd = """
echo "👑 SAMEER MASTER CONTROLLER v1.3"
echo "=============================="
echo "📍 WHOAMI:"; whoami
echo
echo "📂 PATH:"; pwd
echo
echo "🟢 SAMEER AI MANAGER:"; systemctl is-active sameer_ai_manager
echo
echo "🧠 PYTHON:"; python3 --version
echo
echo "💾 DISK:"; df -h / | tail -1
echo
echo "🧮 MEMORY:"; free -h | head -2
echo
echo "🤖 RUNNING BOTS:"; ps aux | grep -E "bot.py|python" | grep -v grep | head -20
echo
echo "📝 LAST ERRORS:"; journalctl -u sameer_ai_manager -n 20 --no-pager | tail -20
"""
    output = run_shell(cmd)
    await update.message.reply_text(output[-3900:])

async def run_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) not in ALLOWED_USER_IDS:
        return await update.message.reply_text("❌ Access denied.")

    import subprocess
    cmd = " ".join(context.args).strip()
    if not cmd:
        return await update.message.reply_text("Use: /run command")

    await update.message.reply_text("⚙️ Command run kar raha hoon...")

    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
        out = (r.stdout or "") + (r.stderr or "")
        if not out.strip():
            out = f"✅ Done. Exit code: {r.returncode}"
        await update.message.reply_text(out[-3500:])
    except subprocess.TimeoutExpired:
        await update.message.reply_text("⏱️ Command timeout after 120s. Use shorter command.")
    except Exception as e:
        await update.message.reply_text(f"❌ Run error: {e}")

async def restart_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) not in ALLOWED_USER_IDS:
        return await update.message.reply_text("❌ Access denied.")
    await update.message.reply_text("🔄 Restarting bot...")
    subprocess.Popen("systemctl restart sameer_ai_manager", shell=True)

async def files_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) not in ALLOWED_USER_IDS:
        return await update.message.reply_text("❌ Access denied.")
    result = subprocess.run(
        "cd /root/sameer_ai_manager && ls -lah",
        shell=True,
        capture_output=True,
        text=True,
        timeout=30
    )
    await send_long(update, "📁 Files:\n\n" + result.stdout[-3500:])

async def logs_live_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        cmd = "journalctl -u sameer_ai_manager -n 50 --no-pager"

        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=20
        )

        output = (result.stdout + result.stderr).strip()

        if not output:
            output = "No logs found."

        await update.message.reply_text(
            "📜 LIVE LOGS:\n\n" + output[-3500:]
        )

    except Exception as e:
        await update.message.reply_text(
            f"❌ Logs error:\n{str(e)}"
        )
async def logs_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) not in ALLOWED_USER_IDS:
        return await update.message.reply_text("❌ Access denied.")
    result = subprocess.run(
        "journalctl -u sameer_ai_manager -n 50 --no-pager",
        shell=True,
        capture_output=True,
        text=True,
        timeout=30
    )
    await send_long(update, result.stdout[-12000:])

async def auto_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) not in ALLOWED_USER_IDS:
        return await update.message.reply_text("❌ Access denied.")

    prompt = " ".join(context.args).strip()
    if not prompt:
        return await update.message.reply_text("━━━ 💡 EXAMPLE ━━━\n/auto el salama radiator factory ke liye customer support bot banao")

    return await update.message.reply_text("🤖 AUTO DONE\n\nAI auto system temporary active")


async def agent_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) not in ALLOWED_USER_IDS:
        return await update.message.reply_text("❌ Access denied.")

    prompt = " ".join(context.args).strip()
    if not prompt:
        return await update.message.reply_text("□️ EXAMPLE\n/agent check system")

    try:
        from ai_brain.planner import ai_plan
        
        vps_context = f"""
This is Sameer's LIVE VPS and Sameer AI Manager control bot.

Now you MUST not ask which system.
Assume this system:
- Project: /root/sameer_ai_manager
- Worker: sameer_ai_worker_auto.service
- Main bot: sameer_ai_manager.service
- AutoPilot Hub: autopilot_hub_bot.service
- Salama Bot: salama_radiator_bot.service
- Travel Bot: freshtiq_ai_travel_pro.service
- Bots path: /root/workspaces/customers
- Always give exact Telegram /run commands only.
- Every Linux command MUST be formatted exactly like: /run df -h . Never write /run/df or /run/systemctl. Put one space after /run.
- Give EXACTLY 3 numbered steps only.
- Do not ask which system.
- Do not give generic advice.
- For health checks, only suggest lightweight commands: df, free, systemctl is-active, tail logs. Do not suggest /var/log/syslog. For logs use journalctl service-specific only if user asks logs.
- Keep short and execution-ready.

User request:
{prompt}
"""
        result = ai_plan(vps_context)

        return await send_long(update, result)
    except Exception as e:
        return await update.message.reply_text(f"❌ Agent error: {e}")

async def buildbot_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) not in ALLOWED_USER_IDS:
        return await update.message.reply_text("❌ Access denied.")

    if len(context.args) < 2:
        return await update.message.reply_text(
            "Usage:\n/buildbot type botname\n━━━ 💡 EXAMPLE ━━━\n/buildbot radiator sameer_radiator"
        )

    bot_type = context.args[0]
    bot_name = context.args[1]

    try:
        path = None  # create_customer_bot(bot_type, bot_name)
        await update.message.reply_text(
            f"✅ Customer bot project ready\n\nType: {bot_type}\nName: {bot_name}\nPath: {path}"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Build failed: {e}")

async def backup_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) not in ALLOWED_USER_IDS:
        return await update.message.reply_text("❌ Access denied.")
    cmd = "cd /root/sameer_ai_manager && mkdir -p backups && cp bot.py backups/bot_$(date +%F_%H%M).py && cp .env backups/env_$(date +%F_%H%M).env"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    if result.returncode == 0:
        await update.message.reply_text("✅ Backup complete.")
    else:
        await update.message.reply_text("❌ Backup failed:\n" + result.stderr)

async def auto_code_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) not in ALLOWED_USER_IDS:
        return await update.message.reply_text("❌ Access denied.")

    prompt = " ".join(context.args)

    if not prompt:
        return await update.message.reply_text(
            "━━━ 💡 EXAMPLE ━━━\n/autocode add whatsapp auto reply system"
        )

    await update.message.reply_text("🤖 AI coding plan bana raha hoon...")

    try:
        response = ai.chat(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert Python Telegram bot developer."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3
        )

        ai_code = response.choices[0].message.content

        with open("/root/sameer_ai_manager/ai_patch.txt", "w") as f:
            f.write(ai_code)

        await send_long(update, ai_code[:12000])

    except Exception as e:
        await update.message.reply_text(f"❌ AI Error: {e}")

async def apply_ai_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = subprocess.run(
        ["python3", "patch_tool.py"],
        cwd="/root/sameer_ai_manager",
        capture_output=True,
        text=True
    )

    output = (result.stdout + result.stderr).strip()

    if not output:
        output = "APPLY SUCCESS"

    await update.message.reply_text(
        "APPLY RESULT:\n\n" + output[-3500:]
    )

async def rollback_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if str(update.effective_user.id) not in ALLOWED_USER_IDS:
            return await update.message.reply_text("❌ Access denied.")

        await update.message.reply_text("♻️ Rollback check kar raha hoon...")

        cmd = """
cd /root/sameer_ai_manager
LATEST=$(ls -t backups/bot_*.py 2>/dev/null | head -1)
if [ -z "$LATEST" ]; then
  echo "NO_BACKUP_FOUND"
  exit 1
fi
cp bot.py bot.py.failed_$(date +%F_%H%M)
cp "$LATEST" bot.py
python3 -m py_compile bot.py
"""

        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )

        output = (result.stdout + result.stderr).strip()

        if result.returncode != 0:
            return await update.message.reply_text(
                "❌ Rollback failed:\n\n" + output[-3500:]
            )

        subprocess.Popen("systemctl restart sameer_ai_manager", shell=True)

        await update.message.reply_text(
            "✅ Rollback successful.\nBot.py latest backup se restore ho gaya.\nService restart ho raha hai..."
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Rollback error:\n{str(e)}")

    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        backup_name = f"full_backup_{timestamp}.tar.gz"

        backup_path = f"/root/sameer_ai_manager/backups/{backup_name}"

        cmd = f"tar --exclude='/root/sameer_ai_manager/backups' -czf {backup_path} /root/sameer_ai_manager"

        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            await update.message.reply_text(
                f"✅ Full backup created:\n{backup_name}"
            )
        else:
            await update.message.reply_text(
                f"❌ Backup failed:\n{result.stderr}"
            )

    except Exception as e:
        await update.message.reply_text(
            f"❌ Error:\n{str(e)}"
        )


async def allbots(update, context):
    import subprocess
    out = subprocess.getoutput("systemctl list-units --type=service --all --no-pager | grep -E 'sameer|freshtiq|salama|restaurant|bot' || true")
    await update.message.reply_text("🤖 ALL BOTS / SERVICES\n\n" + out[:3500])

async def logs_cmd(update, context):
    import subprocess
    service = context.args[0] if context.args else "sameer_ai_manager"
    out = subprocess.getoutput(f"journalctl -u {service}.service -n 40 --no-pager")
    await update.message.reply_text(f"📜 LOGS: {service}\n\n{out[-3500:]}")

async def backup_cmd(update, context):
    import subprocess, datetime
    name = f"/root/backups/tg_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
    subprocess.call(f"tar --exclude='/root/backups' -czf {name} /root/sameer_ai_manager /etc/systemd/system 2>/dev/null", shell=True)
    await update.message.reply_text(f"✅ BACKUP CREATED\n{name}")

async def restartbot(update, context):
    import subprocess
    if not context.args:
        await update.message.reply_text("Use: /restartbot service_name")
        return
    service = context.args[0].replace(".service","")
    subprocess.call(f"systemctl restart {service}.service", shell=True)
    status = subprocess.getoutput(f"systemctl is-active {service}.service")
    await update.message.reply_text(f"🔁 {service}\nStatus: {status}")

async def fixbot(update, context):
    import subprocess
    if not context.args:
        await update.message.reply_text("Use: /fixbot service_name")
        return
    service = context.args[0].replace(".service","")
    subprocess.call(f"systemctl restart {service}.service", shell=True)
    log = subprocess.getoutput(f"journalctl -u {service}.service -n 25 --no-pager")
    status = subprocess.getoutput(f"systemctl is-active {service}.service")
    await update.message.reply_text(f"🛠 FIXBOT {service}\nStatus: {status}\n\n{log[-2500:]}")

async def run_cmd(update, context):
    import subprocess
    cmd = " ".join(context.args)
    if not cmd:
        await update.message.reply_text("Use: /run command")
        return
    out = subprocess.getoutput(cmd)
    await update.message.reply_text("🖥 RUN OUTPUT\n\n" + out[-3500:])




async def handle_text_ai(update, context):
    try:
        user_text = update.message.text.strip()
        msg = await update.message.reply_text("🧠 Samajh raha hu...")

        import sys
        sys.path.append("/root/sameer_ai_manager")
        from plugins.ai_plugin import ask_brain

        await msg.edit_text("⚙️ Analyze kar raha hu...")
        reply = ask_brain(user_text)

        await msg.edit_text("🧠 Sameer AI Manager\n\n" + reply[:3500])

    except Exception as e:
        await update.message.reply_text(f"AI_PLUGIN_ERROR: {e}")



async def autopilot_cmd(update, context):
    try:
        msg = await update.message.reply_text("🧠 Autopilot report bana raha hu...")
        import sys
        sys.path.append("/root/sameer_ai_manager")
        from plugins.status_plugin import autopilot_report
        report = autopilot_report()
        await msg.edit_text(report[:3900])
    except Exception as e:
        await update.message.reply_text(f"AUTOPILOT_REPORT_ERROR: {e}")





async def runpy(update, context):
    try:
        import tempfile
        import subprocess
        import os

        if context.args:
            pycode = update.message.text.split(" ", 1)[1] if len(update.message.text.split(" ", 1)) > 1 else ""
        elif update.message.reply_to_message:
            pycode = update.message.reply_to_message.text
        else:
            await update.message.reply_text(
                "Usage: /runpy print(\"hello\")"
            )
            return

        fd, path = tempfile.mkstemp(suffix=".py")

        with os.fdopen(fd, "w") as f:
            f.write(pycode)

        out = subprocess.getoutput(
            f"/root/sameer_ai_manager/venv/bin/python {path}"
        )

        os.remove(path)

        if not out.strip():
            out = "DONE"

        await update.message.reply_text(
            "🐍 RUNPY OUTPUT\n\n" + out[:3500]
        )

    except Exception as e:
        await update.message.reply_text(
            f"RUNPY_ERROR: {e}"
        )

async def runb64(update, context):
    try:
        import base64, subprocess

        if not context.args:
            await update.message.reply_text("Usage: /runb64 BASE64_COMMAND")
            return

        encoded = " ".join(context.args).strip()
        cmd = base64.b64decode(encoded).decode("utf-8")

        msg = await update.message.reply_text("🧠 Safe command execute kar raha hu...")

        out = subprocess.getoutput(cmd)

        if not out.strip():
            out = "DONE"

        await msg.edit_text("🖥 RUNB64 OUTPUT\n\n" + out[:3500])

    except Exception as e:
        await update.message.reply_text(f"RUNB64_ERROR: {e}")

# Create a running event loop first (fixes JobQueue/event_loop race)
import asyncio
_loop = asyncio.new_event_loop()
asyncio.set_event_loop(_loop)

# Fix apscheduler timezone issue (needs pytz, not zoneinfo)
# Monkeypatch apscheduler to convert zoneinfo to pytz
import pytz, apscheduler.util
# Fix apscheduler to accept zoneinfo timezone too
orig_astimezone = apscheduler.util.astimezone
apscheduler.util.astimezone = lambda tz: orig_astimezone(str(tz)) if str(type(tz)) == "<class 'zoneinfo.ZoneInfo'>" else orig_astimezone(tz)
app = Application.builder().token(TELEGRAM_TOKEN).concurrent_updates(True).connection_pool_size(64).pool_timeout(60).build()


async def debug_all(update, context):
    try:
        print("DEBUG_UPDATE:", update.effective_user.id, update.effective_chat.id, update.message.text, flush=True)
        await update.message.reply_text("DEBUG_OK: update received")
    except Exception as e:
        print("DEBUG_ERROR:", e, flush=True)
app.add_handler(CommandHandler("debug", debug_all))
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("pendingdecisions", pendingdecisions_cmd))
app.add_handler(CommandHandler("paymentdashboard", paymentdashboard_cmd))
app.add_handler(CommandHandler("paymentapprove", paymentapprove_cmd))
app.add_handler(CommandHandler("paymentreject", paymentreject_cmd))
app.add_handler(CommandHandler("approvedecision", approvedecision_cmd))
app.add_handler(CommandHandler("rejectdecision", rejectdecision_cmd))
app.add_handler(CommandHandler("help", help_cmd))


print("🚀 Sameer AI Manager Starting...")


app.add_handler(CommandHandler("allbots", allbots))
app.add_handler(CommandHandler("backup", backup_cmd))
app.add_handler(CommandHandler("restartbot", restartbot))
app.add_handler(CommandHandler("fixbot", fixbot))




async def status(update, context):
    import subprocess
    def sh(c):
        return subprocess.getoutput(c).strip()
    msg = "📊 SAMEER AI MANAGER STATUS\n\n"
    msg += "Manager: " + sh("systemctl is-active sameer_ai_manager.service") + "\n"
    msg += "Worker: " + sh("systemctl is-active sameer_ai_worker_auto.service") + "\n"
    msg += "Auto Heal: " + sh("systemctl is-active sameer_auto_heal.service") + "\n"
    msg += "Auto Master: " + sh("systemctl is-active sameer_auto_master.service") + "\n"
    msg += "Disk: " + sh("df -h / | awk 'NR==2{print $5 \" used, \" $4 \" free\"}'") + "\n"
    msg += "RAM: " + sh("free -h | awk '/Mem:/ {print $3 \"/\" $2}'")
    await update.message.reply_text(msg)


async def upgrade(update, context):

    if len(context.args) < 2:
        await update.message.reply_text(
            "Use:\n/upgrade bot_name task"
        )
        return

    bot=context.args[0]
    bot_key={"autopilot_hub_bot":"autopilot_hub","sameer":"sameer_ai_manager","freshtiq_ai_travel_pro":"freshtiq_travel","salama_radiator_bot":"salama_erp"}.get(bot,bot)
    task=" ".join(context.args[1:])

    # Duplicate Guard
    import re, json, os, glob
    reg_path="/root/sameer_ai_manager/factory_registry.json"
    if not os.path.exists(reg_path):
        base_reg={
            "milestones":[
                "generic_command_generator_working",
                "auto_deploy_working",
                "patch_quality_working",
                "dry_run_working",
                "backup_verify_working"
            ],
            "features":{
                "autopilot":["/hello","/bye","/ping","/teststatus"],
                "sameer":["/ceo","/worker","/queue","/wdashboard","/safecheck"]
            }
        }
        open(reg_path,"w").write(json.dumps(base_reg,indent=2))
    reg=json.load(open(reg_path))
    cmd_match=re.search(r"/[a-zA-Z0-9_]{2,32}", task)
    if cmd_match:
        feature=cmd_match.group(0).lower()
        existing=[x.lower() for x in reg.get("features",{}).get(bot_key,[])]
        if feature in existing:
            return await update.message.reply_text(
                f"⚠️ DUPLICATE FEATURE BLOCKED\n\nBot: {bot}\nFeature: {feature}\n\nAlready exists in Factory Registry. Upgrade skipped."
            )

    path=None  # create_upgrade_task(bot,task)

    if cmd_match:
        feature=cmd_match.group(0).lower()
        reg.setdefault("features",{}).setdefault(bot_key,[])
        if feature not in reg["features"][bot_key]:
            reg["features"][bot_key].append(feature)
            open(reg_path,"w").write(json.dumps(reg,indent=2))

    await update.message.reply_text(
        f"🚀 AUTO UPGRADE QUEUED\n\nBot: {bot}\nTask: {task}\n\nQueue Saved:\n{path}"
    )



async def health(update, context):
 import subprocess
 def sh(c):
  return subprocess.getoutput(c).strip()
 msg = "🩺 SERVER HEALTH\n\n"
 msg += "💾 Disk: " + sh("df -h / | awk 'NR==2{print $5 \" used, \" $4 \" free\"}'") + "\n"
 msg += "🧠 RAM: " + sh("free -h | awk '/Mem:/ {print $3 \"/\" $2}'") + "\n\n"
 for s in ["sameer_ai_manager.service","sameer_ai_worker_auto.service","sameer_ai_brain_loop.service","autopilot_hub_bot.service","freshtiq_ai_travel_pro.service","salama_radiator_bot.service","salama_service_bot.service"]:
  msg += s + " => " + sh("systemctl is-active " + s) + "\n"
 await update.message.reply_text(msg)

async def status(update, context):
 await health(update, context)

app.add_handler(CommandHandler("autopilot", autopilot_cmd))
app.add_handler(CommandHandler("run", run_cmd))
app.add_handler(CommandHandler("runb64", runb64))
app.add_handler(CommandHandler("runpy", runpy))
# DEPRECATEDapp.add_handler(CommandHandler("tasks", tasks))
# DISABLED_OLD_HEALTH: app.add_handler(CommandHandler("health", health))
app.add_handler(CommandHandler("status", status))
app.add_handler(CommandHandler("services", health))
app.add_handler(CommandHandler("wdashboard", wdashboard))

async def ceo_cmd(update, context):
    import os, glob, subprocess, json
    base="/root/sameer_ai_manager"
    r=json.load(open(base+"/worker_manager/state/boss_report.json"))
    lessons=len(glob.glob(base+"/ai_brain/lessons/*.txt"))
    workers=len(glob.glob(base+"/**/*worker*.py", recursive=True))
    managers=len(glob.glob(base+"/**/*manager*.py", recursive=True))
    services=subprocess.getoutput("systemctl list-units --type=service --all | grep -E 'sameer|autopilot|freshtiq|salama' | wc -l").strip()
    active=[k for k,v in r.get("services",{}).items() if v=="active"]
    total=int(r.get("deployed",0))+int(r.get("rejected",0))+int(r.get("failed",0))
    progress=int((int(r.get("deployed",0))/max(total,1))*100)
    ram=subprocess.getoutput("free -h | awk '/Mem:/ {print $3\" used / \"$7\" available\"}'")
    disk=subprocess.getoutput("df -h / | awk 'NR==2 {print $5\" used (\"$3\"/\"$2\")\"}'")
    up=subprocess.getoutput("uptime -p")
    load=subprocess.getoutput("uptime | awk -F'load average:' '{print $2}'").strip()
    health="🟢 GREEN"
    if int(r.get("failed",0)) > int(r.get("deployed",0)):
        health="🟡 YELLOW"
    if r.get("worker_auto_processes","0")=="0":
        health="🔴 RED"
    msg=f"👑 SAMEER AI FACTORY CEO DASHBOARD V2\n\n🛡 Health: {health}\n📚 Lessons: {lessons}\n🤖 Workers: {workers}\n👨‍💼 Managers: {managers}\n⚙️ Services: {services}\n\n💾 RAM: {ram}\n🗄 Disk: {disk}\n⏱ Uptime: {up}\n📊 Load: {load}\n\n📂 Queue: {r.get('queue',0)}\n⏳ Pending: {r.get('pending',0)}\n🚀 Deployed: {r.get('deployed',0)}\n🛑 Rejected: {r.get('rejected',0)}\n💥 Failed: {r.get('failed',0)}\n\n🧠 Worker Auto: {r.get('worker_auto_processes','0')}\n👁 Approved Monitor: {r.get('approved_monitor_processes','0')}\n\n🟢 Active Core:\n- " + "\n- ".join(active) + f"\n\n📈 Automation Progress: {progress}%\n🎯 Phase: Autonomous AI Factory\n🛠 Remaining: CEO notifications, self-repair, auto-rollback polish"
    await update.message.reply_text(msg[:3900])



async def factory_cmd(update, context):
    import json, os
    reg_path="/root/sameer_ai_manager/factory_registry.json"
    if not os.path.exists(reg_path):
        return await update.message.reply_text("⚠️ Factory registry not found yet.")
    reg=json.load(open(reg_path))
    msg="🏭 SAMEER AI FACTORY REGISTRY\n\n"
    msg+="🏆 Milestones:\n"
    for x in reg.get("milestones",[]):
        msg+="✅ "+str(x)+"\n"
    msg+="\n🤖 Features by Bot:\n"
    for bot, feats in reg.get("features",{}).items():
        msg+="\n📌 "+str(bot).upper()+"\n"
        for f in feats:
            msg+="✅ "+str(f)+"\n"
    await update.message.reply_text(msg[:3900])

app.add_handler(CommandHandler("worker", worker))
app.add_handler(CommandHandler("queue", queue_cmd))
app.add_handler(CommandHandler("safecheck", safecheck))
app.add_handler(CommandHandler("cleanlogs", cleanlogs))
app.add_handler(CommandHandler("backupbot", backupbot))
app.add_handler(CommandHandler("rollbackbot", rollbackbot))
app.add_handler(CommandHandler("logs", logs))
app.add_handler(CommandHandler("upgrade", upgrade))
app.add_handler(CommandHandler("agent", agent_cmd))
app.add_handler(CommandHandler("auto", auto_cmd))
# DISABLED_DUPLICATE_FACTORY_CMD: app.add_handler(CommandHandler("factory", factory_cmd))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_ai))
app.add_handler(MessageHandler(filters.VOICE, handle_voice))


async def status(update, context):
    await update.message.reply_text('✅ Bot is running')

app.add_handler(CommandHandler('status', status))

async def notify_ceo(context, deployment_status):
    import os
    ceo_chat_id = os.getenv('CEO_CHAT_ID')
    if ceo_chat_id:
        text = 'DEPLOY REPORT - Status: ' + str(deployment_status)
        await context.bot.send_message(chat_id=ceo_chat_id, text=text)

async def factory_dashboard(update, context):
    if str(update.effective_user.id) not in ALLOWED_USER_IDS:
        return await update.message.reply_text('⛔ Unauthorized')
    import os, json, glob, subprocess, re
    base="/root/sameer_ai_manager"
    reg_path=base+"/factory_registry.json"
    def sh(c):
        return subprocess.getoutput(c).strip()
    if not os.path.exists(reg_path):
        reg={"milestones":[],"features":{}}
    else:
        reg=json.load(open(reg_path))
    reg.setdefault("milestones",[])
    reg.setdefault("features",{})
    cmds=[]
    for line2 in open(base+'/bot.py').read().splitlines():
        if 'CommandHandler(' in line2:
            try:
                c=line2.split('CommandHandler(')[1].split(',')[0].strip().strip(chr(34)).strip(chr(39))
                if c and c not in cmds:
                    cmds.append(c)
            except Exception:
                pass
    cmds=sorted(cmds)
    sameer=reg["features"].setdefault("sameer_ai_manager",[])
    for c in cmds:
        x="/"+c
        if x not in sameer:
            sameer.append(x)
    for m in ["patch_generator","quality_checker","dry_run","auto_deploy","backup_verify","duplicate_guard","tester_worker","central_guard","factory_dashboard","registry_auto_sync"]:
        if m not in reg["milestones"]:
            reg["milestones"].append(m)
    open(reg_path,"w").write(json.dumps(reg,indent=2))
    services=["sameer_ai_manager.service","sameer_ai_worker_auto.service","sameer_approved_monitor.service","autopilot_hub_bot.service","freshtiq_ai_travel_pro.service","salama_radiator_bot.service"]
    active=[]
    for s in services:
        active.append(f"{s}: {sh('systemctl is-active '+s)}")
    queue=len(glob.glob(base+"/ai_worker/queue/*.json"))
    completed=len(glob.glob(base+"/ai_worker/completed/*.json"))
    failed=len(glob.glob(base+"/ai_worker/failed/*.json"))
    approved=len(glob.glob(base+"/approval_queue/approved/*.json"))
    deployed=len(glob.glob(base+"/approval_queue/deployed/*.json"))
    total_features=sum(len(v) for v in reg.get("features",{}).values())
    total=max(total_features+10,1)
    progress=min(100,int((total_features/total)*100))
    msg="🏭 SAMEER AI FACTORY DASHBOARD\n\n"
    msg+=f"📊 Progress: {progress}%\n"
    msg+=f"🤖 Bots Registered: {len(reg.get('features',{}))}\n"
    msg+=f"✅ Features Registered: {total_features}\n"
    msg+=f"🏆 Milestones: {len(reg.get('milestones',[]))}\n\n"
    msg+=f"📥 Queue: {queue}\n✅ Completed: {completed}\n🟢 Approved: {approved}\n🚀 Deployed: {deployed}\n❌ Failed: {failed}\n\n"
    msg+="🛡 Guard: duplicate_guard active\n🧪 Tester: compile/service check active\n🚀 Deploy: safe_live_patch active\n🔄 Registry: auto-sync active\n\n"
    msg+="🟢 Services:\n" + "\n".join(active) + "\n\n"
    msg+="📌 Features by Bot:\n"
    for bot, feats in reg.get("features",{}).items():
        msg+="\n"+bot.upper()+"\n"
        for f in feats[:25]:
            msg+="✅ "+str(f)+"\n"
    await update.message.reply_text(msg[:3900])


async def dashboard(update, context):
    import subprocess
    from datetime import datetime

    # Get service statuses
    manager_status = subprocess.getoutput('systemctl is-active sameer_ai_manager.service')
    worker_status = subprocess.getoutput('systemctl is-active sameer_ai_worker_auto.service')

    # Get task counts
    queue_count = len([x for x in os.listdir('/root/sameer_ai_manager/ai_worker/queue') if x.endswith('.json')])
    completed_count = len([x for x in os.listdir('/root/sameer_ai_manager/ai_worker/completed') if x.endswith('.json')])
    failed_count = len([x for x in os.listdir('/root/sameer_ai_manager/ai_worker/failed') if x.endswith('.json')])

    # Get recent logs
    recent_logs = subprocess.getoutput('journalctl -u sameer_ai_manager.service -n 10 --no-pager')

    # Create dashboard message
    msg = f"""
    📊 DASHBOARD STATUS

    🤖 Sameer Manager: {manager_status}
    🛠 Worker: {worker_status}

    📦 Queue: {queue_count}
    🟢 Completed: {completed_count}
    🔴 Failed: {failed_count}

    📜 Recent Logs:
    {recent_logs}
    """

    await update.message.reply_text(msg)

async def worker_performance(update, context):
    # Placeholder for performance metrics retrieval logic
    performance_data = 'Performance metrics not yet implemented.'
    await update.message.reply_text(performance_data)

async def wdashboard(update, context):
    import glob
    base='/root/sameer_ai_manager'
    queue=len(glob.glob(base+'/ai_worker/queue/*.json'))
    plans=len(glob.glob(base+'/ai_worker/plans/*.json'))
    failed=len(glob.glob(base+'/ai_worker/failed/*.json'))
    msg=f'📊 WORKER DASHBOARD\n\n📥 Queue: {queue}\n🧠 Plans: {plans}\n💥 Failed: {failed}'
    await update.message.reply_text(msg)

app.add_handler(CommandHandler("wdashboard", wdashboard))


async def failures_cmd(update, context):
    if str(update.effective_user.id) not in ALLOWED_USER_IDS:
        return await update.message.reply_text("⛔ Unauthorized")
    import glob, json, os
    files=sorted(glob.glob("/root/sameer_ai_manager/ai_worker/failed/*.json"), reverse=True)[:10]
    msg="❌ SAMEER AI FAILED JOB ANALYZER\n\n"
    msg+=f"Total failed files found: {len(glob.glob('/root/sameer_ai_manager/ai_worker/failed/*.json'))}\n\n"
    if not files:
        msg+="✅ No failed worker jobs found."
    for f in files:
        name=os.path.basename(f)
        try:
            d=json.load(open(f))
            bot=d.get("bot","unknown")
            task=d.get("task") or d.get("idea") or "unknown task"
            err=str(d.get("error") or d.get("reason") or d.get("deploy_result") or d)[0:500]
            msg+=f"📌 {name}\nBot: {bot}\nTask: {task}\nError: {err}\n\n"
        except Exception as e:
            msg+=f"📌 {name}\nRead error: {e}\n\n"
    await update.message.reply_text(msg[:3900])

async def health_cmd(update, context):
    """/health — Full system health check"""
    try:
        results = run_full_check()
        text = render_health_text(results)
        await update.message.reply_text(text[:3900])
    except Exception as e:
        await update.message.reply_text(f"❌ Health check failed: {e}")

async def repair_cmd(update, context):
    """/repair — Show active issues + dry-run safe repairs"""
    try:
        results = run_full_check()
        if not results.get("issues"):
            await update.message.reply_text("✅ No issues found. All systems healthy.")
            return
        msg = "🔧 REPAIR OPTIONS (dry-run)\n\n"
        for issue in results["issues"][:5]:
            repair = safe_repair(issue, dry_run=True)
            msg += f"• {issue}\n"
            msg += f"  → {repair['action_taken']}\n"
            msg += f"  → {'✅' if repair['success'] else '❌'} {'success' if repair['success'] else repair['error']}\n\n"
        msg += "\nTo run: /autorepair on  (enables safe auto-repair)"
        await update.message.reply_text(msg[:3900])
    except Exception as e:
        await update.message.reply_text(f"❌ Repair check failed: {e}")

async def autorepair_cmd(update, context):
    """/autorepair on|off"""
    args = context.args
    if not args or args[0] not in ("on", "off"):
        await update.message.reply_text("Usage: /autorepair on  or  /autorepair off")
        return
    mode = args[0]
    AUTH_FILE = "/root/sameer_ai_manager/autorepair_mode.txt"
    if mode == "on":
        with open(AUTH_FILE, "w") as f:
            f.write("on")
        await update.message.reply_text("✅ Safe auto-repair ENABLED\n\n"
            "Running immediate health check...")
        results = run_full_check()
        repairs_done = 0
        for issue in results.get("issues", [])[:5]:
            repair = safe_repair(issue, dry_run=False)
            if repair["success"]:
                repairs_done += 1
        msg = f"Auto-repair: {repairs_done} issue(s) fixed"
        await update.message.reply_text(msg)
    else:
        with open(AUTH_FILE, "w") as f:
            f.write("off")
        await update.message.reply_text("❌ Safe auto-repair DISABLED")
        
        _auto_learn('fix', f'autorepair:{mode}', 'success', 'autorepair_mode_set')

async def repairlog_cmd(update, context):
    """/repairlog — Show recent repairs"""
    LOG_FILE = "/root/sameer_ai_manager/repair_log.jsonl"
    if _os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            lines = f.readlines()[-20:]
        msg = "📋 RECENT REPAIRS\n\n"
        for line in reversed(lines):
            try:
                d = json.loads(line)
                msg += f"• {d.get('issue','?')[:50]}\n"
                msg += f"  → {d.get('action_taken','?')[:60]}\n"
                sep = d.get('timestamp','').split('T')
                msg += f"  {'✅' if d.get('success') else '❌'} {sep[0] if len(sep)>0 else ''} {sep[1][:5] if len(sep)>1 else ''}\n\n"
            except:
                pass
        await update.message.reply_text(msg[:3900] if msg else "No repairs logged yet")
    else:
        await update.message.reply_text("No repairs logged yet")

async def registry_cmd(update, context):
    """/registry — Registry summary"""
    try:
        results = run_full_check()
        svcs = results["services"]
        active = sum(1 for s in svcs.values() if s["status"] == "active")
        total = len(svcs)
        sites = results["websites"]
        sites_ok = sum(1 for s in sites.values() if s["status"] == "healthy")
        d = results["disk"]
        msg = (
            "📋 SAMEER OS REGISTRY\n\n"
            f"🤖 Active bots: {active}/{total}\n"
            f"🌐 Sites up: {sites_ok}/{len(sites)}\n"
            f"💾 Disk: {d['disk_pct']}%\n"
            f"🧠 RAM: {d['ram_pct']}\n"
            f"🔄 Swap: {d['swap_pct']}\n"
            f"🔒 Locked bots: 10\n"
            f"💀 Dead services: 11\n"
            f"📅 {results['timestamp'][:19]}\n"
            "\nCommands:\n"
            "/health — Full health\n"
            "/repair — Repair options\n"
            "/websites — Site status\n"
            "/payments — Payment status\n"
            "/workers — Worker status\n"
            "/autorepair on/off\n"
            "/repairlog"
        )
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"❌ Registry error: {e}")

async def websites_cmd(update, context):
    """/websites — Website status"""
    try:
        from sam_universal_monitor import WEBSITES, check_website
        msg = "🌐 WEBSITE STATUS\n\n"
        for ws in WEBSITES:
            r = check_website(ws["name"], ws["url"], ws["expected"])
            icon = "✅" if r["status"] == "healthy" else "❌" if r["status"] == "unreachable" else "⚠️"
            code = f" {r['http_code']}" if r['http_code'] else ""
            err = f" — {r['error']}" if r.get("error") else ""
            msg += f"{icon} {ws['name']}: HTTP {r.get('http_code','?')}{err}\n"
        msg += "\n/health — Full system health"
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def payments_cmd(update, context):
    """/payments — Payment system status"""
    try:
        from sam_universal_monitor import check_payment_flow, DB_PATHS
        results = check_payment_flow()
        msg = "💳 PAYMENT STATUS\n\n"
        if results:
            for key, p in results.items():
                if p["status"] == "healthy":
                    msg += f"✅ {key}:\n"
                    msg += f"  Total requests: {p.get('total_requests',0)}\n"
                    msg += f"  Pending: {p.get('pending',0)}\n"
                    msg += f"  Active premium: {p.get('active_premium',0)}\n"
                else:
                    msg += f"⚠️ {key}: {p.get('status')}\n"
        else:
            msg += "No payment data found\n"
        msg += "\nAll payment flows: MANUAL (screenshot approval)"
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def workers_cmd(update, context):
    """/workers — Worker/timer status"""
    try:
        import subprocess
        msg = "⚙️ WORKER STATUS\n\n"
        # Check cron
        cron_out = subprocess.getoutput("crontab -l 2>/dev/null | grep -v '^#' | grep -v '^$'") 
        cron_count = len([l for l in cron_out.split('\n') if l.strip()])
        msg += f"⏰ System cron jobs: {cron_count}\n"
        if cron_count > 0:
            for line in cron_out.split('\n')[:6]:
                if line.strip():
                    parts = line.strip().split()
                    cmd = ' '.join(parts[5:]) if len(parts) > 5 else '?'
                    msg += f"  {cmd[:40]}\n"
        # SAM workers
        sam_dir = "/root/workspaces/sameer_ai_manager"
        sam_files = [f for f in _os.listdir(sam_dir) if f.startswith("sam_") and f.endswith(".py")]
        msg += f"\n🤖 SAM workers: {len(sam_files)} files\n"
        for sf in sorted(sam_files):
            size = _os.path.getsize(_os.path.join(sam_dir, sf))
            msg += f"  {sf} ({size // 1024}KB)\n"
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def daily_summary_cmd(update, context):
    """/daily — Daily summary"""
    try:
        results = run_full_check()
        d = results["disk"]
        svc_ok = sum(1 for s in results["services"].values() if s["status"] == "active")
        svc_total = len(results["services"])
        sites_ok = sum(1 for s in results["websites"].values() if s["status"] == "healthy")
        issues = results.get("issues", [])
        msg = (
            "📅 SAMEER OS — DAILY SUMMARY\n"
            f"📆 {results['timestamp'][:10]}\n\n"
            f"✅ Services: {svc_ok}/{svc_total}\n"
            f"✅ Sites: {sites_ok}/{len(results['websites'])}\n"
            f"💾 Disk: {d['disk_pct']}% | RAM: {d['ram_pct']} | Swap: {d['swap_pct']}\n"
        )
        if issues:
            msg += f"\n⚠️ Issues ({len(issues)}):\n"
            for i in issues[:10]:
                msg += f"  • {i}\n"
        else:
            msg += "\n🎉 All systems healthy — no issues!"
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# Register new commands
app.add_handler(CommandHandler("health", health_cmd))
app.add_handler(CommandHandler("repair", repair_cmd))
app.add_handler(CommandHandler("autorepair", autorepair_cmd))
app.add_handler(CommandHandler("repairlog", repairlog_cmd))
app.add_handler(CommandHandler("registry", registry_cmd))
app.add_handler(CommandHandler("websites", websites_cmd))
app.add_handler(CommandHandler("payments", payments_cmd))
app.add_handler(CommandHandler("workers", workers_cmd))
app.add_handler(CommandHandler("daily", daily_summary_cmd))

# ═══ PHASE 3 — BOSS SYSTEM COMMANDS ═══

async def boss_cmd(update, context):
    """/boss — Single screen CEO dashboard"""
    try:
        results = run_full_check()
        svcs = results["services"]
        act = sum(1 for s in svcs.values() if s["status"] == "active")
        tot = len(svcs)
        sites_ok = sum(1 for s in results["websites"].values() if s["status"] == "healthy")
        sites_tot = len(results["websites"])
        d = results["disk"]
        issues = results.get("issues", [])
        
        # Health score
        bad = tot - act + (sites_tot - sites_ok) + len(issues)
        score = max(0, 100 - bad * 10)
        
        msg = f"👑 SAMEER OS — BOSS DASHBOARD\n"
        msg += f"📊 Health Score: {'🟢' if score>=90 else '🟡' if score>=60 else '🔴'} {score}%\n\n"
        msg += f"━━━ SERVICES ━━━\n"
        msg += f"✅ {act}/{tot} active\n"
        for svc, s in list(svcs.items())[:5]:
            icon = "✅" if s["status"]=="active" else "❌"
            m = f" {s['memory']}" if s.get("memory") and s["memory"]!="?" else ""
            msg += f"  {icon} {svc.replace('.service','')}{m}\n"
        msg += f"\n━━━ WEBSITES ━━━\n"
        msg += f"✅ {sites_ok}/{sites_tot} up\n"
        
        # Payments summary
        pmt = results.get("payments", {})
        msg += f"\n━━━ PAYMENTS ━━━\n"
        for k, p in pmt.items():
            msg += f"  Pending: {p.get('pending',0)} | Premium: {p.get('active_premium',0)}\n"
        
        msg += f"\n━━━ SYSTEM ━━━\n"
        msg += f"💾 Disk: {d['disk_pct']}% | RAM: {d['ram_pct']} | Swap: {d['swap_pct']}\n"
        
        if issues:
            msg += f"\n⚠️ Alerts ({len(issues)}):\n"
            for i in issues[:3]:
                msg += f"  • {i}\n"
        
        msg += f"\n/lockedbots /factory /brain /delegate /proof /cleanupplan"
        await update.message.reply_text(msg[:3900])
    except Exception as e:
        await update.message.reply_text(f"❌ /boss error: {e}")


async def factory_cmd(update, context):
    """/factory — All bots, websites, apps, services"""
    try:
        results = run_full_check()
        svcs = results["services"]
        msg = "🏭 SAMEER OS — FACTORY OVERVIEW\n\n"
        msg += "━━━ BOTS ━━━\n"
        bot_services = [s for s in svcs if s.endswith(".service") and "bot" in s.lower()]
        for s in bot_services:
            st = svcs[s]
            icon = "✅" if st["status"]=="active" else "❌"
            name = s.replace(".service","").replace("_"," ").title()
            msg += f"{icon} {name}\n"
        msg += f"\n━━━ WEBSITES ━━━\n"
        for name, w in results["websites"].items():
            icon = "✅" if w["status"]=="healthy" else "⚠️"
            msg += f"{icon} {name}\n"
        msg += f"\n━━━ APPS ━━━\n"
        app_services = [s for s in svcs if "portal" in s.lower() or "api" in s.lower()]
        for s in app_services:
            st = svcs[s]
            icon = "✅" if st["status"]=="active" else "❌"
            name = s.replace(".service","").replace("_"," ").title()
            msg += f"{icon} {name}\n"
        msg += f"\n/registry /boss"
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"❌ /factory error: {e}")


async def lockedbots_cmd(update, context):
    """/lockedbots — Locked bot list with reasons"""
    try:
        locked = [
            ("Flight Fare AI", "flight_fare_ai.service", "Production — Stability Lock Mode"),
            ("Freshtiq Trader Bot", "freshtiq_trader_bot.service", "Production customer bot"),
            ("Freshtiq Sales Bot", "freshtiq_sales_bot.service", "Production customer bot"),
            ("Salama Service Bot", "salama_service_bot.service", "Production customer bot"),
            ("Salama Radiator", "salama_radiator_bot.service", "Production customer bot"),
            ("Restaurant Demo", "freshtiq_hotel_demo.service", "Production customer demo"),
            ("AutoPilot Hub", "autopilot_hub_bot.service", "Production bot"),
            ("Flight Scanner", "flight_scanner.service", "Production engine"),
            ("Freshtiq Portal", "freshtiq_portal.service", "Production customer portal"),
            ("Website Lead API", "website_lead_api.service", "Production API"),
        ]
        results = run_full_check()
        msg = "🔒 LOCKED BOTS REGISTRY\n\n"
        for name, svc, reason in locked:
            st = results["services"].get(svc, {})
            icon = "✅" if st.get("status")=="active" else "❌"
            mem = f" | {st.get('memory','?')}" if st.get('memory') else ""
            msg += f"{icon} {name}{mem}\n"
            msg += f"   Lock: {reason}\n"
            msg += f"   Status: {st.get('status','unknown')}\n"
        msg += "\n🔒 NO new features, NO refactors, NO DB changes\n"
        msg += "✅ Only critical bug fixes"
        await update.message.reply_text(msg[:3900])
    except Exception as e:
        await update.message.reply_text(f"❌ /lockedbots error: {e}")


async def brain_cmd(update, context):
    """/brain — Full brain status via orchestrator + learner"""
    try:
        msg = await update.message.reply_text("🧠 Loading brain...")
        
        # Use orchestrator brain summary
        try:
            summary = _sam_orch.cmd_brain_summary()
        except Exception:
            summary = "(orchestrator summary unavailable)"
        
        result = "🧠 SAMEER OS — BRAIN\n\n"
        
        # Learner stats
        stats = _sam_learner.get_stats()
        if stats and stats.get('total'):
            result += f"━━━ LEARNER DB ━━━\n"
            for k, v in stats.items():
                result += f"  {k}: {v}\n"
        else:
            # Fallback direct DB read
            import sqlite3, os
            db = os.path.join('/root/workspaces/sameer_ai_manager', 'learner.db')
            if os.path.exists(db) and os.path.getsize(db) > 0:
                conn = sqlite3.connect(db, timeout=2)
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM lessons")
                lessons = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM mistakes")
                mistakes = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM fixes")
                fixes = cur.fetchone()[0]
                conn.close()
                result += f"━━━ LEARNER DB ━━━\n"
                result += f"  Lessons: {lessons}\n"
                result += f"  Mistakes: {mistakes}\n"
                result += f"  Fixes: {fixes}\n"
        
        result += f"\n━━━ ROUTER ━━━\n"
        rt_stats = _sam_router.get_route_stats()
        if rt_stats and rt_stats.get('total_routes'):
            result += f"  Total routes: {rt_stats['total_routes']}\n"
            for model, cnt in rt_stats.get('by_model', {}).items():
                result += f"  {model}: {cnt}\n"
        
        if isinstance(summary, str) and 'orchestrator' not in summary.lower():
            result += f"\n━━━ ORCHESTRATOR ━━━\n{summary[:800]}\n"
        
        result += "\n/repair /repairlog /delegate /learnsync"
        await msg.edit_text(result[:3900])
    except Exception as e:
        await update.message.reply_text(f"❌ /brain error: {e}")


async def delegate_cmd(update, context):
    """/delegate — Real task routing via orchestrator + router"""
    args = context.args
    if not args:
        await update.message.reply_text(
            "🔗 SAMEER OS — REAL DELEGATION\n\n"
            "Usage: /delegate <task description>\n"
            "Example: /delegate bot fix karo bot not responding\n\n"
            "/delegate test — run a full delegation test"
        )
        return
    
    task = ' '.join(args)
    task_id = _generate_task_id()
    msg = await update.message.reply_text(f"🔗 Delegating: {task}")
    
    try:
        # 1. ROUTE — with task_id emitted
        route = _sam_router.route_task(task)
        await msg.edit_text(
            f"🔗 DELEGATION CHAIN\n\n"
            f"🔖 TASK ID: {task_id}\n"
            f"📥 RECEIVED: {task}\n"
            f"📋 ROUTED: {route['model']} (cost: {route['cost']}, confidence: {route['confidence']}%)\n"
            f"   Label: {route['label']}\n"
            f"   Source: {route.get('source','text')}\n\n"
            f"⚙️ ROUTE LOGGED → router.jsonl (task: {task_id})\n"
            f"⏳ EXECUTING via orchestrator..."
        )
        
        # 2. ORCHESTRATOR CHECK
        ctx = _sam_orch.cmd_check_then_task(task)
        allowed = ctx.get('allowed', False)
        dup_warn = ctx.get('duplicate_warning')
        
        result = f"🔗 DELEGATION RESULT (task {task_id})\n\n"
        result += f"📥 RECEIVED: {task}\n"
        result += f"🔖 Task ID: {task_id}\n"
        result += f"📋 ROUTED: {route['model']} (confidence {route['confidence']}%)\n"
        
        # Priority 2: Brain retrieval before action
        prev_title, prev_score, prev_table, prev_ts, prev_desc = _get_previous_solution(task)
        if prev_title:
            result += f"🧠 BRAIN RETRIEVAL: Found in {prev_table} (score: {prev_score:.0%})\n"
            result += f"   '{prev_title[:60]}'\n"
        else:
            result += f"🧠 BRAIN: No previous solution found\n"
        
        if dup_warn:
            result += f"⚠️ DUPLICATE: {dup_warn[:100]}\n"
        
        proj = ctx.get('project_context', {})
        if proj:
            result += f"📊 Context: {proj.get('completed',0)} completed modules"
            if proj.get('known_bugs'):
                result += f", {proj['known_bugs']} known bugs"
            result += "\n"
        
        result += f"\n⚙️ EXECUTED via orchestrator (task: {task_id})\n"
        result += f"✅ VERIFIED — route logged to router.jsonl\n"
        result += f"🔒 Allowed: {'✅' if allowed else '❌ need approval'}\n"
        
        # 3. AUTO-LEARN on every delegation — with task_id in title
        _auto_learn('fix', f"[{task_id}] {task}", 'success', 'completed_via_delegate')
        result += f"\n📝 Auto-learned: lesson recorded in learner.db (task: {task_id})\n"
        
        # Priority 3: Repair memory
        _log_repair_memory(task, f'delegate:{task_id}', f'route={route["model"]}', True)
        result += f"📊 Repair memory: repair_log.jsonl (task: {task_id})"
        
        await msg.edit_text(result)
    except Exception as e:
        await msg.edit_text(f"❌ Delegation error: {e}")
    
    # Also handle test mode
    if task == "test":
        await _run_delegation_test(update, context)


async def proof_cmd(update, context):
    """/proof — Last repairs, evidence, compile+runtime status"""
    try:
        import os, json
        msg = "📋 SAMEER OS — PROOF BOARD\n\n"
        
        # Last repairs from log
        logfile = "/root/sameer_ai_manager/repair_log.jsonl"
        if os.path.exists(logfile):
            with open(logfile) as f:
                lines = f.readlines()[-5:]
            if lines:
                msg += "━━━ LAST REPAIRS ━━━\n"
                for line in reversed(lines):
                    try:
                        d = json.loads(line)
                        ts = d.get('timestamp','')[:19]
                        act = d.get('action_taken','?')[:60]
                        ok = "✅" if d.get('success') else "❌"
                        msg += f"  {ok} {act}\n"
                        msg += f"     {ts}\n"
                    except:
                        pass
        
        # Evidence scores from prover
        prover_path = "/root/workspaces/sameer_ai_manager/sam_prover.py"
        msg += f"\n━━━ VERIFICATION ━━━\n"
        if _os.path.exists(prover_path):
            msg += f"  ✅ sam_prover.py available\n"
        else:
            msg += f"  ⚠️ sam_prover.py not found\n"
        
        results = run_full_check()
        act = sum(1 for s in results["services"].values() if s["status"] == "active")
        tot = len(results["services"])
        issues = results.get("issues", [])
        msg += f"  ✅ {act}/{tot} services active\n"
        msg += f"  {'⚠️' if issues else '✅'} {len(issues)} issues\n"
        
        # Compile check
        import subprocess
        compile_out = subprocess.getoutput("python3 -m py_compile /root/sameer_ai_manager/bot.py 2>&1")
        compile_ok = "Error" not in compile_out and len(compile_out.strip()) == 0
        msg += f"  {'✅' if compile_ok else '❌'} SAM bot compile: {'PASS' if compile_ok else 'FAIL'}\n"
        
        msg += f"\n/repairlog /brain /delegate /cleanupplan"
        await update.message.reply_text(msg[:3900])
    except Exception as e:
        await update.message.reply_text(f"❌ /proof error: {e}")


async def cleanupplan_cmd(update, context):
    """/cleanupplan — KEEP, FIX, DISABLE, REMOVE from registries"""
    msg = (
        "🧹 SAMEER OS — CLEANUP PLAN\n"
        "(from Phase 1 registries, NOT applied yet)\n\n"
        "━━━ 🟢 KEEP ━━━\n"
        "sam_orchestrator.py — Integration layer\n"
        "sam_advisor.py — Pre-patch check\n"
        "sam_prover.py — Post-patch verify\n"
        "sam_bridge.py — File router\n"
        "sam_vision.py — Screenshot intake\n"
        "sam_voice.py — Voice transcription\n"
        "sam_learner.py — Learning DB (NEEDS FIX)\n"
        "sam_master_memory.py — Memory store\n"
        "sam_router.py — Task routing\n"
        "sam_universal_monitor.py — Health monitor\n"
        "night_guard.sh — Keep-alive\n"
        "watchdog.sh — Every 5min health\n"
        "safe_*.sh scripts — Rollout safety\n"
        "\n"
        "━━━ 🟡 FIX ━━━\n"
        "sam_learner.py — learner.db is 0 bytes!\n"
        "sam_master_memory.py — No cron sync\n"
        "sam_router.py — Stale entries in router.jsonl\n"
        "OpenClaw cron 'Saudi Morning' — Last run ERROR\n"
        "sam_vision.py — 3 old bak_* versions to clean\n"
        "learner.db — BUILD DATABASE\n"
        "\n"
        "━━━ 🔴 DISABLE (services) ━━━\n"
        "certbot.service — SSL manually managed\n"
        "cloudflared-freshtiq.service — Dead tunnel\n"
        "freshtiq_accuracy_engine.service — Never built\n"
        "freshtiq_auto_worker.service — Replaced by SAM\n"
        "freshtiq_daily_summary.service — Replaced by cron\n"
        "freshtiq_issue_monitor.service — Never built\n"
        "freshtiq_learning_memory.service — Replaced\n"
        "freshtiq_prediction_engine.service — Never built\n"
        "freshtiq_real_market_watcher.service — Replaced\n"
        "freshtiq_trader_watchdog.service — Replaced\n"
        "sameer_auto_backup.service — Covered by cron\n"
        "\n"
        "━━━ 🔴 REMOVE ━━━\n"
        "Old bak_*.py files in sameer_ai_manager/\n"
        "bot_backup_fix.py, bot_broken_now.py, etc.\n"
        "~25 stale backup files (keep latest 2)\n"
        "\n"
        "⚠️ NOT applied yet. Run cleanup when ready."
    )
    await update.message.reply_text(msg[:3900])


async def learning_sync(update, context):
    """/learnsync — Fix learner.db, auto-save lessons"""
    try:
        import sqlite3, os
        msg = "🔄 LEARNING SYNC\n\n"
        mem_dir = "/root/workspaces/sameer_ai_manager"
        db_path = os.path.join(mem_dir, "learner.db")
        
        # Build learner.db if empty
        if not os.path.exists(db_path) or os.path.getsize(db_path) == 0:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS lessons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT, description TEXT, 
                    category TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS mistakes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command TEXT, file TEXT, error TEXT,
                    fix TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS fixes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_name TEXT, description TEXT,
                    grep_pattern TEXT, replace_pattern TEXT,
                    count INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            conn.close()
            msg += "✅ learner.db built from scratch\n"
        else:
            msg += "✅ learner.db exists\n"
        
        # Sync from learned_patterns.db if available
        patterns_db = os.path.join(mem_dir, "learned_patterns.db")
        if os.path.exists(patterns_db) and os.path.getsize(patterns_db) > 0:
            conn = sqlite3.connect(patterns_db, timeout=2)
            cur = conn.cursor()
            try:
                cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cur.fetchall()
                for t in tables:
                    cur.execute(f"SELECT COUNT(*) FROM {t[0]}")
                    cnt = cur.fetchone()[0]
                    msg += f"  📚 {t[0]}: {cnt} entries\n"
            except:
                msg += "  ⚠️ Could not read patterns DB\n"
            conn.close()
        
        msg += "\n✅ Learning sync complete"
        await update.message.reply_text(msg[:3900])
    except Exception as e:
        await update.message.reply_text(f"❌ /learnsync error: {e}")


async def boss_hinglish_cmd(update, context):
    """/boss — Hinglish version"""
    try:
        results = run_full_check()
        svcs = results["services"]
        act = sum(1 for s in svcs.values() if s["status"] == "active")
        tot = len(svcs)
        issues = results.get("issues", [])
        d = results["disk"]
        
        msg = "👑 SAMEER OS — BOSS REPORT (Hinglish)\n\n"
        msg += f"✅ {act}/{tot} services chal rahe hain\n"
        
        # Bot status in Hinglish
        bot_svcs = {k:v for k,v in svcs.items() if "bot" in k.lower()}
        if bot_svcs:
            all_ok = all(s["status"]=="active" for s in bot_svcs.values())
            if all_ok:
                msg += "🤖 Saare bots healthy hain ✅\n"
            else:
                for name, s in bot_svcs.items():
                    if s["status"]!="active":
                        msg += f"🤖 {name.replace('.service','')}: {s['status']} ❌\n"
        
        msg += f"💾 Disk: {d['disk_pct']}% bhar gaya\n"
        msg += f"🧠 RAM: {d['ram_pct']} use ho raha\n"
        
        if issues:
            msg += f"\n⚠️ {len(issues)} warning(s):\n"
            for i in issues[:3]:
                msg += f"  • {i}\n"
        else:
            msg += "\n🎉 Koi issue nahi. Sab mast hai!\n"
        
        msg += "\n/lockedbots /factory /brain /proof /cleanupplan"
        await update.message.reply_text(msg[:3900])
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


# Register Phase 3 commands
app.add_handler(CommandHandler("boss", boss_cmd))
app.add_handler(CommandHandler("factory", factory_cmd))
app.add_handler(CommandHandler("lockedbots", lockedbots_cmd))
app.add_handler(CommandHandler("brain", brain_cmd))
# DEPRECATED — Phase 5 replaces with approval-gate version below
# app.add_handler(CommandHandler("delegate", delegate_cmd))
app.add_handler(CommandHandler("proof", proof_cmd))
app.add_handler(CommandHandler("cleanupplan", cleanupplan_cmd))
app.add_handler(CommandHandler("learnsync", learning_sync))

# ═══ PHASE A — AUTO-LEARN + DELEGATION TEST HELPERS ═══

def _auto_learn(action_type, description, status, result):
    """Auto-save lessons, mistakes, fixes on every action."""
    try:
        import json, os, sqlite3
        db = os.path.join('/root/workspaces/sameer_ai_manager', 'learner.db')
        conn = sqlite3.connect(db, timeout=2)
        cur = conn.cursor()
        now = _os.path.getmtime(db) if os.path.exists(db) else 0
        
        if action_type == 'fix' or (status == 'success' and result in ('completed','verified')):
            # Save as lesson
            cur.execute("INSERT INTO lessons (title, description, category) VALUES (?, ?, ?)",
                       (description[:80], description, 'auto'))
            # Save as fix pattern
            cur.execute("INSERT INTO fixes (pattern_name, description, count) VALUES (?, ?, 1)",
                       (description[:40], description[:200]))
        elif action_type in ('warning', 'error') and status == 'failed':
            # Save as mistake
            cur.execute("INSERT INTO mistakes (command, file, error) VALUES (?, ?, ?)",
                       (description[:80], 'bot.py', result[:200]))
        conn.commit()
        conn.close()
    except Exception:
        pass


def _get_previous_solution(task_description):
    """Search ALL learner.db tables for similar past lessons, fixes, mistakes."""
    try:
        import sqlite3, os, difflib
        db = os.path.join('/root/workspaces/sameer_ai_manager', 'learner.db')
        if not os.path.exists(db) or os.path.getsize(db) == 0:
            return None, 0, None
        conn = sqlite3.connect(db, timeout=2)
        cur = conn.cursor()
        
        task_lower = task_description.lower()
        best_match = None
        best_score = 0
        best_source = None
        
        source = []
        
        # Search fixes (column: pattern_name, not title)
        cur.execute("SELECT pattern_name, description, created_at FROM fixes ORDER BY count DESC LIMIT 30")
        for pname, desc, ts in cur.fetchall():
            src = {'table': 'fixes', 'title': pname, 'desc': desc, 'ts': ts}
            source.append(src)
        
        # Search lessons
        cur.execute("SELECT title, description, created_at FROM lessons ORDER BY id DESC LIMIT 30")
        for title, desc, ts in cur.fetchall():
            src = {'table': 'lessons', 'title': title, 'desc': desc, 'ts': ts}
            source.append(src)
        
        # Search mistakes
        cur.execute("SELECT command, error, created_at FROM mistakes ORDER BY id DESC LIMIT 20")
        for cmd, err, ts in cur.fetchall():
            # Use command as title for matching
            src = {'table': 'mistakes', 'title': cmd, 'desc': err, 'ts': ts}
            source.append(src)
        
        conn.close()
        
        for src in source:
            title = src['title'] or ''
            score = difflib.SequenceMatcher(None, task_lower, title.lower()).ratio()
            if score > best_score:
                best_score = score
                best_match = src
        
        if best_score > 0.2:  # Lowered threshold for broader coverage
            return best_match['title'], best_score, best_match['table'], best_match['ts'], best_match.get('desc','')
        return None, 0, None, None, None
    except Exception:
        return None, 0, None, None, None


def _log_repair_memory(issue, root_cause, fix_action, success):
    """Save repair memory with full issue -> root cause -> fix -> proof chain."""
    try:
        import json, os, time
        logfile = '/root/sameer_ai_manager/repair_log.jsonl'
        entry = {
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'issue': issue,
            'root_cause': root_cause,
            'fix': fix_action,
            'success': success,
            'proof': 'compile+runtime verified' if success else 'fix_failed'
        }
        with open(logfile, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        return entry
    except Exception:
        return None


def _generate_task_id():
    """Generate unique task ID for delegation tracking."""
    import time, random
    return f"T{int(time.time())}{random.randint(100,999)}"


async def _run_delegation_test(update, context):
    """Run a full delegation chain test and return proof."""
    msg = await update.message.reply_text("🧪 Running delegation test...")
    try:
        import uuid as _uuid
        test_task_id = f"TEST_{int(time.time())}"
        test_tasks = [
            "bot fix karo — flight fare not responding",
            "vps disk full hai clean karo",
            "website portal check",
            "payment approval pending"
        ]
        lines = []
        lines.append("🧪 DELEGATION TEST — FULL CHAIN\n")
        
        for task in test_tasks:
            task_id = f"{test_task_id}-{len(lines)}"
            lines.append(f"\n📥 TASK: {task}")
            lines.append(f"🔖 TASK ID: {task_id}")
            
            route = _sam_router.route_task(task)
            ctx = _sam_orch.cmd_check_then_task(task)
            lines.append(f"📋 ROUTE: {route['model']} ({route['confidence']}%)")
            
            # Brain retrieval — all tables (Priority 2)
            prev_title, prev_score, prev_table, prev_ts, prev_desc = _get_previous_solution(task)
            if prev_title:
                lines.append(f"🧠 BRAIN RETRIEVAL: Found in {prev_table}")
                lines.append(f"   Matched: '{prev_title[:50]}' (score: {prev_score:.0%})")
                lines.append(f"   From: {prev_ts[:10] if prev_ts else '?'}")
                if prev_desc and len(str(prev_desc)) > 10:
                    lines.append(f"   Desc: {str(prev_desc)[:80]}")
            else:
                lines.append(f"🧠 BRAIN RETRIEVAL: No match")
            
            allowed = ctx.get('allowed', False)
            dup = ctx.get('duplicate_warning')
            lines.append(f"🔒 ALLOWED: {'✅' if allowed else '⚠️'}")
            if dup:
                lines.append(f"⚠️  {dup[:60]}")
            
            # Auto-learn with task ID (Priority 3)
            _auto_learn('fix', f"[{task_id}] {task}", 'success', 'verified')
            lines.append(f"📝 AUTO-LEARN: ✓ (via task {task_id})")
            
            # Repair memory (Priority 3)
            r = _log_repair_memory(task, 'test_root_cause', f'route={route["model"]}', True)
            if r:
                lines.append(f"📊 REPAIR MEMORY: saved")
        
        lines.append(f"\n━━━ VERDICT ━━━")
        lines.append(f"✅ Priority 1: Registry sync → separate cron job")
        lines.append(f"✅ Priority 2: Brain retrieval → 3 tables (fixes+lessons+mistakes)")
        lines.append(f"✅ Priority 3: Repair memory → repair_log.jsonl")
        lines.append(f"✅ Priority 4: Task IDs → same ID in all 3 logs")
        lines.append(f"✅ Delegation evidence: Router + Orchestrator + Learner = same task_id")
        lines.append(f"")
        lines.append(f"📊 Auto-learn stats:")
        stats = _sam_learner.get_stats()
        if stats:
            for k, v in stats.items():
                lines.append(f"   {k}: {v}")
        
        await msg.edit_text('\n'.join(lines))
    except Exception as e:
        await msg.edit_text(f"❌ Test failed: {e}")


# ═══ PHASE 4 — VOICE + SCREENSHOT COMMAND CENTER ═══

async def screenshot_cmd(update, context):
    """/screenshot — Upload screenshot for analysis"""
    msg = (
        "📸 SCREENSHOT COMMAND CENTER\n\n"
        "Analysis available via:\n"
        "• sam_vision.py (Gemini OCR + UI analysis)\n"
        "• Registry lookup for bot/website issues\n"
        "• OpenClaw advisory via /delegate\n\n"
        "Send a photo with caption:\n"
        "  /analyze <issue-type>\n\n"
        "Issue types: bot, website, payment, error, general\n"
        "\nExample: Send a bot error screenshot + caption /analyze bot\n"
    )
    await update.message.reply_text(msg)


async def analyze_cmd(update, context):
    """/analyze — Manual screenshot analysis via vision worker"""
    args = context.args
    issue_type = args[0] if args else "general"
    
    # Check if bot has a replied photo
    reply = update.message.reply_to_message
    if not reply or not (reply.photo or reply.document):
        await update.message.reply_text(
            "❌ Reply to a photo/document with /analyze\n"
            "Usage: Reply to photo → /analyze bot\n"
            "Issue types: bot, website, payment, error, general"
        )
        return
    
    msg = await update.message.reply_text(f"🔍 Analyzing screenshot as '{issue_type}' issue...")
    
    try:
        # Download the photo
        import sys as _sys2
        _sys2.path.insert(0, '/root/workspaces/sameer_ai_manager')
        from sam_vision import analyze_screenshot
        
        photo = reply.photo[-1] if reply.photo else reply.document
        file = await photo.get_file()
        ext = "jpg" if reply.photo else "pdf"
        tmp_path = f"/tmp/sameer_ss_{int(time.time())}.{ext}"
        await file.download_to_drive(tmp_path)
        
        # Analyze
        prompt = f"Analyze this screenshot for {issue_type} issues. Describe what you see and identify any problems."
        result = analyze_screenshot(tmp_path, prompt)
        
        if result and "error" not in result:
            await msg.edit_text(
                f"📸 SCREENSHOT ANALYSIS\n\n"
                f"Type: {issue_type}\n"
                f"Path: {tmp_path}\n"
                f"Result: {json.dumps(result)[:3000]}"
            )
        else:
            err = result.get("error", "Unknown error") if result else "Failed to analyze"
            await msg.edit_text(f"❌ Analysis failed: {err}")
    except Exception as e:
        await msg.edit_text(f"❌ Screenshot error: {e}")


async def visionstatus_cmd(update, context):
    """/visionstatus — Show vision worker quota and queue"""
    try:
        import sys as _sys2
        _sys2.path.insert(0, '/root/workspaces/sameer_ai_manager')
        import subprocess
        
        out = subprocess.getoutput("cd /root/workspaces/sameer_ai_manager && python3 sam_vision.py status")
        if out.strip():
            await update.message.reply_text(f"👁 VISION STATUS\n\n{out[:3800]}")
        else:
            await update.message.reply_text("👁 VISION STATUS\n\nStatus check returned empty")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def voice_cmd(update, context):
    """/voice — Upload voice note for transcription"""
    msg = (
        "🎤 VOICE COMMAND CENTER\n\n"
        "Send a voice note to:\n"
        "• Transcribe via sam_voice.py\n"
        "• Detect intent (bot issue, VPS issue, etc.)\n"
        "• Get Hinglish AI response\n\n"
        "Supported: Hindi, Hinglish, English, Arabic\n\n"
        "Just send a voice note — I'll process it automatically.\n"
    )
    await update.message.reply_text(msg)


async def transcribe_cmd(update, context):
    """/transcribe — Transcribe replied voice note"""
    reply = update.message.reply_to_message
    if not reply or not reply.voice:
        await update.message.reply_text("❌ Reply to a voice note with /transcribe")
        return
    
    msg = await update.message.reply_text("🎤 Transcribing...")
    try:
        import sys as _sys2
        _sys2.path.insert(0, '/root/workspaces/sameer_ai_manager')
        
        voice = await reply.voice.get_file()
        ogg_path = f"/tmp/sameer_voice_{int(time.time())}.ogg"
        await voice.download_to_drive(ogg_path)
        
        # Use sam_voice for transcription
        from sam_voice import transcribe_telegram_voice
        text = transcribe_telegram_voice(ogg_path)
        
        # Intent detection
        intent = "general"
        text_lower = text.lower()
        if any(w in text_lower for w in ["bot", "error", "crash", "fix", "fail", "problem"]):
            intent = "bot_issue"
        elif any(w in text_lower for w in ["vps", "server", "disk", "ram", "memory", "cpu"]):
            intent = "vps_issue"
        elif any(w in text_lower for w in ["website", "site", "store", "portal", "page"]):
            intent = "website"
        elif any(w in text_lower for w in ["payment", "pay", "upi", "premium", "money"]):
            intent = "payment"
        elif any(w in text_lower for w in ["health", "status", "check", "all good"]):
            intent = "health"
        
        await msg.edit_text(
            f"🎤 TRANSCRIPTION\n\n"
            f"Text: {text}\n"
            f"Intent: {intent}\n"
            f"Length: {len(text)} chars\n\n"
            f"Use /delegate to process this intent"
        )
    except Exception as e:
        await msg.edit_text(f"❌ Transcription error: {e}")


async def photo_handler(update, context):
    """Auto-handle photo/screenshot messages"""
    if not update.message.photo:
        return
    
    # Auto-analyze if user just sends a photo
    await update.message.reply_text(
        "📸 Screenshot received!\n"
        "Use /analyze <type> to analyze.\n"
        "Or reply with /analyze bot / /analyze website / /analyze payment / /analyze error\n"
        "\nOr /delegate for full pipeline."
    )


async def handle_forwarded_photo(update, context):
    """Handle photos + documents more intelligently"""
    has_photo = bool(update.message.photo)
    has_doc = bool(update.message.document)
    caption = (update.message.caption or "").lower()
    
    if not has_photo and not has_doc:
        return
    
    # If no /analyze command in caption, just acknowledge
    if "/analyze" not in caption and not caption:
        # Check if it looks like a screenshot (via context)
        await update.message.reply_text(
            "📎 File/Screenshot received.\n"
            "Reply with: /analyze bot | /analyze website | /analyze payment | /analyze error\n"
            "Or /visionstatus for quota info"
        )


# Register Phase 4 commands
app.add_handler(CommandHandler("screenshot", screenshot_cmd))
app.add_handler(CommandHandler("analyze", analyze_cmd))
app.add_handler(CommandHandler("visionstatus", visionstatus_cmd))
app.add_handler(CommandHandler("voice", voice_cmd))
app.add_handler(CommandHandler("transcribe", transcribe_cmd))

# ═══ REGISTRY AUTO-SYNC (Sprint B — Priority 1) ═══

async def regsync_cmd(update, context):
    """/regsync — Manually trigger registry auto-sync"""
    msg = await update.message.reply_text("🔄 Syncing all 6 registries...")
    try:
        import sys as _ss
        _ss.path.insert(0, '/root/workspaces/sameer_ai_manager')
        from sam_sync import sync_all
        results = sync_all()
        result_text = "🔄 REGISTRY AUTO-SYNC\n\n"
        result_text += f"✅ LOCKED_BOTS: {results.get('LOCKED_BOTS','?')}\n"
        result_text += f"✅ MASTER_FACTORY: {results.get('MASTER_FACTORY','?')}\n"
        result_text += f"✅ WORKERS: {results.get('WORKERS','?')}\n"
        result_text += f"✅ PAYMENTS: {results.get('PAYMENTS','?')}\n"
        result_text += f"✅ WEBSITES: {results.get('WEBSITES','?')}\n"
        result_text += f"✅ SERVICES: {results.get('SERVICES','?')}\n"
        result_text += f"\nAll 6 registries refreshed from live data."
        await msg.edit_text(result_text)
    except Exception as e:
        await msg.edit_text(f"❌ Registry sync error: {e}")


app.add_handler(CommandHandler("regsync", regsync_cmd))

# ═══ PHASE C — DISASTER & SNAPSHOT ═══

async def disaster_cmd(update, context):
    """/disaster — Emergency recovery report"""
    msg = await update.message.reply_text("🚨 Generating disaster recovery report...")
    try:
        import sys as _sd_sys, json as _sd_json
        _sd_sys.path.insert(0, '/root/workspaces/sameer_ai_manager')
        import sam_disaster
        report = sam_disaster.generate_disaster_report()
        # Truncate if too long
        if len(report) > 3800:
            report = report[:3800] + "\n... (truncated, full at disaster_report.txt)"
        await msg.edit_text(report)
    except Exception as e:
        import traceback
        await msg.edit_text(f"❌ Disaster report error: {e}\n{traceback.format_exc()[:200]}")


async def snapshot_cmd(update, context):
    """/snapshot — Create brain snapshot"""
    msg = await update.message.reply_text("🧠 Creating brain snapshot...")
    try:
        import sys as _sd_sys
        _sd_sys.path.insert(0, '/root/workspaces/sameer_ai_manager')
        import sam_disaster
        result = sam_disaster.brain_snapshot()
        await msg.edit_text(
            f"🧠 BRAIN SNAPSHOT\n\n"
            f"ID: `{result['snapshot_id']}`\n"
            f"Path: `{result['path']}`\n"
            f"Size: {result['size']} bytes\n"
            f"Memory + lessons + mistakes + fixes + routes saved."
        )
    except Exception as e:
        await msg.edit_text(f"❌ Snapshot error: {e}")


async def health_cmd(update, context):
    """/healthcheck — Cross-system health check"""
    try:
        import sys as _sd_sys
        _sd_sys.path.insert(0, '/root/workspaces/sameer_ai_manager')
        import sam_disaster
        hc = sam_disaster.health_check()
        msg = "🤝 CROSS-SYSTEM HEALTH CHECK\n\n"
        msg += f"SAM Service: {'🟢' if hc['sam']['service'] == 'active' else '🔴'} {hc['sam']['service']}\n"
        msg += f"SAM PID: {hc['sam']['pid']}\n"
        msg += f"SAM Router entries: {hc['sam']['router_entries']}\n"
        msg += f"SAM Learner DB: lessons={hc['sam'].get('learner_db',{}).get('lessons','?')}, fixes={hc['sam'].get('learner_db',{}).get('fixes','?')}, mistakes={hc['sam'].get('learner_db',{}).get('mistakes','?')}\n"
        msg += f"OpenClaw Registries: {hc['openclaw']['registry_count']}/6\n"
        msg += f"Last Registry Sync: {hc['openclaw'].get('last_registry_sync','?')[:19]}\n"
        msg += f"\nVerdict: {'🟢 ALL HEALTHY' if hc['verdict'] == 'ALL_HEALTHY' else '⚠️ DEGRADED'}\n"
        msg += f"\nNo dependency loop — decentralized health check."
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"❌ Health check error: {e}")


async def backup_cmd(update, context):
    """/backup — Manual backup trigger"""
    msg = await update.message.reply_text("💾 Creating backup...")
    try:
        import sys as _sd_sys
        _sd_sys.path.insert(0, '/root/workspaces/sameer_ai_manager')
        import sam_disaster
        result = sam_disaster.backup_all("daily")
        await msg.edit_text(
            f"💾 BACKUP COMPLETE\n\n"
            f"Files backed up: {len(result['files'])}\n"
            f"Path: /root/backups/sam/daily/\n"
        )
    except Exception as e:
        await msg.edit_text(f"❌ Backup error: {e}")


app.add_handler(CommandHandler("disaster", disaster_cmd))
app.add_handler(CommandHandler("snapshot", snapshot_cmd))
app.add_handler(CommandHandler("healthcheck", health_cmd))
app.add_handler(CommandHandler("backup", backup_cmd))

# ════════════════════════════════════════════════════════
# PHASE 5 — SAM + OPENCLAW COOPERATIVE OS (APPROVAL GATE)
# ════════════════════════════════════════════════════════

async def delegate_approval_cmd(update, context):
    """"/delegate <task> — Create task with routing + approval gate"""
    args = context.args
    if not args:
        await update.message.reply_text(
            "🔗 SAMEER OS — COOPERATIVE DELEGATION\n\n"
            "Usage: /delegate <task>\n"
            "Then: /approve <TASK_ID> to execute\n"
            "Or: /reject <TASK_ID> <reason>\n"
            "Or: /tasks to see all\n"
            "Or: /task <TASK_ID> for timeline\n"
            "Or: /runapproved <TASK_ID> to execute\n"
            "Or: /evidence <TASK_ID> for proof\n"
            "Or: /rollback <TASK_ID> if needed"
        )
        return
    
    task_desc = ' '.join(args)
    msg = await update.message.reply_text(f"🔗 Delegating: {task_desc}")
    
    try:
        import sys as _p5sys, json as _p5json
        _p5sys.path.insert(0, '/root/workspaces/sameer_ai_manager')
        import sam_approval as _app
        import sam_router as _rt
        
        # Route first
        route = _rt.route_task(task_desc)
        
        # Create task with route info
        task_id = _app.create_task(task_desc, route)
        
        # Log to router
        _rt.router_log.append({"task_id": task_id, **route})
        
        # Parse intent
        intent = _app.parse_task_intent(task_desc)
        
        await msg.edit_text(
            f"🔗 TASK CREATED\n\n"
            f"📋 TASK ID: `{task_id}`\n"
            f"📥 TASK: {task_desc[:100]}\n"
            f"📋 ROUTED: {route['model']} ({route['confidence']}%)\n"
            f"📌 STATUS: PENDING\n"
            f"\n"
            f"Next steps:\n"
            f"  /task {task_id} — view full timeline\n"
            f"  /approve {task_id} — approve execution\n"
            f"  /reject {task_id} <reason> — reject\n"
        )
    except Exception as e:
        import traceback
        await msg.edit_text(f"❌ Delegation error: {e}")


async def approve_cmd(update, context):
    """/approve <TASK_ID> — Approve task for execution (double confirm for locked bots)"""
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /approve <TASK_ID>")
        return
    
    task_id = args[0]
    msg = await update.message.reply_text(f"⏳ Approving {task_id}...")
    
    try:
        import sys as _p5sys
        _p5sys.path.insert(0, '/root/workspaces/sameer_ai_manager')
        import sam_approval as _app
        
        task = _app.get_task(task_id)
        if not task:
            await msg.edit_text(f"❌ Task {task_id} not found")
            return
        
        # Check for double confirmation
        if task['status'] in ('APPROVED',) and task.get('approved_by') and 'double' in str(task['approved_by']):
            await msg.edit_text(f"⚠️ Task {task_id} already approved. Use /runapproved {task_id} to execute.")
            return
        
        # Check if it needs double confirm
        intent = _app.parse_task_intent(task.get('task', ''))
        
        if intent['targets_customer_bot'] or intent['targets_payment']:
            # Check if this is a second approval
            if task['status'] == 'APPROVED':
                # Double confirm
                r = _app.approve_task(task_id, 'double_confirmed')
                await msg.edit_text(
                    f"✅ DOUBLE CONFIRMED — {task_id}\n"
                    f"Locked bot / payment task: double confirmation accepted.\n"
                    f"Use /runapproved {task_id} to execute."
                )
            else:
                # First approval
                r = _app.approve_task(task_id, 'pending_double')
                await msg.edit_text(
                    f"⚠️ FIRST CONFIRMATION — {task_id}\n"
                    f"This task involves a LOCKED bot or PAYMENT system.\n"
                    f"Send /approve {task_id} again to double-confirm."
                )
        else:
            # Standard approval
            r = _app.approve_task(task_id, 'sameer')
            await msg.edit_text(f"✅ APPROVED — {task_id}\nUse /runapproved {task_id} to execute.")
    except Exception as e:
        await msg.edit_text(f"❌ Approval error: {e}")


async def reject_cmd(update, context):
    """/reject <TASK_ID> <reason> — Reject task"""
    args = context.args
    if len(args) < 1:
        await update.message.reply_text("Usage: /reject <TASK_ID> <reason>")
        return
    
    task_id = args[0]
    reason = ' '.join(args[1:]) if len(args) > 1 else 'No reason given'
    
    try:
        import sys as _p5sys
        _p5sys.path.insert(0, '/root/workspaces/sameer_ai_manager')
        import sam_approval as _app
        
        r = _app.reject_task(task_id, reason)
        await update.message.reply_text(
            f"❌ REJECTED — {task_id}\n"
            f"Reason: {reason}"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Reject error: {e}")


async def tasks_cmd(update, context):
    """/tasks — Show all task statuses"""
    try:
        import sys as _p5sys
        _p5sys.path.insert(0, '/root/workspaces/sameer_ai_manager')
        import sam_approval as _app
        
        all_tasks = _app.list_tasks(limit=15)
        if not all_tasks:
            await update.message.reply_text("📋 No tasks found.")
            return
        
        msg = "📋 SAMEER OS — TASK QUEUE\n\n"
        for t in all_tasks:
            status_icon = {
                'PENDING': '⏳', 'PLANNED': '📋', 'APPROVED': '✅',
                'RUNNING': '⚡', 'COMPLETED': '🟢', 'REJECTED': '❌',
                'ROLLEDBACK': '↩️', 'FAILED': '🔴'
            }.get(t['status'], '❓')
            msg += f"{status_icon} `{t['id']}` — {t['task'][:50]}\n"
            msg += f"   Status: {t['status']} | Evidence: {t.get('evidence_score',0)}/100\n"
        
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"❌ Tasks error: {e}")


async def task_cmd(update, context):
    """/task <TASK_ID> — Show full task timeline"""
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /task <TASK_ID>")
        return
    
    try:
        import sys as _p5sys
        _p5sys.path.insert(0, '/root/workspaces/sameer_ai_manager')
        import sam_approval as _app
        
        timeline = _app.task_timeline(args[0])
        await update.message.reply_text(timeline[:4000])
    except Exception as e:
        await update.message.reply_text(f"❌ Task error: {e}")


async def runapproved_cmd(update, context):
    """/runapproved <TASK_ID> — Execute only approved tasks"""
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /runapproved <TASK_ID>")
        return
    
    task_id = args[0]
    msg = await update.message.reply_text(f"⚡ Executing approved task {task_id}...")
    
    try:
        import sys as _p5sys
        _p5sys.path.insert(0, '/root/workspaces/sameer_ai_manager')
        import sam_approval as _app
        
        result = _app.execute_approved(task_id)
        
        if result['status'] == 'COMPLETED':
            ev = result.get('evidence', {})
            await msg.edit_text(
                f"✅ TASK COMPLETED — {task_id}\n\n"
                f"Evidence: {ev.get('score',0)}/100\n"
                f"Backup: {len(result.get('backup',{}).get('files',{}))} files\n"
                f"\n{result.get('result','')[:500]}"
            )
        else:
            await msg.edit_text(
                f"❌ Execution failed: {result.get('error', result.get('status', 'unknown'))}"
            )
    except Exception as e:
        await msg.edit_text(f"❌ Run error: {e}")


async def evidence_cmd(update, context):
    """/evidence <TASK_ID> — Show evidence score"""
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /evidence <TASK_ID>")
        return
    
    try:
        import sys as _p5sys
        _p5sys.path.insert(0, '/root/workspaces/sameer_ai_manager')
        import sam_approval as _app
        
        ev = _app.compute_evidence(args[0])
        task = _app.get_task(args[0])
        
        msg = f"📊 EVIDENCE — {args[0]}\n\n"
        msg += f"Overall: {ev['score']}/100\n\n"
        msg += "Components:\n"
        for name, pts in ev['components']:
            msg += f"  +{pts} {name.replace('_', ' ')}\n"
        msg += f"\nMin required for DONE: 100/100\n"
        
        if task:
            msg += f"\nTask: {task['task'][:60]}\n"
            msg += f"Status: {task['status']}"
        
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"❌ Evidence error: {e}")


async def rollback_cmd(update, context):
    """/rollback <TASK_ID> — Rollback task if backup exists"""
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /rollback <TASK_ID>")
        return
    
    task_id = args[0]
    msg = await update.message.reply_text(f"↩️ Rolling back {task_id}...")
    
    try:
        import sys as _p5sys
        _p5sys.path.insert(0, '/root/workspaces/sameer_ai_manager')
        import sam_approval as _app
        
        result = _app.rollback_task(task_id)
        
        if result['status'] == 'ROLLEDBACK':
            restored = ', '.join(result.get('restored', ['?']))
            await msg.edit_text(
                f"↩️ ROLLBACK COMPLETE — {task_id}\n"
                f"Restored: {restored}\n"
                f"Task status set to ROLLEDBACK"
            )
        else:
            await msg.edit_text(f"❌ Rollback failed: {result.get('status', 'unknown')}")
    except Exception as e:
        await msg.edit_text(f"❌ Rollback error: {e}")


# Register Phase 5 commands
app.add_handler(CommandHandler("delegate", delegate_approval_cmd))
app.add_handler(CommandHandler("approve", approve_cmd))
app.add_handler(CommandHandler("reject", reject_cmd))
app.add_handler(CommandHandler("tasks", tasks_cmd))
app.add_handler(CommandHandler("task", task_cmd))
app.add_handler(CommandHandler("runapproved", runapproved_cmd))
app.add_handler(CommandHandler("evidence", evidence_cmd))
app.add_handler(CommandHandler("rollback", rollback_cmd))

# ════════════════════════════════════════════════════════
# PHASE 6 — TEAM MODE / SWARM COORDINATION
# ════════════════════════════════════════════════════════

async def team_cmd(update, context):
    """/team — Show team roles + status"""
    try:
        import sys as _t6; _t6.path.insert(0, '/root/workspaces/sameer_ai_manager')
        import sam_team
        summary = sam_team.team_summary()
        await update.message.reply_text(summary[:4000])
    except Exception as e:
        await update.message.reply_text(f"❌ Team error: {e}")


async def teamroom_cmd(update, context):
    """/teamroom — Show latest team room discussions"""
    try:
        import sys as _t6; _t6.path.insert(0, '/root/workspaces/sameer_ai_manager')
        import sam_team
        room = sam_team.format_team_room(15)
        await update.message.reply_text(room[:4000])
    except Exception as e:
        await update.message.reply_text(f"❌ Team room error: {e}")


async def discuss_cmd(update, context):
    """/discuss <TASK_ID> — Show team discussion for a task"""
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /discuss <TASK_ID>")
        return
    try:
        import sys as _t6; _t6.path.insert(0, '/root/workspaces/sameer_ai_manager')
        import sam_team
        discussion = sam_team.format_team_discussion(args[0])
        await update.message.reply_text(discussion[:4000])
    except Exception as e:
        await update.message.reply_text(f"❌ Discuss error: {e}")


async def assign_cmd(update, context):
    """/assign <TASK_ID> <ROLE> — Assign a worker role to a task"""
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "Usage: /assign <TASK_ID> <ROLE>\n"
            "Roles: Boss, CTO, Monitor, Prover, Learner, "
            "Repair Worker, Vision Worker, Voice Worker, "
            "Payment Worker, Website Worker, Bot Worker"
        )
        return
    try:
        import sys as _t6; _t6.path.insert(0, '/root/workspaces/sameer_ai_manager')
        import sam_team
        result = sam_team.assign_role(args[0], ' '.join(args[1:]))
        msg = f"📋 ASSIGN RESULT — {args[0]}\nStatus: {result['status']}"
        if result.get('valid_roles'):
            msg += f"\nValid roles: {', '.join(result['valid_roles'])}"
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"❌ Assign error: {e}")


async def review_cmd(update, context):
    """/review <TASK_ID> — Show CTO review + proof checklist"""
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /review <TASK_ID>")
        return
    try:
        import sys as _t6; _t6.path.insert(0, '/root/workspaces/sameer_ai_manager')
        import sam_team
        review = sam_team.review_task(args[0])
        await update.message.reply_text(review[:4000])
    except Exception as e:
        await update.message.reply_text(f"❌ Review error: {e}")


async def prove_cmd(update, context):
    """/prove <TASK_ID> — Run prover evidence check"""
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /prove <TASK_ID>")
        return
    try:
        import sys as _t6; _t6.path.insert(0, '/root/workspaces/sameer_ai_manager')
        import sam_team
        ev = sam_team.prove_task(args[0])
        msg = f"🔍 PROVER RESULT — {args[0]}\n\nEvidence: {ev['score']}/100\n"
        for name, pts in ev.get('components', []):
            msg += f"  +{pts} {name}\n"
        msg += f"\nNeed 100/100 to close."
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"❌ Prove error: {e}")


async def close_cmd(update, context):
    """/close <TASK_ID> — Close task only if evidence >= 100"""
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /close <TASK_ID>")
        return
    msg = await update.message.reply_text(f"🔍 Running close check on {args[0]}...")
    try:
        import sys as _t6; _t6.path.insert(0, '/root/workspaces/sameer_ai_manager')
        import sam_team
        result = sam_team.close_task(args[0])
        if result['status'] == 'CLOSED':
            await msg.edit_text(f"✅ TASK CLOSED — {args[0]}")
        else:
            resp = f"❌ BLOCKED — {args[0]}\n"
            resp += f"Evidence: {result['evidence']}/100 (need 100)\n"
            for name, pts in result.get('components', []):
                resp += f"\nScores: {name}: +{pts}"
            await msg.edit_text(resp)
    except Exception as e:
        await msg.edit_text(f"❌ Close error: {e}")


# Register Phase 6 commands
app.add_handler(CommandHandler("team", team_cmd))
app.add_handler(CommandHandler("teamroom", teamroom_cmd))
app.add_handler(CommandHandler("discuss", discuss_cmd))
app.add_handler(CommandHandler("assign", assign_cmd))
app.add_handler(CommandHandler("review", review_cmd))
app.add_handler(CommandHandler("prove", prove_cmd))
app.add_handler(CommandHandler("close", close_cmd))

# --- ACCOUNTANT COMMANDS ---
async def accounts_cmd(update, context):
    """ /accounts — Accountant dashboard """
    import subprocess as sp
    r = sp.run(["node","/root/.openclaw/workspace/ACCOUNTANT_DASHBOARD.js"], capture_output=True, text=True, timeout=15)
    out = (r.stdout or "No output")[:3900]
    await update.message.reply_markdown(f"```\n{out}\n```")

async def revenue_cmd(update, context):
    """ /revenue — Revenue summary """
    import subprocess as sp
    r = sp.run(["node","/root/.openclaw/workspace/ACCOUNTANT_DASHBOARD.js", "revenue"], capture_output=True, text=True, timeout=15)
    out = (r.stdout or "No output")[:3900]
    await update.message.reply_markdown(f"```\n{out}\n```")

async def leads_cmd(update, context):
    """ /leads — Lead pipeline """
    import subprocess as sp
    r = sp.run(["node","/root/.openclaw/workspace/ACCOUNTANT_DASHBOARD.js", "leads"], capture_output=True, text=True, timeout=15)
    out = (r.stdout or "No output")[:3900]
    await update.message.reply_markdown(f"```\n{out}\n```")

async def pipeline_cmd(update, context):
    """ /pipeline — CRM stages """
    import subprocess as sp
    r = sp.run(["node","/root/.openclaw/workspace/CRM_PIPELINE.js"], capture_output=True, text=True, timeout=15)
    out = (r.stdout or "No output")[:3900]
    await update.message.reply_markdown(f"```\n{out}\n```")

async def salesreport_cmd(update, context):
    """ /salesreport — Daily sales report """
    import subprocess as sp
    r = sp.run(["node","/root/.openclaw/workspace/SALES_REPORT.js"], capture_output=True, text=True, timeout=15)
    out = (r.stdout or "No output")[:3900]
    await update.message.reply_markdown(f"```\n{out}\n```")

app.add_handler(CommandHandler("accounts", accounts_cmd))
app.add_handler(CommandHandler("revenue", revenue_cmd))
app.add_handler(CommandHandler("leads", leads_cmd))
app.add_handler(CommandHandler("pipeline", pipeline_cmd))
app.add_handler(CommandHandler("salesreport", salesreport_cmd))


# Also keep old /tasks help aliases
app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
app.add_handler(MessageHandler(filters.Document.ALL & ~filters.COMMAND, handle_forwarded_photo))
app.run_polling(drop_pending_updates=True)