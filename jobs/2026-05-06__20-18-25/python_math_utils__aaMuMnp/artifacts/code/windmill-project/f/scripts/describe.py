def main(values: list[float]) -> dict:
    if not values:
        raise ValueError("Cannot describe an empty list")
    sorted_v = sorted(values)
    n = len(sorted_v)
    mid = n // 2
    median = sorted_v[mid] if n % 2 else (sorted_v[mid - 1] + sorted_v[mid]) / 2
    return {
        "count": n,
        "min": sorted_v[0],
        "max": sorted_v[-1],
        "mean": sum(sorted_v) / n,
        "median": median,
        "range": sorted_v[-1] - sorted_v[0],
    }