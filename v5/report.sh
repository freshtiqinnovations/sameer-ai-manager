#!/bin/bash
echo "🧠 SAMEER AI MANAGER V5 REPORT"
echo
date
echo
echo "🤖 BOTS:"
find /root -maxdepth 4 -type f -name "bot.py" 2>/dev/null | wc -l
echo
echo "⚙️ RUNNING SERVICES:"
systemctl list-units --type=service --state=running --no-pager | grep service | wc -l
echo
echo "💾 DISK:"
df -h / | tail -1
echo
echo "🧠 RAM:"
free -h | grep Mem
