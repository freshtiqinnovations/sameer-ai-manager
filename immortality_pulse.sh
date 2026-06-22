#!/bin/bash
# ── IMMORTALITY PULSE v2 — PHASE 6 FIX: No unnecessary restarts ──
LOG="/root/sameer_ai_manager/immortality_pulse.log"

[ -f "$LOG" ] || touch "$LOG"
find "$LOG" -size +500k -exec truncate -s 0 {} \;

# 1. Sameer AI Manager
if ! systemctl is-active sameer_ai_manager.service >/dev/null 2>&1; then
    echo "[$(date '+%F %T')] ⚠️ SAMEER AI DOWN — Restarting" >> "$LOG"
    systemctl restart sameer_ai_manager.service
fi

# 2-6. Other services (unchanged)
for svc in openclaw_chat.service openclaw_webhook.service openclaw_emergency.service openclaw_fortress.service; do
    if ! systemctl is-active "$svc" >/dev/null 2>&1; then
        echo "[$(date '+%F %T')] ⚠️ ${svc%.service} DOWN — Restarting" >> "$LOG"
        systemctl restart "$svc"
    fi
done

# 6. OpenClaw Gateway
if ! systemctl is-active openclaw.service >/dev/null 2>&1 && ! systemctl --user is-active openclaw-gateway.service >/dev/null 2>&1; then
    if pgrep -f "openclaw.*gateway" >/dev/null 2>&1; then
        :
    else
        echo "[$(date '+%F %T')] 🔴 GATEWAY FULLY DEAD — Full restart" >> "$LOG"
        openclaw gateway restart >/dev/null 2>&1
    fi
fi

# 7. BRAIN HEALTH — PHASE 6 FIX: No unnecessary kill of healthy bot
BOT_PID=$(systemctl show sameer_ai_manager.service -p MainPID 2>/dev/null | cut -d= -f2)
if [ -n "$BOT_PID" ] && [ "$BOT_PID" -gt 0 ] 2>/dev/null; then
    # Check if bot is already active/running
    if systemctl is-active sameer_ai_manager.service >/dev/null 2>&1; then
        # Bot is running — only kill if genuinely stuck:
        # 1. CPU at exactly 0.0% (not just < 1%)
        # 2. No inbox or outbox activity for 10 min (double previous threshold)
        BOT_CPU=$(ps -p "$BOT_PID" -o %cpu --no-headers 2>/dev/null | tr -d ' ')
        if [ -n "$BOT_CPU" ]; then
            BOT_CPU_INT=${BOT_CPU%.*}
            # Only consider stuck if REALLY zero AND old inbox
            if [ "$BOT_CPU_INT" -eq 0 ] 2>/dev/null; then
                LAST_INBOX=$(stat -c %Y /root/sameer_ai_manager/openclaw_bridge/chat_inbox.jsonl 2>/dev/null || echo 0)
                NOW=$(date +%s)
                DIFF=$((NOW - LAST_INBOX))
                # Also check outbox for recent activity
                LAST_OUTBOX=$(stat -c %Y /root/sameer_ai_manager/openclaw_bridge/chat_outbox.jsonl 2>/dev/null || echo 0)
                OUTBOX_DIFF=$((NOW - LAST_OUTBOX))
                # If BOTH inbox AND outbox unchanged for 10 min AND cpu is 0%, then maybe stuck
                if [ "$DIFF" -gt 600 ] && [ "$OUTBOX_DIFF" -gt 600 ]; then
                    echo "[$(date '+%F %T')] ⚠️ BRAIN IDLE — No activity for 10min (inbox=${DIFF}s, outbox=${OUTBOX_DIFF}s). Keeping alive, no restart." >> "$LOG"
                    # Keep alive even if idle — PTB bots sit at 0% CPU during polling 
                    # No longer kill healthy bots
                fi
            fi
        fi
    fi
fi

# 8. AUTO LOG CLEANUP
find /root/sameer_ai_manager/openclaw_bridge -name "*.log" -size +5M -exec truncate -s 0 {} \;
journalctl --vacuum-time=3d >/dev/null 2>&1
