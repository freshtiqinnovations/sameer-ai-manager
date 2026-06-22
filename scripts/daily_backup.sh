#!/bin/bash
# Daily backup (manager scripts) — Keep latest 3
DIR="/root/backups/daily"
mkdir -p "$DIR"

TS=$(date +%F_%H%M%S)
tar -czf "$DIR/daily_manager_$TS.tar.gz" \
  /root/sameer_ai_manager \
  /root/workspaces/customers \
  2>/dev/null

# Keep only latest 3
ls -t "$DIR"/daily_manager_*.tar.gz 2>/dev/null | tail -n +4 | xargs -r rm -f

echo "✅ Manager daily backup done: daily_manager_$TS.tar.gz"
du -sh "$DIR"
