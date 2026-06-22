#!/bin/bash
echo "=== SAMEER V5 MEMORY ==="
echo "BOTS=$(find /root -maxdepth 4 -type f -name bot.py 2>/dev/null | wc -l)"
echo "SERVICES=$(systemctl list-units --type=service --state=running --no-pager | grep service | wc -l)"
echo "DATE=$(date)"
