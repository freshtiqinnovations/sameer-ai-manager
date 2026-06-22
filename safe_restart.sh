#!/bin/bash
SERVICE=$1
FILE=$2
[ -z "$SERVICE" ] && echo "Usage: safe_restart.sh service_name /path/bot.py" && exit 1
[ -z "$FILE" ] && echo "Missing python file path" && exit 1
echo "🔒 Safe restart: $SERVICE"
/root/sameer_ai_manager/safe_compile.sh "$FILE" || exit 1
systemctl restart "$SERVICE"
sleep 2
systemctl status "$SERVICE" --no-pager | head -25
