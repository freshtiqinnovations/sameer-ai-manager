
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
import sys,subprocess,json
target=sys.argv[1] if len(sys.argv)>1 else ""
if not target: print("USE: worker_tester.py file.py"); raise SystemExit(1)
r={"file":target}
try:
 subprocess.check_call(["python3","-m","py_compile",target])
 r["compile"]="PASS"
except Exception as e:
 r["compile"]="FAIL"; r["error"]=str(e)
print(json.dumps(r,indent=2))
