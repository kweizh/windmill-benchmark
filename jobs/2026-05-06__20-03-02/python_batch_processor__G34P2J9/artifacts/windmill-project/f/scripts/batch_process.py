import math
from typing import List, Dict, Any


def _apply_transform(value: str, transform: str) -> str:
    if transform == "upper":
        return value.upper()
    if transform == "lower":
        return value.lower()
    if transform == "reverse":
        return value[::-1]
    raise ValueError(
        f"Unknown transform: '{transform}'. Choose 'upper', 'lower', or 'reverse'"
    )


def main(items: list[str], batch_size: int = 10, transform: str = "upper") -> dict:
    results: List[str] = []
    batches: List[Dict[str, Any]] = []

    for start_index in range(0, len(items), batch_size):
        batch_items = items[start_index : start_index + batch_size]
        batch_results = [_apply_transform(item, transform) for item in batch_items]
        results.extend(batch_results)
        batches.append(
            {
                "batch_index": len(batches),
                "items": batch_results,
            }
        )

    return {
        "total": len(items),
        "batch_count": math.ceil(len(items) / batch_size) if items else 0,
        "batch_size": batch_size,
        "transform": transform,
        "results": results,
        "batches": batches,
    }
