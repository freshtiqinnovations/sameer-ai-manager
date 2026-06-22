#!/bin/bash
LOG="/root/sameer_ai_manager/logs/self_manager.log"

echo "---- $(date) ----" >> "$LOG"

# Sameer AI Manager check
systemctl is-active --quiet sameer_ai_manager
if [ $? -ne 0 ]; then
  echo "sameer_ai_manager down, restarting..." >> "$LOG"
  systemctl restart sameer_ai_manager
fi

# Salama bot check
systemctl is-active --quiet salama_radiator_bot
if [ $? -ne 0 ]; then
  echo "salama_radiator_bot down, restarting..." >> "$LOG"
  systemctl restart salama_radiator_bot
fi

# Backup important files
cp /root/sameer_ai_manager/bot.py /root/sameer_ai_manager/backups/bot_auto_$(date +%F_%H%M).py 2>/dev/null
cp /root/workspaces/customers/el_salama_radiator_factory/bot.py /root/workspaces/customers/el_salama_radiator_factory/backups/bot_auto_$(date +%F_%H%M).py 2>/dev/null
cp /root/workspaces/customers/el_salama_radiator_factory/data/business.json /root/workspaces/customers/el_salama_radiator_factory/backups/business_auto_$(date +%F_%H%M).json 2>/dev/null

# Keep latest 40 backups only
ls -1t /root/sameer_ai_manager/backups/* 2>/dev/null | tail -n +41 | xargs -r rm -f
ls -1t /root/workspaces/customers/el_salama_radiator_factory/backups/* 2>/dev/null | tail -n +41 | xargs -r rm -f

echo "self check done" >> "$LOG"
