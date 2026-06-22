# RESTORE_NOTE — Sameer AI Manager Working State
## Date: 2026-06-07 01:53 IST

### 🔥 STATUS: STABLE & WORKING

- **PID**: 1317478
- **Service**: `sameer_ai_manager.service` — active (running)
- **Conflicts resolved**: `openclaw_telegram.service` stopped (same token conflict)

### What Was Fixed
1. **Event loop crash** → `asyncio.new_event_loop()` before `ApplicationBuilder()`
2. **APScheduler zoneinfo/pytz bug** → Patched `/venv_new/lib/python3.10/site-packages/apscheduler/util.py` (ZoneInfo + datetime.timezone auto-conversion)
3. **Systemd drop-in truncated token** → Rewrote with actual 46-char token

### Restore Procedure
```bash
# If everything breaks:
systemctl stop sameer_ai_manager.service
tar -xzf /root/backups/sameer_ai_manager_working_latest.tgz -C /
cp -a /root/backups/sameer_ai_manager_working_20260607_015309/venv_new /root/sameer_ai_manager/
cp /root/backups/sameer_ai_manager_working_20260607_015309/.env /root/sameer_ai_manager/.env
cp /root/backups/sameer_ai_manager_working_20260607_015309/bot.py /root/sameer_ai_manager/bot.py
systemctl daemon-reload && systemctl start sameer_ai_manager.service
```

### Key Files
- `bot.py` (73KB) — main bot with event loop fix + DeepSeek integration
- `assistant_engine.py` — DeepSeek-only AI engine (no OpenAI/OpenRouter)
- `apscheduler_util_patched.py` — backup of the patched file

### ⚠️ Critical Note
APScheduler patch applied to **venv_local copy**, not system-wide. Recreate if venv is rebuilt.
```
