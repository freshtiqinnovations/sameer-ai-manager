#!/bin/bash
set -e
/root/sameer_ai_manager/scripts/compile_all.sh
systemctl restart sameer_ai_manager salama_radiator_bot salama_service_bot freshtiq_travel_bot
systemctl is-active sameer_ai_manager salama_radiator_bot salama_service_bot freshtiq_travel_bot
echo "✅ All services restarted safely"
