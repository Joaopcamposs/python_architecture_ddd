from datetime import date
from typing import Optional

from pydantic import BaseModel


class CreateAllocation(BaseModel):
    orderid: str
    sku: str
    qty: int


class CreateBatch(BaseModel):
    ref: str
    sku: str
    qty: int
    eta: Optional[date]
