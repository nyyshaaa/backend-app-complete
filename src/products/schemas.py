from pydantic import BaseModel, ConfigDict,Field
from typing import Union,Optional
from datetime import datetime
from decimal import Decimal


class FrostyCreateIn(BaseModel):
   
    title:str=Field(...,min_length=8) 
    description:Optional[str]=None
    item_image:Optional[str]=None
    qty:int=Field(default=1,ge=1)
    price:Optional[Decimal]=None

class FrostyResponseOut(BaseModel):

    id: int
    user_id: int 
    title: str
    description: Optional[str]=None
    # item_image: str  
    qty: int
    created_at: datetime
    updated_at: Optional[datetime]=None
    price: Optional[Decimal]=None

class FrostyPatch(BaseModel):
    
    title:Optional[str]=Field(...,min_length=8)
    description:Optional[str]=None
    item_image:Optional[str]=None
    qty:Optional[int]=Field(None,ge=1)
    price:Optional[Decimal]=None

    model_config = ConfigDict(extra='forbid')

  