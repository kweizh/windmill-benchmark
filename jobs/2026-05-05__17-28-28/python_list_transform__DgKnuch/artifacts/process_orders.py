def main(orders: list[dict], min_amount: float = 0.0) -> dict:
    """Filter and summarize a list of orders by minimum amount."""
    filtered = [o for o in orders if o["amount"] >= min_amount]

    return {
        "total_orders": len(filtered),
        "total_amount": sum(o["amount"] for o in filtered),
        "shipped_count": sum(1 for o in filtered if o["shipped"]),
        "items": [
            {"id": o["id"], "product": o["product"], "amount": o["amount"]}
            for o in filtered
        ],
    }
