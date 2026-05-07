def main(orders: list[dict], min_amount: float = 0.0) -> dict:
    filtered = [order for order in orders if order["amount"] >= min_amount]
    return {
        "total_orders": len(filtered),
        "total_amount": sum(order["amount"] for order in filtered),
        "shipped_count": sum(1 for order in filtered if order["shipped"]),
        "items": [
            {
                "id": order["id"],
                "product": order["product"],
                "amount": order["amount"],
            }
            for order in filtered
        ],
    }
