import wmill


def main(attempt_marker_path: str):
    current = int(wmill.get_variable(attempt_marker_path))
    new_count = current + 1
    wmill.set_variable(attempt_marker_path, str(new_count))

    if new_count < 3:
        raise RuntimeError(f"Flaky failure on attempt {new_count}, need 3 to succeed")

    return {"ok": True, "attempt": 3}
