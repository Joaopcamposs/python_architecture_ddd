from pydantic import BaseModel


class CreateAllocation(BaseModel):
    orderid: str
    sku: str
    qty: int
