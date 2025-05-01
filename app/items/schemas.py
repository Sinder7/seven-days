from pydantic import BaseModel


class ItemSchema(BaseModel):
    name: str
    articule: str
    price: float
    quantity: int