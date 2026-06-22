
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
def build_worker_dashboard_patch():
    return """async def wdashboard(update, context):\n    import os, subprocess\n    q=len([x for x in os.listdir(\"/root/sameer_ai_manager/ai_worker/queue\") if x.endswith(\".json\")])\n    c=len([x for x in os.listdir(\"/root/sameer_ai_manager/ai_worker/completed\") if x.endswith(\".json\")])\n    f=len([x for x in os.listdir(\"/root/sameer_ai_manager/ai_worker/failed\") if x.endswith(\".json\")])\n    st=subprocess.getoutput(\"systemctl is-active sameer_ai_worker_auto.service\")\n    msg=f\"WORKER DASHBOARD\\n\\nWorker: {st}\\nQueue: {q}\\nCompleted: {c}\\nFailed: {f}\"\n    await update.message.reply_text(msg)\n\napp.add_handler(CommandHandler(\"wdashboard\", wdashboard))"""