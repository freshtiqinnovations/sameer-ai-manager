
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
import os
import logging
import subprocess
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from telegram import Update, BotCommand, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from builder_engine import create_customer_bot
from assistant_engine import handle_agent_prompt
from modules.safe_runner import run_shell
import safe_editor
from modules.ai_fix_engine import run_ai_fix
from modules.ai_repair import ai_repair
from template_deploy_cmds import deploy_template_cmd

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_ID = os.getenv("ADMIN_ID")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
ALLOWED_USER_IDS = os.getenv("ALLOWED_USER_IDS", "").split(",")
client = OpenAI(api_key=OPENAI_API_KEY)

logging.basicConfig(level=logging.INFO)
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

async def repair_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            ["👑 Master", "🤖 Bots"],
            ["🩺 Doctor", "🔧 Repair"],
            ["📊 Status", "🧠 Brain"],
            ["⚡ Do", "💾 Backup"],
            ["📜 Logs", "🚀 Version"],
        ],
        resize_keyboard=True
    )


async def panel_button_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = (update.message.text or "").strip()

    if txt == "👑 Master":
        return await master_cmd(update, context)

    if txt == "🤖 Bots":
        context.args = []
        return await bots_cmd(update, context)

    if txt == "🩺 Doctor":
        context.args = ["sameer_ai_manager"]
        return await doctor_cmd(update, context)

    if txt == "🔧 Repair":
        return await repair_cmd(update, context)

    if txt == "📊 Status":
        return await status(update, context)

    if txt == "🧠 Brain":
        return await update.message.reply_text("Use: /brain your idea")

    if txt == "⚡ Do":
        return await update.message.reply_text("Use: /do your task")

    if txt == "💾 Backup":
        return await backup_cmd(update, context)

    if txt == "📜 Logs":
        context.args = ["logs", "sameer_ai_manager"]
        return await bots_cmd(update, context)

    if txt == "🚀 Version":
        return await version_cmd(update, context)

async def panel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👑 Sameer AI Manager Control Panel\nSelect button:",
        reply_markup=main_keyboard()
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Sameer AI Manager Ready 🚀\n\n"
        "Main aapka digital assistant manager hoon.\n\n"
        "Commands:\n"
        "/idea - idea ko plan me convert karo\n"
        "/ok - pending plan approve karo\n"
        "/status - system status\n"
        "/help - help menu\n\n"
        "Example:\n"
        "/idea Travel agency ke liye fare alert bot banao"
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

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Sameer AI Manager online hai.\n"
        f"Model: {MODEL}\n"
        "Mode: Approval-based safe manager"
    )

