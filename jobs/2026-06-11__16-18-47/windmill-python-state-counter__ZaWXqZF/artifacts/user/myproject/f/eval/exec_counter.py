import wmill


def main():
    state = wmill.get_state()
    if state is None:
        state = {"runs": 0}
    new_state = {"runs": state["runs"] + 1}
    wmill.set_state(new_state)
    return new_state