from __future__ import annotations

from typing import Any, Dict


def main(config: dict, prefix: str = "") -> dict:
    """Flatten a nested dict into dot-notation keys.

    Args:
        config: The nested dictionary to flatten.
        prefix: Optional prefix to prepend to keys.

    Returns:
        A flattened dictionary with dot-notation keys.
    """

    def _flatten(current: Dict[str, Any], parent_key: str) -> Dict[str, Any]:
        items: Dict[str, Any] = {}
        for key, value in current.items():
            new_key = f"{parent_key}.{key}" if parent_key else str(key)
            if isinstance(value, dict):
                items.update(_flatten(value, new_key))
            else:
                items[new_key] = value
        return items

    base = _flatten(config, "")
    if prefix:
        return {f"{prefix}.{key}": value for key, value in base.items()}
    return base
