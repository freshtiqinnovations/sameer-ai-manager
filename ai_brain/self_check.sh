#!/bin/bash

LOG="/root/self_check.log"

echo "==== $(date) ====" >> $LOG

systemctl is-active sameer_ai_manager.service >> $LOG
systemctl is-active sameer_auto_heal.service >> $LOG
systemctl is-active sameer_ai_worker_auto.service >> $LOG

df -h >> $LOG
free -m >> $LOG

if [ $(df / | awk 'NR==2 {print $5}' | tr -d '%') -ge 90 ]; then
 bash /root/auto_cleanup.sh
fi