async def idea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) not in ALLOWED_USER_IDS:
        return await update.message.reply_text("❌ Access denied.")
    idea_text = " ".join(context.args).strip()
    if not idea_text:
        return await update.message.reply_text("Example:\n/idea el salama radiator factory ke liye customer support bot banao")

    await update.message.reply_text("🧠 Idea analyze kar raha hoon...")

    response = client.chat.completions.create(
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


async def customer_document_cmd(update, context):
    try:
        import re, json
        from pathlib import Path
        from datetime import datetime
        from pypdf import PdfReader

        msg = update.message
        caption = (msg.caption or msg.text or "").strip()
        cap_src_match = re.search(r"SRC\d+", caption.upper())
        caption_src = cap_src_match.group(0) if cap_src_match else None

        file_obj = None
        filename = None
        is_pdf = False

    if msg.document:
        file_obj = msg.document
        filename = file_obj.file_name or "document"

        name_src_match = re.search(r"SRC\d+", filename.upper())
        filename_src = name_src_match.group(0) if name_src_match else None

        is_pdf = filename.lower().endswith(".pdf")
        elif msg.photo:
            file_obj = msg.photo[-1]
            filename = "photo_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".jpg"
        else:
            return

        temp_dir = Path("/root/customer_memory/uploads")
        temp_dir.mkdir(parents=True, exist_ok=True)
        temp_path = temp_dir / (datetime.now().strftime("%Y%m%d_%H%M%S_") + filename)

        tg_file = await context.bot.get_file(file_obj.file_id)
        await tg_file.download_to_drive(str(temp_path))

        extracted_text = ""
        file_src = None
        invoice_total = None
        invoice_no = None
        customer_name = None
        due_date = None

        if is_pdf:
            try:
                reader = PdfReader(str(temp_path))
                for page in reader.pages:
                    extracted_text += "\\n" + (page.extract_text() or "")
            except Exception as e:
                extracted_text = ""

            m = re.search(r"SRC\d+", extracted_text.upper())
            if m:
                file_src = m.group(0)

            m = re.search(r"(?:Amount Total Invoice|Invoice Total Amount|إجمالي مبلغ الفاتورة).*?(\\d+[.,]\\d{2})", extracted_text, re.I | re.S)
            if m:
                invoice_total = m.group(1).replace(",", ".")

            m = re.search(r"(CINV[-A-Z0-9]+)", extracted_text.upper())
            if m:
                invoice_no = m.group(1)

            m = re.search(r"Customer name\\s+([A-Z0-9 .&-]+)", extracted_text, re.I)
            if m:
                customer_name = m.group(1).strip()

            m = re.search(r"Payment due\\s+(\\d{2}/\\d{2}/\\d{4})", extracted_text, re.I)
            if m:
                due_date = m.group(1)

        final_src = file_src or caption_src

        if caption_src and file_src and caption_src != file_src:
            return await msg.reply_text(
                f"⚠️ SRC mismatch!\\n\\nCaption: {caption_src}\\nFile/Fatoora: {file_src}\\n\\nGalat customer me save nahi kiya."
            )

        if not final_src:
            return await msg.reply_text("❌ SRC nahi mila. Caption me bas SRC likho, example: SRC001261")

        base = Path(f"/root/customer_memory/customers/{final_src}")
        for folder in ["invoices", "receipts", "sanad", "photos", "pdf", "excel", "other"]:
            (base / folder).mkdir(parents=True, exist_ok=True)

        folder = "other"
        low = filename.lower()
        if is_pdf:
            folder = "invoices" if ("cinv" in extracted_text.lower() or "invoice" in extracted_text.lower() or "فاتورة" in extracted_text) else "pdf"
        elif low.endswith((".xlsx", ".xls")):
            folder = "excel"
        elif msg.photo:
            folder = "photos"

        final_path = base / folder / temp_path.name
        temp_path.rename(final_path)

        ledger_file = base / "ledger.json"
        try:
            ledger = json.loads(ledger_file.read_text())
        except:
            ledger = []

        entry = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "src": final_src,
            "caption_src": caption_src,
            "file_src": file_src,
            "type": "invoice" if folder == "invoices" else folder,
            "file": str(final_path),
            "original_name": filename,
            "invoice_no": invoice_no,
            "customer_name": customer_name,
            "invoice_total": invoice_total,
            "due_date": due_date,
            "caption": caption
        }

        ledger.append(entry)
        ledger_file.write_text(json.dumps(ledger, indent=2, ensure_ascii=False))

        reply = f"✅ Saved successfully\\n👤 SRC: {final_src}\\n📁 Type: {entry['type']}\\n📄 File: {filename}"
        if invoice_total:
            reply += f"\\n💰 Invoice Total: {invoice_total} SAR"
        if invoice_no:
            reply += f"\\n🧾 Invoice: {invoice_no}"
        if due_date:
            reply += f"\\n📅 Due: {due_date}"

        await msg.reply_text(reply)

    except Exception as e:
        await update.message.reply_text(f"❌ Save error:\\n{e}")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("❌ Access denied.")

    user_msg = update.message.text

    await update.message.reply_text("💭 Soch raha hoon...")

    try:
        response = client.chat.completions.create(
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
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)

        response = client.chat.completions.create(
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
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)

        response = client.chat.completions.create(
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
            "Use:\n/service service_name working_dir bot_file\n\nExample:\n/service freshtiq_travel_bot /root/workspaces/customers/freshtiq_travel_agency_automation bot.py"
        )

    name = args[0].replace(".service", "")
    workdir = args[1]
    botfile = args[2]

    service_path = f"/etc/systemd/system/{name}.service"

    cmd = f"""
cat > {service_path} <<'EOF'
[Unit]
Description={name}
After=network.target

[Service]
WorkingDirectory={workdir}
ExecStart=/root/sameer_ai_manager/venv/bin/python {workdir}/{botfile}
Restart=always
RestartSec=5
User=root

[Install]
WantedBy=multi-user.target
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
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        r = client.chat.completions.create(
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
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        r = client.chat.completions.create(
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
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        r = client.chat.completions.create(
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

    cmd = " ".join(context.args).strip()
    if not cmd:
        return await update.message.reply_text("Example:\n/auto el salama radiator factory ke liye customer support bot banao")

    await update.message.reply_text("⚙️ Command run kar raha hoon...")

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        output = (result.stdout + "\n" + result.stderr).strip()
        if not output:
            output = "✅ Command complete. No output."
        await send_long(update, output[:12000])
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

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
        return await update.message.reply_text("Example:\n/auto el salama radiator factory ke liye customer support bot banao")

    try:
        lower_text = prompt.lower()
        upgrade_keywords = ["upgrade", "feature add", "feature add karo", "khud ko upgrade", "khud ko aur upgrade", "new feature", "automation add"]

        if any(k in lower_text for k in upgrade_keywords):
            with open("/root/sameer_ai_manager/ai_patch_request.txt", "a", encoding="utf-8") as f:
                f.write(prompt + "\n")
            await update.message.reply_text("✅ Request save ho gayi.\n/approve_patch bhejo.")

        reply = handle_agent_prompt(prompt)
        return await update.message.reply_text("🤖 AUTO DONE\n\n" + reply)

    except Exception as e:
        return await update.message.reply_text(f"❌ Auto failed: {e}")

async def agent_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) not in ALLOWED_USER_IDS:
        return await update.message.reply_text("❌ Access denied.")

    prompt = " ".join(context.args).strip()
    if not prompt:
        return await update.message.reply_text("Example:\n/auto el salama radiator factory ke liye customer support bot banao")

    try:
        reply = handle_agent_prompt(prompt)
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text(f"❌ Agent error: {e}")

async def buildbot_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) not in ALLOWED_USER_IDS:
        return await update.message.reply_text("❌ Access denied.")

    if len(context.args) < 2:
        return await update.message.reply_text(
            "Usage:\n/buildbot type botname\nExample:\n/buildbot radiator sameer_radiator"
        )

    bot_type = context.args[0]
    bot_name = context.args[1]

    try:
        path = create_customer_bot(bot_type, bot_name)
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
            "Example:\n/autocode add whatsapp auto reply system"
        )

    await update.message.reply_text("🤖 AI coding plan bana raha hoon...")

    try:
        response = client.chat.completions.create(
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
async def health_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) not in ALLOWED_USER_IDS:
        return await update.message.reply_text("❌ Access denied.")

    cmd = "uptime && echo '---DISK---' && df -h / && echo '---MEMORY---' && free -h && echo '---SERVICE---' && systemctl is-active sameer_ai_manager"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    await send_long(update, "🩺 VPS HEALTH REPORT:\n\n" + result.stdout[-12000:])

async def deploy_customer_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("Access denied.")

    import re, os, subprocess
    from pathlib import Path

    if len(context.args) < 2:
        return await update.message.reply_text(
            "Use:\n/deploy_customer customer_name BOT_TOKEN"
        )

    customer_name = context.args[0]
    bot_token = context.args[1]

    slug = re.sub(r"[^a-zA-Z0-9_]+", "_", customer_name.lower()).strip("_")

    root = Path(f"/root/workspaces/customers/{slug}")
    root.mkdir(parents=True, exist_ok=True)

    (root / "logs").mkdir(exist_ok=True)
    (root / "backups").mkdir(exist_ok=True)

    bot_code = f'''
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = "{bot_token}"

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Customer bot running successfully."
    )

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))

app.run_polling(drop_pending_updates=True)
'''

    (root / "bot.py").write_text(bot_code, encoding="utf-8")

    req = '''
python-telegram-bot==21.6
'''

    (root / "requirements.txt").write_text(req, encoding="utf-8")

    service_name = f"{slug}.service"

    service_text = f'''
[Unit]
Description={customer_name} Bot
After=network.target

[Service]
WorkingDirectory={root}
ExecStart={root}/venv/bin/python {root}/bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
'''

    service_path = f"/etc/systemd/system/{service_name}"

    Path(service_path).write_text(service_text, encoding="utf-8")

    cmd = f"""
