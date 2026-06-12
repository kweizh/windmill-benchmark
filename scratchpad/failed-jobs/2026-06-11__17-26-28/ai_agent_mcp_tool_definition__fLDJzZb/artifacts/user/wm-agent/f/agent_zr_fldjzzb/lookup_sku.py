def main(sku: str):
    # Returns structured data about a product SKU
    sku_upper = sku.strip().upper()
    if "WIDGET-42" in sku_upper:
        return {
            "sku": "WIDGET-42",
            "unit_price": 42.0,
            "currency": "USD"
        }
    elif "WIDGET" in sku_upper:
        return {
            "sku": sku_upper,
            "unit_price": 19.99,
            "currency": "USD"
        }
    else:
        return {
            "sku": sku_upper,
            "unit_price": 9.99,
            "currency": "USD"
        }
