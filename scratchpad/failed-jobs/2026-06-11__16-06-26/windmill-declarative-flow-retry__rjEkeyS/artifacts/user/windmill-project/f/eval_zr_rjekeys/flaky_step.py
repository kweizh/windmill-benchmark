import wmill

def main(attempt_marker_path: str):
    val_str = wmill.get_variable(attempt_marker_path)
    val = int(val_str)
    val += 1
    wmill.set_variable(attempt_marker_path, str(val))
    if val < 3:
        raise RuntimeError("Flaky error")
    return {"ok": True, "attempt": 3}