cd {root}
python3 -m venv venv
{root}/venv/bin/pip install -r requirements.txt
python3 -m py_compile bot.py
systemctl daemon-reload
systemctl enable {service_name}
systemctl restart {service_name}
"""

    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )

    out = (result.stdout + result.stderr)[-3000:]

    await update.message.reply_text(
        f"✅ CUSTOMER BOT DEPLOYED\n\n"
        f"Customer: {customer_name}\n"
        f"Service: {service_name}\n"
        f"Path: {root}\n\n"
        f"STATUS:\n{out}"
    )



def _safe_customer_service_name(raw: str) -> str:
    import re
    name = re.sub(r"[^a-zA-Z0-9_]+", "_", raw.lower()).strip("_")
    if not name:
        raise ValueError("Invalid bot name")
    return name

async def customer_status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("Access denied.")
    if not context.args:
        return await update.message.reply_text("Use: /customer_status botname")
    import subprocess
    service = _safe_customer_service_name(context.args[0]) + ".service"
    r = subprocess.run(f"systemctl status {service} --no-pager", shell=True, capture_output=True, text=True, timeout=30)
    await update.message.reply_text((r.stdout + r.stderr)[-3500:])

async def customer_logs_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("Access denied.")
    if not context.args:
        return await update.message.reply_text("Use: /customer_logs botname")
    import subprocess
    service = _safe_customer_service_name(context.args[0]) + ".service"
    r = subprocess.run(f"journalctl -u {service} -n 80 --no-pager", shell=True, capture_output=True, text=True, timeout=30)
    await update.message.reply_text((r.stdout + r.stderr)[-3500:])

async def customer_restart_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("Access denied.")
    if not context.args:
        return await update.message.reply_text("Use: /customer_restart botname")
    import subprocess
    service = _safe_customer_service_name(context.args[0]) + ".service"
    r = subprocess.run(f"systemctl restart {service} && systemctl status {service} --no-pager", shell=True, capture_output=True, text=True, timeout=40)
    await update.message.reply_text(("✅ Restart done\n\n" + r.stdout + r.stderr)[-3500:])

async def customer_start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("Access denied.")
    if not context.args:
        return await update.message.reply_text("Use: /customer_start botname")
    import subprocess
    service = _safe_customer_service_name(context.args[0]) + ".service"
    r = subprocess.run(f"systemctl start {service} && systemctl status {service} --no-pager", shell=True, capture_output=True, text=True, timeout=40)
    await update.message.reply_text(("✅ Start done\n\n" + r.stdout + r.stderr)[-3500:])

async def customer_stop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("Access denied.")
    if not context.args:
        return await update.message.reply_text("Use: /customer_stop botname")
    import subprocess
    service = _safe_customer_service_name(context.args[0]) + ".service"
    r = subprocess.run(f"systemctl stop {service} && systemctl status {service} --no-pager", shell=True, capture_output=True, text=True, timeout=40)
    await update.message.reply_text(("🛑 Stop done\n\n" + r.stdout + r.stderr)[-3500:])

async def customer_list_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("Access denied.")
    import subprocess
    cmd = "systemctl list-units --type=service --all | grep -E 'demo_|freshtiq|salama|customer|bot' || true"
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    await update.message.reply_text(("🤖 Customer/Bot Services:\n\n" + r.stdout + r.stderr)[-3500:])



async def customer_help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("Access denied.")
    await update.message.reply_text("""
