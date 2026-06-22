#!/bin/bash
FILE=$1
[ -z "$FILE" ] && echo "Usage: safe_compile.sh /path/file.py" && exit 1
[ ! -f "$FILE" ] && echo "File not found: $FILE" && exit 1
cp "$FILE" "${FILE}.bak_$(date +%F_%H-%M-%S)"
python3 -m py_compile "$FILE"
if [ $? -eq 0 ]; then echo "✅ COMPILE_OK: $FILE"; else echo "❌ COMPILE_FAILED: $FILE"; exit 1; fi
