from wmill import get_state, set_state

def main():
    current_count = get_state()
    if current_count is None:
        current_count = 0
    new_count = current_count + 1
    set_state(new_count)
    return {
        "count": new_count,
        "message": f"This script has been executed {new_count} time(s)."
    }