🤖 CUSTOMER BOT CONTROL

/deploy_customer name token
/customer_list
/customer_status botname
/customer_logs botname
/customer_restart botname
/customer_start botname
/customer_stop botname
/customer_backup botname
/customer_compile botname
/customer_files botname
/customer_set_token botname token
/customer_delete botname CONFIRM

Example:
/deploy_customer shopbot 123456:ABC
/customer_logs shopbot
/customer_set_token shopbot 123456:NEW_TOKEN
""")

async def customer_files_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("Access denied.")
    if not context.args:
        return await update.message.reply_text("Use: /customer_files botname")
    import subprocess
    name = _safe_customer_service_name(context.args[0])
    root = f"/root/workspaces/customers/{name}"
    r = subprocess.run(f"ls -la {root}", shell=True, capture_output=True, text=True, timeout=20)
    await update.message.reply_text((r.stdout + r.stderr)[-3500:])

async def customer_compile_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("Access denied.")
    if not context.args:
        return await update.message.reply_text("Use: /customer_compile botname")
    import subprocess
    name = _safe_customer_service_name(context.args[0])
    root = f"/root/workspaces/customers/{name}"
    r = subprocess.run(f"python3 -m py_compile {root}/bot.py", shell=True, capture_output=True, text=True, timeout=30)
    out = (r.stdout + r.stderr).strip()
    if r.returncode == 0:
        out = "✅ Compile successful"
    await update.message.reply_text(out[-3500:])

async def customer_backup_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("Access denied.")
    if not context.args:
        return await update.message.reply_text("Use: /customer_backup botname")
    import subprocess, datetime
    name = _safe_customer_service_name(context.args[0])
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    root = f"/root/workspaces/customers/{name}"
    dest = f"{root}/backups/{name}_{ts}.tar.gz"
    cmd = f"mkdir -p {root}/backups && tar --exclude='{root}/venv' --exclude='{root}/backups' -czf {dest} {root}"
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
    out = (r.stdout + r.stderr).strip()
    if r.returncode == 0:
        out = f"✅ Backup created:\n{dest}"
    await update.message.reply_text(out[-3500:])

async def customer_set_token_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("Access denied.")
    if len(context.args) < 2:
        return await update.message.reply_text("Use: /customer_set_token botname token")
    import re, subprocess
    from pathlib import Path
    name = _safe_customer_service_name(context.args[0])
    token = context.args[1].strip()
    botfile = Path(f"/root/workspaces/customers/{name}/bot.py")
    if not botfile.exists():
        return await update.message.reply_text("❌ bot.py not found.")
    text = botfile.read_text()
    text = re.sub(r'BOT_TOKEN\s*=\s*["\'].*?["\']', f'BOT_TOKEN = "{token}"', text)
    botfile.write_text(text)
    service = name + ".service"
    cmd = f"python3 -m py_compile {botfile} && systemctl restart {service} && systemctl status {service} --no-pager"
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=40)
    await update.message.reply_text(("✅ Token updated/restarted\n\n" + r.stdout + r.stderr)[-3500:])

async def customer_delete_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("Access denied.")
    if len(context.args) < 2 or context.args[1] != "CONFIRM":
        return await update.message.reply_text("Use: /customer_delete botname CONFIRM")
    import subprocess
    name = _safe_customer_service_name(context.args[0])
    service = name + ".service"
    root = f"/root/workspaces/customers/{name}"
    cmd = f"systemctl stop {service} || true; systemctl disable {service} || true; rm -f /etc/systemd/system/{service}; systemctl daemon-reload; mv {root} {root}_deleted_$(date +%Y%m%d_%H%M%S)"
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
    await update.message.reply_text(("🗑 Delete/disable done\n\n" + r.stdout + r.stderr)[-3500:])


async def fix_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) not in ALLOWED_USER_IDS:
        return await update.message.reply_text("❌ Access denied.")

    note = " ".join(context.args).strip()
    await update.message.reply_text("🛠 Fix check running...")

    result = run_ai_fix(note)
    await update.message.reply_text(result[-3900:])


async def ai_fix_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("Access denied.")
    cmd = """
