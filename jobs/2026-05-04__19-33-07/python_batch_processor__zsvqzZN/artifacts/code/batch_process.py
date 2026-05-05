import math

def main(items: list[str], batch_size: int = 10, transform: str = "upper") -> dict:
    if transform == "upper":
        transform_fn = str.upper
    elif transform == "lower":
        transform_fn = str.lower
    elif transform == "reverse":
        transform_fn = lambda s: s[::-1]
    else:
        raise ValueError(f"Unknown transform: '{transform}'. Choose 'upper', 'lower', or 'reverse'")

    results = []
    batches = []
    
    total_items = len(items)
    if total_items == 0:
        return {
            "total": 0,
            "batch_count": 0,
            "batch_size": batch_size,
            "transform": transform,
            "results": [],
            "batches": []
        }

    for i in range(0, total_items, batch_size):
        batch_items = items[i : i + batch_size]
        transformed_batch = [transform_fn(item) for item in batch_items]
        
        batches.append({
            "batch_index": i // batch_size,
            "items": transformed_batch
        })
        results.extend(transformed_batch)

    return {
        "total": total_items,
        "batch_count": math.ceil(total_items / batch_size),
        "batch_size": batch_size,
        "transform": transform,
        "results": results,
        "batches": batches
    }
