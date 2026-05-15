import time
from wmill import get_state, set_state

def main():
    count = get_state() or 0
    count += 1
    set_state(count)
    return {
        "count": count,
        "timestamp": time.time(),
        "message": f"Heartbeat #{count}"
    }
