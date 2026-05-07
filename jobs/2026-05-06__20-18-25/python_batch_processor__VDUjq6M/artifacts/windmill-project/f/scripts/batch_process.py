import math
from typing import List, Dict, Any


def main(items: List[str], batch_size: int = 10, transform: str = "upper") -> Dict[str, Any]:
    """
    Process a list of strings in configurable batches with specified transformation.

    Args:
        items: List of strings to process
        batch_size: Number of items to process per batch (default: 10)
        transform: Transformation to apply - 'upper', 'lower', or 'reverse' (default: 'upper')

    Returns:
        Dictionary containing:
            - total: Total number of items processed
            - batch_count: Number of batches processed
            - batch_size: Batch size used
            - transform: Transformation applied
            - results: Flat list of all transformed items
            - batches: List of batch results with batch_index and items

    Raises:
        ValueError: If transform is not one of 'upper', 'lower', or 'reverse'
    """
    # Validate transform option
    if transform not in ("upper", "lower", "reverse"):
        raise ValueError(f"Unknown transform: '{transform}'. Choose 'upper', 'lower', or 'reverse'")

    # Calculate batch count
    total = len(items)
    batch_count = math.ceil(total / batch_size) if items else 0

    # Process all items and collect results
    results = []
    batches = []

    for i in range(0, total, batch_size):
        # Get current batch
        batch = items[i : i + batch_size]
        batch_index = i // batch_size

        # Transform items in this batch
        batch_results = []
        for item in batch:
            if transform == "upper":
                transformed = item.upper()
            elif transform == "lower":
                transformed = item.lower()
            elif transform == "reverse":
                transformed = item[::-1]
            batch_results.append(transformed)

        # Add batch results to overall results
        results.extend(batch_results)

        # Record batch information
        batches.append({"batch_index": batch_index, "items": batch_results})

    return {
        "total": total,
        "batch_count": batch_count,
        "batch_size": batch_size,
        "transform": transform,
        "results": results,
        "batches": batches,
    }