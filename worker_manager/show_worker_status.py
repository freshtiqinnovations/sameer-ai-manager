from pathlib import Path
p=Path("/root/sameer_ai_manager/ai_worker/current_status.txt")
print(p.read_text() if p.exists() else "🤖 Idle - No active task")
