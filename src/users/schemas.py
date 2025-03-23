from pydantic import BaseModel,Field
from typing import Union,Optional
from datetime import datetime


class UserProfileResponse(BaseModel):
    id:int     #**int or bigint?
    name:str
    about:str
    email:str
    avatar:str
    created_at:datetime

class UserUpdateRequest(BaseModel):
    name:str
    about:str
    email:str
    avatar:str