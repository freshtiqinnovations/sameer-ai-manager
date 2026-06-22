from pathlib import Path

p = Path("/root/sameer_ai_manager/bot.py")
s = p.read_text(encoding="utf-8")

block = r'''
async def errors_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cmd = "journalctl -u sameer_ai_manager -u salama_radiator_bot -u freshtiq_travel_bot -u salama_service_bot -n 300 --no-pager | grep -iE 'error|exception|traceback|failed|timed out' | tail -80"
    out = run_shell(cmd)
    if not out.strip():
        out = "✅ No recent errors found."
    await send_long(update, "🚨 ERROR LOGS\n\n" + out)


async def server_health_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cmd = "echo '=== DISK ==='; df -h /; echo; echo '=== RAM ==='; free -h; echo; echo '=== SERVICES ==='; systemctl is-active sameer_ai_manager salama_radiator_bot freshtiq_travel_bot salama_service_bot; echo; echo '=== TIMERS ==='; systemctl list-timers --no-pager | grep sameer || true"
    out = run_shell(cmd)
    await send_long(update, "🖥 SERVER HEALTH\n\n" + out)


async def self_repair_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛠 Self repair started...")
    cmd = """
cd /root/sameer_ai_manager && python3 -m py_compile bot.py || exit 10
systemctl restart salama_radiator_bot || true
systemctl restart freshtiq_travel_bot || true
systemctl restart salama_service_bot || true
sleep 3
echo '=== STATUS ==='
systemctl is-active sameer_ai_manager salama_radiator_bot freshtiq_travel_bot salama_service_bot
"""
    out = run_shell(cmd)
    await send_long(update, "🛠 SELF REPAIR RESULT\n\n" + out)
'''

if "async def errors_cmd" not in s:
    marker = "def is_admin(user_id: int) -> bool:"
    s = s.replace(marker, block + "\n\n" + marker)

handlers = '''
app.add_handler(CommandHandler("errors", errors_cmd))
app.add_handler(CommandHandler("server_health", server_health_cmd))
app.add_handler(CommandHandler("self_repair", self_repair_cmd))
'''

if 'CommandHandler("server_health"' not in s:
    marker = 'app.add_handler(CommandHandler("backup_all", backup_all_cmd))'
    s = s.replace(marker, marker + "\n" + handlers)

p.write_text(s, encoding="utf-8")
