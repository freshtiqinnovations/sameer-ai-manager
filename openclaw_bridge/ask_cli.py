#!/usr/bin/env python3
import sys, traceback
import openclaw_brain
q=sys.stdin.read().strip()
try:
    print(openclaw_brain.ask(q) or "NO_AI_OUTPUT")
except Exception:
    print("AI_ERROR")
    print(traceback.format_exc())
