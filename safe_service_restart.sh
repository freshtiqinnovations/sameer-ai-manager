#!/bin/bash
SVC=$1
[ -z "$SVC" ] && echo "Usage: safe_service_restart.sh service_name" && exit 1
LINE=$(grep "^${SVC}|" /root/customer_registry/services.map)
[ -z "$LINE" ] && echo "Service not in registry: $SVC" && exit 1
FILE=$(echo "$LINE" | cut -d"|" -f2)
/root/sameer_ai_manager/safe_restart.sh "$SVC" "$FILE"
