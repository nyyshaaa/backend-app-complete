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

class OrderResponse(BaseModel):
    pass
    

class OrderUpdate(BaseModel):
    pass