#!/bin/bash
LOG="/root/sameer_ai_manager/logs/night_guard.log"
echo "==== $(date) NIGHT GUARD ====" >> $LOG

# disk high ho to cleanup
USED=$(df / | awk 'NR==2 {print $5}' | tr -d '%')
if [ "$USED" -ge 80 ]; then
  bash /root/auto_cleanup.sh >> $LOG 2>&1
fi

# main engines keep alive — only restart UNHEALTHY services
# HEALTHY = active + no recent crash
for s in sameer_ai_manager.service sameer_ai_worker.service sameer_auto_heal.service sameer_self_check.timer sameer_auto_cleanup.timer sameer_watchdog.service sameer_repair_engine.service sameer_master_ai.service; do
  STATUS=$(systemctl is-active "$s" 2>/dev/null)
  if [ "$STATUS" = "active" ]; then
    echo "  ✅ $s healthy, no restart" >> $LOG
  else
    echo "  ⚠️ $s $STATUS → restarting" >> $LOG
    systemctl restart "$s" >> $LOG 2>&1 || true
  fi
done

# customer bots keep alive — only restart INACTIVE/FAILED services
for s in freshtiq_ai_travel_pro.service salama_service_bot.service salama_radiator_bot.service restaurant_demo_bot.service autopilot_hub_bot.service; do
  STATUS=$(systemctl is-active "$s" 2>/dev/null)
  if [ "$STATUS" != "active" ]; then
    echo "  ⚠️ $s $STATUS → restarting" >> $LOG
    systemctl restart "$s" >> $LOG 2>&1
  else
    echo "  ✅ $s healthy, no restart" >> $LOG
  fi
done

df -h >> $LOG
systemctl list-units --type=service --all | grep -E 'sameer|freshtiq|salama|restaurant|autopilot' >> $LOG
echo "NIGHT_GUARD_DONE" >> $LOG
