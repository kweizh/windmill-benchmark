import wmill


def main(attempt_marker_path: str):
    # Read current attempt counter from Windmill variable
    current = int(wmill.get_variable(attempt_marker_path))

    # Increment
    new_count = current + 1

    # Write back
    wmill.set_variable(attempt_marker_path, str(new_count))

    # Raise error on attempts before the 3rd one
    if new_count < 3:
        raise RuntimeError(f"Attempt {new_count} < 3, retrying...")

    # On the 3rd attempt, succeed
    return {"ok": True, "attempt": new_count}
