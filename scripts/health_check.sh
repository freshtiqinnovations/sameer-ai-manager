#!/bin/bash
echo "🤖 SERVICES"
systemctl is-active sameer_ai_manager salama_radiator_bot salama_service_bot freshtiq_travel_bot
echo
echo "💾 DISK"
df -h /
echo
echo "🧠 MEMORY"
free -h
echo
echo "🔥 LAST ERRORS"
journalctl -u sameer_ai_manager -n 20 --no-pager
