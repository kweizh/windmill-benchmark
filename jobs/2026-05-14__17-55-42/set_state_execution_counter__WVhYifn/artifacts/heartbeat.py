import time
from wmill import get_state, set_state

def main():
    # TODO: Fix this script to use Windmill state to track execution count
    count = get_state() or 0
    count += 1
    set_state(count)
    return {
        "count": count,
        "timestamp": time.time(),
        "message": f"Heartbeat #{count}"
    }