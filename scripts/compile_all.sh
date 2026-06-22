#!/bin/bash
set -e
python3 -m py_compile /root/sameer_ai_manager/bot.py
python3 -m py_compile /root/sameer_ai_manager/safe_engine.py
find /root/workspaces/customers -name "*.py" -print0 | xargs -0 -n1 python3 -m py_compile
echo "✅ All Python files compile OK"
