#!/bin/bash
# ── IMMORTAL CLEANER v2.0 — Auto-clean all trash ──
LOG="/root/sameer_ai_manager/cleaner.log"
echo "[$(date '+%F %T')] 🧹 CLEANER RUNNING..." >> "$LOG"

# 1. Journal — sirf last 2 days keep
journalctl --vacuum-time=2d >/dev/null 2>&1
echo "  ✓ Journal vacuum: 2d" >> "$LOG"

# 2. Old bridge logs >10MB truncate
find /root/sameer_ai_manager/openclaw_bridge -name "*.log" -size +2M -exec truncate -s 0 {} \;
echo "  ✓ Truncated large bridge logs" >> "$LOG"

# 3. Clean archived jsonl files
find /root/sameer_ai_manager/openclaw_bridge -name "*archived*" -mtime +1 -delete 2>/dev/null
echo "  ✓ Deleted >1d archived files" >> "$LOG"

# 4. Keep only latest 3 backups
BACKUP_DIR="/root/backups"
if [ -d "$BACKUP_DIR" ] && [ "$(ls -1 "$BACKUP_DIR"/*.tar.gz 2>/dev/null | wc -l)" -gt 3 ]; then
    ls -t "$BACKUP_DIR"/*.tar.gz 2>/dev/null | tail -n +4 | xargs rm -f
    echo "  ✓ Kept latest 3 backups only" >> "$LOG"
fi

# 5. Clean old temp files
find /tmp -type f -atime +1 -delete 2>/dev/null
echo "  ✓ Cleaned /tmp" >> "$LOG"

# 6. Clean python __pycache__
find /root -name "__pycache__" -type d -mtime +1 -exec rm -rf {} + 2>/dev/null
echo "  ✓ Cleaned __pycache__" >> "$LOG"

# 7. Clean old .pyc files
find /root -name "*.pyc" -mtime +1 -delete 2>/dev/null
echo "  ✓ Cleaned .pyc" >> "$LOG"

# 8. Clean apt cache
apt-get clean 2>/dev/null
echo "  ✓ Cleand apt cache" >> "$LOG"

# 9. Keep cleaner.log small
if [ -f "$LOG" ] && [ "$(stat -c%s "$LOG")" -gt 50000 ]; then
    tail -20 "$LOG" > "${LOG}.tmp" && mv "${LOG}.tmp" "$LOG"
fi

echo "[$(date '+%F %T')] ✅ CLEANER DONE" >> "$LOG"
