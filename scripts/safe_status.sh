#!/bin/bash
echo "👑 SAMEER SAFE STATUS"
date
echo
systemctl --no-pager --type=service | grep -E "sameer_ai_manager|salama|freshtiq" || true
echo
df -h /
echo
free -h
