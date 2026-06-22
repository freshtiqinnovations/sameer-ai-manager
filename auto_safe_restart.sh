#!/bin/bash
SERVICE=$1
FILE=$2
[ -z "$SERVICE" ] && echo "Usage: auto_safe_restart.sh service file" && exit 1
[ -z "$FILE" ] && echo "Missing file" && exit 1
BACKUP=${FILE}.bak_$(date +%F_%H-%M-%S)
cp "$FILE" "$BACKUP"
python3 -m py_compile "$FILE"
if [ $? -ne 0 ]; then echo "❌ COMPILE FAILED"; exit 1; fi
systemctl restart "$SERVICE"
sleep 3
systemctl is-active --quiet "$SERVICE"
if [ $? -eq 0 ]; then echo "✅ SERVICE OK"; systemctl status "$SERVICE" --no-pager | head -15; exit 0; fi
echo "⚠️ RESTART FAILED - AUTO ROLLBACK"
cp "$BACKUP" "$FILE"
python3 -m py_compile "$FILE"
systemctl restart "$SERVICE"
sleep 3
systemctl status "$SERVICE" --no-pager | head -20
