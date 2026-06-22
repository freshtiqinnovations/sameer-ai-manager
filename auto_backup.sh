#!/bin/bash
# Auto backup — Keep latest 2
DIR="/root/backups/auto"
mkdir -p "$DIR"

TS=$(date +%Y%m%d_%H%M%S)
tar -czf "$DIR/auto_backup_$TS.tar.gz" \
  /root/sameer_ai_manager \
  /root/workspaces/customers \
  2>/dev/null

# Keep only latest 2
ls -t "$DIR"/auto_backup_*.tar.gz 2>/dev/null | tail -n +3 | xargs -r rm -f

echo "✅ Auto backup: auto_backup_$TS.tar.gz"
du -sh "$DIR"
