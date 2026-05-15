You are working inside a Windmill project environment. A health monitor script at `/home/user/windmill-project/f/scripts/health_monitor.py` is broken — it sends an alert on EVERY scheduled run regardless of whether the service status has changed. Your task is to fix the script so that it:
1. Imports `get_state` (in addition to `set_state`) from the `wmill` package
2. Reads the previous status at the start: `last_status = get_state() or 'unknown'`
3. Only calls `send_alert()` when `current_status != last_status`
4. Always calls `set_state(current_status)` to persist the new status
5. Returns a dict: `{'status': current_status, 'changed': current_status != last_status, 'alerted': current_status != last_status}`

Do not change the `check_endpoint` or `send_alert` helper functions. Only modify the `main` function and the imports.
