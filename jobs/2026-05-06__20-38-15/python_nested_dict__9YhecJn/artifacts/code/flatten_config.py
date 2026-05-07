def main(config: dict, prefix: str = "") -> dict:
    """
    Flatten a nested dictionary into a single-level dictionary with dot-notation keys.
    """
    flattened = {}

    def _flatten(current_dict: dict, current_prefix: str):
        for key, value in current_dict.items():
            new_key = f"{current_prefix}.{key}" if current_prefix else key
            if isinstance(value, dict):
                _flatten(value, new_key)
            else:
                flattened[new_key] = value

    _flatten(config, prefix)
    return flattened
