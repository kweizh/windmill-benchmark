import wmill

def main(attempt_marker_path: str):
    # Read the current variable value
    val_str = wmill.get_variable(attempt_marker_path)
    val = int(val_str)
    
    # Increment
    new_val = val + 1
    
    # Write it back
    wmill.set_variable(attempt_marker_path, str(new_val))
    
    # Raise RuntimeError if new counter value is less than 3
    if new_val < 3:
        raise RuntimeError(f"Counter is {new_val}, which is less than 3")
        
    # On the third invocation (when the counter reaches 3), return the dict
    return {"ok": True, "attempt": new_val}
