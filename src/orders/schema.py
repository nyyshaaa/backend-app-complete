from pydantic import BaseModel,Field
from typing import Union,Optional,List
from datetime import datetime
from decimal import Decimal

class OrderItemCreate(BaseModel):
    frost_id:int
    quantity:int
    price:float #*check if numeric to float is correct ?

class OrderCreate(BaseModel):
    amount:float=Field(...,gt=0)
    order_items:List[OrderItemCreate]


class OrderItemDetail(BaseModel):
    frost_id: int
    title: str
    item_image: str
    price: float
    quantity: int

class OrderDetailResponse(BaseModel):
    order_id: int
    amount: float
    order_items: List[OrderItemDetail]