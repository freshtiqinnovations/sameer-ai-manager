#!/bin/bash
LOG="/root/sameer_ai_manager/watchdog.log"
echo "===== $(date) WATCHDOG START =====" >> "$LOG"

SERVICES="sameer_ai_manager salama_radiator_bot freshtiq_travel_bot salama_service_bot"

for S in $SERVICES; do
  if systemctl list-unit-files | grep -q "^$S.service"; then
    STATUS=$(systemctl is-active $S)
    echo "$S = $STATUS" >> "$LOG"
    if [ "$STATUS" != "active" ]; then
      echo "Restarting $S..." >> "$LOG"
      systemctl restart $S
      sleep 2
      systemctl status $S --no-pager | tail -20 >> "$LOG"
    fi
  fi
done

echo "===== WATCHDOG END =====" >> "$LOG"
