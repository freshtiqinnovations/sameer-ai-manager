#!/bin/bash
set -e
TS=$(date +%F_%H%M%S)
mkdir -p /root/backups/all
tar -czf /root/backups/all/all_bots_$TS.tar.gz /root/sameer_ai_manager /root/workspaces/customers
echo "✅ Backup created: /root/backups/all/all_bots_$TS.tar.gz"
