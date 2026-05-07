def main(config: dict, prefix: str = "") -> dict:
    """
    Flatten a nested dictionary into a single-level dictionary with dot-notation keys.
    
    Args:
        config: The nested dictionary to flatten
        prefix: Optional prefix to prepend to all keys
        
    Returns:
        A flattened dictionary with dot-notation keys
        
    Examples:
        >>> main({"a": {"b": 1, "c": {"d": 2}}})
        {"a.b": 1, "a.c.d": 2}
        
        >>> main({"x": 1}, prefix="ns")
        {"ns.x": 1}
    """
    result = {}
    
    def flatten(obj, current_prefix):
        if isinstance(obj, dict):
            for key, value in obj.items():
                # Build the new key by combining current_prefix and key
                if current_prefix:
                    new_key = f"{current_prefix}.{key}"
                else:
                    new_key = key
                
                # Recursively flatten if value is a dict, otherwise add to result
                if isinstance(value, dict):
                    flatten(value, new_key)
                else:
                    result[new_key] = value
        else:
            # If config itself is not a dict, just return it with prefix
            result[current_prefix] = obj
    
    flatten(config, prefix)
    return result