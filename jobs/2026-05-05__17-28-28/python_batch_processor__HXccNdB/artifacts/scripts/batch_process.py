import math


def main(items: list[str], batch_size: int = 10, transform: str = "upper") -> dict:
    valid_transforms = ("upper", "lower", "reverse")
    if transform not in valid_transforms:
        raise ValueError(
            f"Unknown transform: '{transform}'. Choose 'upper', 'lower', or 'reverse'"
        )

    def apply_transform(item: str) -> str:
        if transform == "upper":
            return item.upper()
        elif transform == "lower":
            return item.lower()
        else:  # reverse
            return item[::-1]

    batches = []
    results = []

    batch_count = math.ceil(len(items) / batch_size) if items else 0

    for i in range(batch_count):
        batch_items = items[i * batch_size : (i + 1) * batch_size]
        batch_results = [apply_transform(item) for item in batch_items]
        results.extend(batch_results)
        batches.append({"batch_index": i, "items": batch_results})

    return {
        "total": len(items),
        "batch_count": batch_count,
        "batch_size": batch_size,
        "transform": transform,
        "results": results,
        "batches": batches,
    }
