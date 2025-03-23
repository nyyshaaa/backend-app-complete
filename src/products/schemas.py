from pydantic import BaseModel,Field
from typing import Union,Optional
from datetime import datetime
from decimal import Decimal


class FrostyCreateIn(BaseModel):
   
    user_id:int 
    title:str=Field(...,min_length=8)  #* ... check syntax
    description:Optional[str]=None
    item_image:Optional[str]=None
    qty:int=Field(default=1,ge=1)
    price:Optional[Decimal]=None

class FrostyResponseOut(BaseModel):
    id: int
    user_id: int 
    title: str
    description: Optional[str]
    item_image: str
    qty: int
    created_at: datetime
    updated_at: Optional[datetime]
    price: Optional[Decimal]

class FrostyPatch(BaseModel):
    
    title:str=Field(...,min_length=8)
    description:Optional[str]=None
    item_image:Optional[str]=None
    qty:int=Field(default=1,ge=1)
    price:Optional[Decimal]=None

  