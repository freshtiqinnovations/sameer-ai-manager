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
import subprocess, datetime, os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv("/root/sameer_ai_manager/.env")

# Ollama first (free, no API key required)
ollama_client = OpenAI(
    api_key="ollama",
    base_url="http://127.0.0.1:11434/v1",
)
OLLAMA_MODEL = "qwen2.5:3b"

# DeepSeek fallback
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY", "")

def ask_ollama(messages):
    try:
        r = ollama_client.chat.completions.create(
            model=OLLAMA_MODEL,
            messages=messages,
            max_tokens=512,
            temperature=0.3
        )
        return r.choices[0].message.content
    except:
        return None

def ask_deepseek(messages):
    if not DEEPSEEK_KEY:
        return None
    try:
        ds = OpenAI(
            api_key=DEEPSEEK_KEY,
            base_url="https://api.deepseek.com/v1",
        )
        r = ds.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            max_tokens=512,
            temperature=0.3
        )
        return r.choices[0].message.content
    except:
        return None

def sh(cmd):
    return subprocess.getoutput(cmd)

def health_report():
    return sh("""
echo "📊 DISK:"
df -h /
echo ""
echo "🤖 SERVICES:"
systemctl is-active sameer_ai_manager.service
systemctl is-active sameer_ai_worker_auto.service
systemctl is-active freshtiq_ai_travel_pro.service
echo ""
echo "🧹 AUTOPILOT:"
tail -n 8 /root/sameer_ai_manager/ai_brain/autopilot.log 2>/dev/null
""")

def ask_brain(text):
    if any(x in text.lower() for x in ["health", "server", "disk", "status"]):
        return "✅ Server health check kiya:\n\n" + health_report()

    system_msg = {"role":"system","content":'You are Sameer AI Manager - OpenClaw Operator style autonomous AI CTO assistant.\n\nPERSONALITY:\n- Hinglish natural replies ("Samajh raha hu...", "Root cause found", "Proof complete")\n- Short, practical, no fake praise\n- When user says "karwao": continue only pending work, dont repeat done tasks\n- Before reporting PASS: verify with evidence (file size, git diff, HTTP codes, screenshots)\n- Ek baar clarify karo, then act\n\nEXPLAIN: what you understood, what you suggest, next safe action.'}
    user_msg = {"role":"user","content":text}
    messages = [system_msg, user_msg]

    # Try Ollama first (free)
    response = ask_ollama(messages)
    if response:
        return response

    # Fallback to DeepSeek
    response = ask_deepseek(messages)
    if response:
        return response

    return "❌ Ollama aur DeepSeek dono fail ho gaye. Please baad mein try karo."