echo '=== SAMEER MANAGER ==='
systemctl is-active sameer_ai_manager
python3 -m py_compile /root/sameer_ai_manager/bot.py 2>&1
echo '=== SALAMA BOT ==='
systemctl is-active salama_radiator_bot
python3 -m py_compile /root/workspaces/customers/el_salama_radiator_factory/bot.py 2>&1
echo '=== LAST SALAMA LOGS ==='
journalctl -u salama_radiator_bot -n 20 --no-pager
"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=40)
    out = (result.stdout + result.stderr)[-3500:]
    await update.message.reply_text("AI FIX REPORT:\n\n" + out)


async def safe_replace_cmd(update, context):
    try:
        args = " ".join(context.args)
        x = args.split(";;", 3)

        if len(x) < 4:
            return await update.message.reply_text("FORMAT_ERROR")

        path, old, new, service = x
        ok, msg = safe_editor.safe_replace(path.strip(), old, new, service.strip())
        await update.message.reply_text(msg[:4000])
    except Exception as e:
        await update.message.reply_text(f"SAFE_REPLACE_ERROR: {e}")

async def safe_insert_cmd(update, context):
    try:
        args = " ".join(context.args)

        x = args.split(";;", 3)

        if len(x) < 4:
            return await update.message.reply_text("FORMAT_ERROR")

        path, marker, text, service = x

        ok, msg = safe_insert_before(
            path.strip(),
            marker,
            text,
            service.strip()
        )

        await update.message.reply_text(msg[:4000])

    except Exception as e:
        await update.message.reply_text(f"SAFE_INSERT_ERROR: {e}")


