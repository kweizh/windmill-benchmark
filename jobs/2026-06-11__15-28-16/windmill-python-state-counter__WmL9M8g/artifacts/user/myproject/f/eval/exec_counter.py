import wmill

def main():
    state = wmill.get_state()
    if state is None:
        state = {"runs": 0}
    
    # Increment the runs field by one
    new_runs = state.get("runs", 0) + 1
    new_state = {"runs": new_runs}
    
    wmill.set_state(new_state)
    return new_state
