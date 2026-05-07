# requirements:
#

def main(config: dict, prefix: str = "") -> dict:
    """
    Flatten a nested dictionary into a single-level dict with dot-notation keys.

    Args:
        config: The nested dictionary to flatten.
        prefix: Optional prefix to prepend to all keys.

    Returns:
        A flat dictionary with dot-notation keys.

    Examples:
        >>> main({"a": {"b": 1, "c": {"d": 2}}})
        {"a.b": 1, "a.c.d": 2}

        >>> main({"x": 1}, prefix="ns")
        {"ns.x": 1}
    """
    result = {}
    _flatten(config, prefix, result)
    return result


def _flatten(obj: dict, prefix: str, result: dict) -> None:
    """
    Recursively walk *obj*, writing leaf values into *result*.

    Lists and all other non-dict values are treated as leaves and written
    as-is — only dicts trigger further recursion.
    """
    for key, value in obj.items():
        full_key = f"{prefix}.{key}" if prefix else key

        if isinstance(value, dict):
            # Recurse into nested dicts
            _flatten(value, full_key, result)
        else:
            # Scalars (str, int, float, bool) and lists are kept as-is
            result[full_key] = value
