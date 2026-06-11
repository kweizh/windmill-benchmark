import wmill

def main():
    state = wmill.get_state()
    if state is None:
        state = {"runs": 0}
    
    state["runs"] += 1
    wmill.set_state(state)
    return state
