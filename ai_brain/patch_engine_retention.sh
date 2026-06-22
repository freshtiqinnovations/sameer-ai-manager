#!/bin/bash
# Patch Engine Retention: Keep latest 5 backups
PATCH_DIR="/root/backups/ai_patch_engine"
mkdir -p "$PATCH_DIR"

echo "[$(date '+%F %T')] PATCH ENGINE RETENTION START"

# Group by bot prefix, keep latest 5 each
for prefix in autopilot_hub_bot sameer_ai_manager freshtiq salama; do
    count=$(ls "$PATCH_DIR/${prefix}_"*.tar.gz 2>/dev/null | wc -l)
    if [ "$count" -gt 5 ]; then
        echo "  $prefix: $count files → keeping 5, removing $((count - 5))"
        ls -t "$PATCH_DIR/${prefix}_"*.tar.gz 2>/dev/null | tail -n +6 | xargs -r rm -f
    else
        echo "  $prefix: $count files (within limit)"
    fi
done

# Remove any orphan .tar.gz not matching known prefixes
for f in "$PATCH_DIR"/*.tar.gz; do
    [ -f "$f" ] || continue
    base=$(basename "$f")
    match=0
    for prefix in autopilot_hub_bot sameer_ai_manager freshtiq salama; do
        [[ "$base" == ${prefix}_* ]] && match=1 && break
    done
    [ "$match" -eq 0 ] && echo "  ORPHAN: $base → removed" && rm -f "$f"
done

echo "[$(date '+%F %T')] PATCH ENGINE RETENTION DONE"
du -sh "$PATCH_DIR"
