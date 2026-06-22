
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
import json,sys,subprocess
NOTIFY='/root/sameer_ai_manager/workers/ceo_manager_worker/ceo_notify.py'
PY='/root/sameer_ai_manager/venv/bin/python'

def main(report):
    d=json.load(open(report))
    status=d.get('final_status','unknown')
    icon='🚀' if status=='deployed' else '⚠️'
    msg=f"{icon} DEPLOY REPORT\\n\\nBot: {d.get('bot')}\\nTask: {d.get('task')}\\nStatus: {status}"
    subprocess.getoutput(f"{PY} {NOTIFY} {repr(msg)}")
    print('CEO_REPORT_NOTIFY_SENT')

if len(sys.argv)>1:
    main(sys.argv[1])
