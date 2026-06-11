import wmill


def main(attempt_marker_path: str):
    current = int(wmill.get_variable(attempt_marker_path))
    new_value = current + 1
    wmill.set_variable(attempt_marker_path, str(new_value))
    if new_value < 3:
        raise RuntimeError(f"Attempt {new_value} failed, retrying...")
    return {"ok": True, "attempt": new_value}