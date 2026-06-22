#!/bin/bash

mkdir -p /root/backups

tar --exclude='/root/backups' \
-czf /root/backups/manager_$(date +%F_%H-%M).tar.gz \
/root/sameer_ai_manager
