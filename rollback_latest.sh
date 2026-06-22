#!/bin/bash
SVC=$1
[ -z "$SVC" ] && echo "Usage: rollback_latest.sh service_name" && exit 1
LINE=$(grep "^${SVC}|" /root/customer_registry/services.map)
[ -z "$LINE" ] && echo "Service not found in registry" && exit 1
FILE=$(echo "$LINE" | cut -d"|" -f2)
BACK=$(ls -t ${FILE}.bak_* 2>/dev/null | head -1)
[ -z "$BACK" ] && echo "No backup found for $FILE" && exit 1
cp "$BACK" "$FILE"
python3 -m py_compile "$FILE" || exit 1
systemctl restart "$SVC"
sleep 2
echo "ROLLBACK_DONE: $SVC"
systemctl status "$SVC" --no-pager | head -20
