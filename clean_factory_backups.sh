#!/bin/bash
set -e
BASE="/root/sameer_ai_manager"
ARCH="/root/backups/factory_old_code_backups_$(date +%F_%H%M%S)"
mkdir -p "$ARCH"

find "$BASE" -type f \( -name "*.BAK_*" -o -name "*.safe_*" -o -name "bot_auto_*.py" -o -name "*.backup*" \) | sort | head -n -20 > /tmp/old_factory_backups.txt || true

COUNT=$(cat /tmp/old_factory_backups.txt | wc -l)

if [ "$COUNT" -gt 0 ]; then
  while read f; do
    [ -f "$f" ] && mkdir -p "$ARCH$(dirname "$f")" && mv "$f" "$ARCH$f"
  done < /tmp/old_factory_backups.txt
fi

echo "FACTORY_BACKUP_CLEANUP_DONE"
echo "Moved old backups: $COUNT"
echo "Archived at: $ARCH"
echo "Latest 20 backup files kept in project."