async def approve_patch_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("Access denied.")
    await update.message.reply_text("Approved. Applying safe patch...")
    result = subprocess.run(
        ["python3", "patch_tool.py"],
        cwd="/root/sameer_ai_manager",
        capture_output=True,
        text=True,
        timeout=60
    )
    out = (result.stdout + result.stderr).strip()
    if not out:
        out = "APPLY SUCCESS"
    await update.message.reply_text("APPROVE PATCH RESULT:\n\n" + out[-3500:])



# PATCH_QUEUE_FUNCTIONS_V1

async def patch_create_cmd(update, context):
    from pathlib import Path
    from datetime import datetime

    text = " ".join(context.args).strip()
    if not text:
        await update.message.reply_text("Usage: /patch_create your patch text")
        return

    base = Path("/root/sameer_ai_manager/upgrades/pending")
    base.mkdir(parents=True, exist_ok=True)

    name = datetime.now().strftime("%Y%m%d_%H%M%S") + "_telegram_patch.txt"
    path = base / name
    path.write_text(text)

    await update.message.reply_text(f"✅ Patch created:\n{name}")


async def patch_preview_cmd(update, context):
    from pathlib import Path

    if not context.args:
        await update.message.reply_text("Usage: /patch_preview filename")
        return

    name = context.args[0]
    base = Path("/root/sameer_ai_manager/upgrades")

    found = None
    for folder in ["pending", "approved", "applied", "rejected"]:
        p = base / folder / name
        if p.exists():
            found = p
            break

    if not found:
        await update.message.reply_text("❌ Patch not found")
        return

    content = found.read_text()[:3500]
    await update.message.reply_text(f"📄 Preview: {name}\n━━━━━━━━━━━━━━\n{content}")
async def patch_list_cmd(update, context):
    from pathlib import Path

    base = Path("/root/sameer_ai_manager/upgrades")

    text = "📦 PATCH QUEUE\n\n"

    for folder in ["pending", "approved", "applied", "rejected"]:
        items = sorted([x.name for x in (base / folder).glob("*")])

        text += f"=== {folder.upper()} ===\n"

        if items:
            text += "\n".join(items)
        else:
            text += "Empty"

        text += "\n\n"

    await update.message.reply_text(text[:4000])


async def patch_approve_cmd(update, context):
    from pathlib import Path
    import shutil

    if not context.args:
        await update.message.reply_text("Usage: /patch_approve filename")
        return

    name = context.args[0]

    base = Path("/root/sameer_ai_manager/upgrades")

    src = base / "pending" / name
    dst = base / "approved" / name

    if not src.exists():
        await update.message.reply_text("❌ Patch not found")
        return

    shutil.move(str(src), str(dst))

    await update.message.reply_text(f"✅ Approved: {name}")


async def patch_apply_cmd(update, context):

    if not context.args:
        await update.message.reply_text(
            "Usage: /patch_apply filename"
        )
        return

    from modules.patch_apply_engine import apply_patch

    name = context.args[0]

    await update.message.reply_text(
        f"⚙️ Applying patch: {name}"
    )

    result = apply_patch(name)

    await update.message.reply_text(
        f"RESULT: {result}"
    )


async def patch_reject_cmd(update, context):
    from pathlib import Path
    import shutil

    if not context.args:
        await update.message.reply_text("Usage: /patch_reject filename")
        return

    name = context.args[0]

    base = Path("/root/sameer_ai_manager/upgrades")

    src = base / "pending" / name
    dst = base / "rejected" / name

    if not src.exists():
        await update.message.reply_text("❌ Patch not found")
        return

    shutil.move(str(src), str(dst))

    await update.message.reply_text(f"🚫 Rejected: {name}")



