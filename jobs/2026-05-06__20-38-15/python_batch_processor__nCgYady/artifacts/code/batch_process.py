import math

def main(items: list[str], batch_size: int = 10, transform: str = "upper") -> dict:
    if transform == "upper":
        transform_func = lambda s: s.upper()
    elif transform == "lower":
        transform_func = lambda s: s.lower()
    elif transform == "reverse":
        transform_func = lambda s: s[::-1]
    else:
        raise ValueError(f"Unknown transform: '{transform}'. Choose 'upper', 'lower', or 'reverse'")

    results = []
    batches = []
    
    total_items = len(items)
    batch_count = math.ceil(total_items / batch_size) if items else 0

    for i in range(batch_count):
        start = i * batch_size
        end = min(start + batch_size, total_items)
        batch_items = items[start:end]
        
        transformed_batch = [transform_func(item) for item in batch_items]
        results.extend(transformed_batch)
        
        batches.append({
            "batch_index": i,
            "items": transformed_batch
        })

    return {
        "total": total_items,
        "batch_count": batch_count,
        "batch_size": batch_size,
        "transform": transform,
        "results": results,
        "batches": batches
    }
