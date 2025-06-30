from pydantic import BaseModel,Field
from typing import Union,Optional
from datetime import datetime


class UserProfileResponse(BaseModel):
    id:int    
    name:str
    about:Optional[str]=None
    email:str
    avatar:str
    created_at:datetime

class UserPublicResponse(BaseModel):
    id:int    
    name:str
    email:str
    about:Optional[str]=None
    avatar:str

class UserUpdateRequest(BaseModel):
    name:str
    about:Optional[str]=None
    email:str
    avatar:str