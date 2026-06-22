
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
import subprocess

def sh(cmd):
    return subprocess.getoutput(cmd)

def autopilot_report():
    return sh("""
echo "🧠 SAMEER AI AUTOPILOT REPORT"
echo ""
echo "📊 DISK:"
df -h /
echo ""
echo "💾 RAM:"
free -h | head -2
echo ""
echo "🤖 SERVICES:"
for s in sameer_ai_manager.service sameer_ai_worker_auto.service sameer_ai_brain_loop.service freshtiq_ai_travel_pro.service restaurant_demo_bot.service salama_radiator_bot.service salama_service_bot.service autopilot_hub_bot.service; do
  echo "$s => $(systemctl is-active $s 2>/dev/null)"
done
echo ""
echo "🧹 LAST SYSTEM GUARD:"
tail -n 8 /root/monitoring/system_guard.log 2>/dev/null
echo ""
echo "🧠 LAST BRAIN LOOP:"
tail -n 8 /root/sameer_ai_manager/reports/brain_loop.log 2>/dev/null
""")