def main():
    if not TELEGRAM_TOKEN:
        raise Exception("TELEGRAM_TOKEN missing in .env")
    if not OPENAI_API_KEY:
        raise Exception("OPENAI_API_KEY missing in .env")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("ping", ping_cmd))
    app.add_handler(CommandHandler("master", master_cmd))
    app.add_handler(CommandHandler("panel", panel_cmd))
    app.add_handler(CommandHandler("bots", bots_cmd))
    app.add_handler(CommandHandler("doctor", doctor_cmd))
    app.add_handler(CommandHandler("autofix", autofix_cmd))
    app.add_handler(CommandHandler("smartfix", smartfix_cmd))
    app.add_handler(CommandHandler("service", service_cmd))
    app.add_handler(CommandHandler("brain", brain_cmd))
    app.add_handler(CommandHandler("do", do_cmd))
    app.add_handler(CommandHandler("version", version_cmd))
    app.add_handler(CommandHandler("health", health_cmd))
    app.add_handler(CommandHandler("idea", idea))
    app.add_handler(CommandHandler("upgrade", upgrade_cmd))
    app.add_handler(CommandHandler("auto_upgrade", auto_upgrade))
    app.add_handler(CommandHandler("createbot", create_bot))
    app.add_handler(CommandHandler("run", run_cmd))
    app.add_handler(CommandHandler("restart", restart_bot))
    app.add_handler(CommandHandler("logs", logs_cmd))
    app.add_handler(CommandHandler("logs_live", logs_live_cmd))
    app.add_handler(CommandHandler("files", files_cmd))
    app.add_handler(CommandHandler("backup", backup_cmd))
    app.add_handler(CommandHandler("buildbot", buildbot_cmd))
    app.add_handler(CommandHandler("agent", agent_cmd))
    app.add_handler(CommandHandler("auto", auto_cmd))
    app.add_handler(CommandHandler("autocode", auto_code_cmd))
    app.add_handler(CommandHandler("apply_ai", apply_ai_cmd))
    app.add_handler(CommandHandler("rollback", rollback_cmd))
    app.add_handler(CommandHandler("salama_status", salama_status_cmd))
    app.add_handler(CommandHandler("salama_logs", salama_logs_cmd))
    app.add_handler(CommandHandler("salama_restart", salama_restart_cmd))
    app.add_handler(CommandHandler("salama_backup", salama_backup_cmd))
    app.add_handler(CommandHandler("salama_health", salama_health_cmd))
    app.add_handler(CommandHandler("repair", repair_cmd))
    app.add_handler(CommandHandler("patch_create", patch_create_cmd))
    app.add_handler(CommandHandler("patch_preview", patch_preview_cmd))
    app.add_handler(CommandHandler("patch_list", patch_list_cmd))
    app.add_handler(CommandHandler("patch_approve", patch_approve_cmd))
    app.add_handler(CommandHandler("patch_apply", patch_apply_cmd))
    app.add_handler(CommandHandler("patch_reject", patch_reject_cmd))
    app.add_handler(CommandHandler("deploy_customer", deploy_customer_cmd))

    app.add_handler(CommandHandler("customer_status", customer_status_cmd))
    app.add_handler(CommandHandler("customer_logs", customer_logs_cmd))
    app.add_handler(CommandHandler("customer_restart", customer_restart_cmd))
    app.add_handler(CommandHandler("customer_start", customer_start_cmd))
    app.add_handler(CommandHandler("customer_stop", customer_stop_cmd))
    app.add_handler(CommandHandler("customer_list", customer_list_cmd))

    app.add_handler(CommandHandler("customer_help", customer_help_cmd))
    app.add_handler(CommandHandler("customer_files", customer_files_cmd))
    app.add_handler(CommandHandler("customer_compile", customer_compile_cmd))
    app.add_handler(CommandHandler("customer_backup", customer_backup_cmd))
    app.add_handler(CommandHandler("customer_set_token", customer_set_token_cmd))
    app.add_handler(CommandHandler("customer_delete", customer_delete_cmd))
    app.add_handler(CommandHandler("deploy_template", deploy_template_cmd))


    app.add_handler(CommandHandler("ai_fix", ai_fix_cmd))
    app.add_handler(CommandHandler("fix", fix_cmd))
    app.add_handler(CommandHandler("approve_patch", approve_patch_cmd))

    app.add_handler(CommandHandler("safe_replace", safe_replace_cmd))
    app.add_handler(CommandHandler("safe_insert", safe_insert_cmd))


    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, customer_document_cmd))
    app.add_handler(MessageHandler(filters.Regex("^(👑 Master|🤖 Bots|🩺 Doctor|🔧 Repair|📊 Status|🧠 Brain|⚡ Do|💾 Backup|📜 Logs|🚀 Version)$"), panel_button_cmd))
    


    print("✅ Sameer AI Manager Bot running...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()


# AUTO_PATCH_APPEND

