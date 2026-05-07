def main(orders: list[dict], min_amount: float = 0.0) -> dict:
    """
    Filter and summarize a list of orders.

    Args:
        orders: List of order dictionaries with keys: id (int), product (str),
                amount (float), shipped (bool)
        min_amount: Minimum order amount to include in results (default: 0.0)

    Returns:
        Dictionary with summary statistics and filtered items
    """
    # Filter orders where amount >= min_amount
    filtered = [order for order in orders if order["amount"] >= min_amount]

    # Build result dictionary
    result = {
        "total_orders": len(filtered),
        "total_amount": sum(o["amount"] for o in filtered),
        "shipped_count": sum(1 for o in filtered if o["shipped"]),
        "items": [
            {"id": o["id"], "product": o["product"], "amount": o["amount"]}
            for o in filtered
        ]
    }

    return result