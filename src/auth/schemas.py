from pydantic import BaseModel,Field
from typing import Union,Optional
from datetime import datetime



class UserCreateModel(BaseModel):
    """For input validation after receiving from client and before sending to server"""
    username:Union[str,None]=None
    email:str
    password:str=Field(min_length=7)

    #modify it to include avatars and check for their uploading and processing 

class UserResponseModel(BaseModel):
    id:int
    name:str
    email:str
    created_at:datetime
    deleted_at:Optional[datetime]=None
    updated_at:datetime

class LoginUserModel(BaseModel):
    email:str
    password:str