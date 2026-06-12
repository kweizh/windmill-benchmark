# schema_validation
from pydantic import BaseModel

class Order(BaseModel):
    item: str
    quantity: int
    unit_price: float

def main(data: Order):
    if isinstance(data, dict):
        data = Order(**data)
    return {
        "item": data.item,
        "total": data.quantity * data.unit_price
    }
