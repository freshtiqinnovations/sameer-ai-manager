#!/bin/bash
echo "===== SAMEER AI MANAGER V5 INVENTORY ====="
echo
echo "[SERVICES]"
systemctl list-units --type=service --state=running --no-pager
echo
echo "[TIMERS]"
systemctl list-timers --no-pager
echo
echo "[BOT PROJECTS]"
find /root -maxdepth 4 -type f -name "bot.py" 2>/dev/null
echo
echo "[SYSTEM]"
df -h /
free -h
