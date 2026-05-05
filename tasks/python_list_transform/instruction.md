# Python Windmill Script — Filter and Transform a List

## Background

Windmill Python scripts frequently receive lists from upstream flow steps and must filter, transform, and return new lists. This is a core pattern for data-processing pipelines built in Windmill.

## Requirements

- Create a Python script at `/home/user/windmill-project/f/scripts/process_orders.py`.
- The `main` function must have this signature:
  ```python
  def main(orders: list[dict], min_amount: float = 0.0) -> dict:
  ```
  Each order dict has keys: `id` (int), `product` (str), `amount` (float), `shipped` (bool).
- The function must:
  1. Filter orders where `amount >= min_amount`.
  2. Return a dict:
     ```python
     {
       "total_orders": len(filtered),
       "total_amount": sum(o["amount"] for o in filtered),
       "shipped_count": sum(1 for o in filtered if o["shipped"]),
       "items": [{"id": o["id"], "product": o["product"], "amount": o["amount"]} for o in filtered]
     }
     ```
- Create the metadata file at `/home/user/windmill-project/f/scripts/process_orders.script.yaml` with:
  - `summary: "Filter and summarize a list of orders"`
  - `language: python3`

## Constraints

- Project path: `/home/user/windmill-project`
- Return keys must be exactly: `total_orders`, `total_amount`, `shipped_count`, `items`

## Integrations

None.
