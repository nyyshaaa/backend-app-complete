import time
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy import select, update
from src.auth.dependencies import AccessTokenBearer
from src.db.dependencies import get_session
from sqlalchemy.ext.asyncio import  AsyncSession
from src.exceptions import FrostyExists, FrostyNotFound
from src.products.schemas import FrostyCreateIn, FrostyPatch,FrostyResponseOut
from src.auth.services import UserService
from src.db.schema import Frosties
from datetime import datetime
from .constants import frosties_columns

from src.users.utils import get_current_user, get_current_user_id

frosties_router=APIRouter()
user_service=UserService()

get_endpoint_str="api/v1/frosties/{frost_id}"

async def post_frost_item(frost_item,session):
    try:
        new_frost_item=Frosties(**frost_item) 
        session.add(new_frost_item)
        await session.commit()
        await session.refresh(new_frost_item)
    except IntegrityError:
        await session.rollback()
        raise FrostyExists()  # in real systems based on some i key or any unique key return the product in response similarly as on new insert by using UPSERT+RETURNING to frontend
    return new_frost_item


@frosties_router.post("/",response_model=FrostyResponseOut)
async def create_frosty(payload:FrostyCreateIn,jwt_token=Depends(AccessTokenBearer()),db_session:AsyncSession=Depends(get_session)):

    token_user_id=jwt_token["user"]["user_id"]
    
    frost_item_data = payload.model_dump()
    frost_item_data["user_id"] = token_user_id
    print(frost_item_data)
    result=await post_frost_item(frost_item_data,db_session)
    print("frost_item:",result)
    return result
        
async def get_frost_item(frost_id,user_id,session):
    stmt=select(*frosties_columns).where(Frosties.user_id==user_id,Frosties.id==frost_id)
    # stmt=select(Frosties).where(Frosties.id==frost_id) 
    res=await session.execute(stmt)
    result=res.mappings().first()
    return result

#* Add deleted_at checks for get and patch 
@frosties_router.get("/{frost_id}")
async def get_frosty(frost_id:int,jwt_token:dict=Depends(AccessTokenBearer()),db_session:AsyncSession=Depends(get_session)):
       
    token_user_id=jwt_token["user"]["user_id"]
    
    if token_user_id:
        
        frost_item=await get_frost_item(frost_id,token_user_id,db_session)
        if not frost_item:
            #  raise FrostyNotFound()
             raise FrostyNotFound(frost_id=frost_id)
        return frost_item 
    

async def update_frost_item(frost_id,user_id,new_item,session):
    update_data=new_item.model_dump(exclude_unset=True)

    stmt=update(Frosties
                ).where(Frosties.user_id==user_id,Frosties.id==frost_id
                        ).values(**update_data).returning(*frosties_columns)
    res=await session.execute(stmt)
    await session.commit()
    result=res.mappings().first()
    return result

@frosties_router.patch("/{frost_id}",response_model=FrostyResponseOut)
async def update_frosty(frost_id:int,frost_item:FrostyPatch,jwt_token:dict=Depends(AccessTokenBearer()),db_session:AsyncSession=Depends(get_session)):
    user_id=jwt_token["user"]["user_id"]
   
    updated_item=await update_frost_item(frost_id,user_id,frost_item,db_session)

    if not updated_item:
        raise FrostyNotFound(frost_id=frost_id)
    
    return updated_item  

async def delete_frost_item(frost_id,user_id,session):
    stmt=update(Frosties
                ).where(Frosties.user_id==user_id,Frosties.id==frost_id
                        ).values(deleted_at=datetime.now())
    await session.execute(stmt)
    await session.commit()
    

@frosties_router.delete("/{frost_id}")
async def delete_frosty(frost_id:int,jwt_token:dict=Depends(AccessTokenBearer()),db_session:AsyncSession=Depends(get_session)):
    
    user_id=jwt_token["user"]["user_id"]
    
    await delete_frost_item(frost_id,user_id,db_session)
    return {"message": "Frost item deleted successfully"}




    
