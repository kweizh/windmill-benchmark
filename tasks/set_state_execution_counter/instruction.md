# Fix the Windmill Heartbeat Script to Use Persistent State

## Background

Windmill provides a built-in state API (`get_state` / `set_state`) that lets a script persist data across multiple executions of the same trigger. This is essential for building counters, accumulators, or any script that must remember what happened the last time it ran.

You have a Python heartbeat script located at `/home/user/windmill-project/f/monitoring/heartbeat.py`. The script is supposed to track how many times it has been executed and return that count. However, the current implementation resets the counter to `0` every time it runs, making it useless as a persistent tracker.

## Requirements

Fix the script so that:
1. It imports `get_state` and `set_state` from the `wmill` package.
2. It loads the current persistent count using `get_state()`, defaulting to `0` if no prior state exists (i.e., `get_state()` returns `None`).
3. It increments the count by `1`.
4. It persists the updated count using `set_state(count)`.
5. It returns a dictionary with the keys `count`, `timestamp`, and `message`.

## Implementation Guide

1. Open `/home/user/windmill-project/f/monitoring/heartbeat.py`.
2. Add the import line at the top of the file:
   ```python
   from wmill import get_state, set_state
   ```
3. Replace the broken `count = 0` line with a call to `get_state()` that falls back to `0`:
   ```python
   count = get_state() or 0
   ```
4. Keep the increment `count += 1` as-is.
5. After the increment, add a call to persist the new value:
   ```python
   set_state(count)
   ```
6. The return statement should remain:
   ```python
   return {
       "count": count,
       "timestamp": time.time(),
       "message": f"Heartbeat #{count}"
   }
   ```

## Constraints

- Project path: `/home/user/windmill-project`
- Script path: `/home/user/windmill-project/f/monitoring/heartbeat.py`
- Do NOT rename the function or change the return keys.
- Do NOT remove the `import time` statement.
- No live Windmill server is required; edit the file directly.
