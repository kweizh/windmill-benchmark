def main(numbers: list[float]) -> dict:
    count = len(numbers)
    total = sum(numbers)
    average = total / count if count > 0 else 0.0
    return {"count": count, "total": total, "average": average}
