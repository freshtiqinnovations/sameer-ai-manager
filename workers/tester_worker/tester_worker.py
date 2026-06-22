
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
import json,os,subprocess,sys

def sh(c):
    return subprocess.getoutput(c).strip()

def test(file_path,service):
    r={}
    r["file_exists"]=os.path.exists(file_path)
    r["compile_ok"]="error" not in sh(f"python3 -m py_compile {file_path} 2>&1").lower()
    r["service_active"]=sh(f"systemctl is-active {service}")=="active"
    r["status"]="PASS" if all(r.values()) else "FAIL"
    return r

if len(sys.argv)>2:
    print(json.dumps(test(sys.argv[1],sys.argv[2]),indent=2))
