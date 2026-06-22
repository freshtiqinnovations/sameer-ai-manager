#!/bin/bash
NAME=${1:-manual}
mkdir -p /root/sameer_ai_manager/safe_backups
tar -czf /root/sameer_ai_manager/safe_backups/${NAME}$(date +%F%H-%M-%S).tar.gz /root/sameer_ai_manager /root/workspaces /etc/systemd/system 2>/dev/null
ls -lh /root/sameer_ai_manager/safe_backups | tail -5
