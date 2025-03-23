from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy import select
from src.auth.dependencies import AccessTokenBearer
from src.db.dependencies import get_session
from sqlalchemy.ext.asyncio import  AsyncSession
from src.products.schemas import FrostyCreateIn,FrostyResponseOut
from src.auth.services import UserService
from src.db.schema import Frosties
from datetime import datetime

frosties_router=APIRouter()
user_service=UserService()

# best way to return responses with efficiency 

async def post_frost_item(frost_item,session):
    new_frost_item=Frosties(**frost_item.dict()) 
    session.add(new_frost_item)
    await session.commit()
    await session.refresh(new_frost_item)
    return new_frost_item

@frosties_router.post("/",response_model=FrostyResponseOut)
async def create_frosty(frostyPayload:FrostyCreateIn,jwt_token:dict=Depends(AccessTokenBearer()),db_session:AsyncSession=Depends(get_session)):
    token_email=jwt_token["user"]["email"]
    user=await user_service.get_user_id_email(token_email,db_session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    
    result=await post_frost_item(frostyPayload,db_session)
    return result

async def get_frost_item(frost_id,session):
    stmt=select(Frosties).where(Frosties.id==frost_id) 
    res=await session.execute(stmt)
    return res.scalars().first()       # *best way to return that it's compatible with proper orm updates if any ,like state sync ?

    

@frosties_router.get("/{frost_id}")
async def get_frosty(frost_id:int,jwt_token:dict=Depends(AccessTokenBearer()),db_session:AsyncSession=Depends(get_session)):
       #is token valid , check if user exists , if item exists and if yes then get and return it 
    token_email=jwt_token["user"]["email"]
    user=user_service.get_user_id_email(token_email,db_session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found.")
    
    frost_item=await get_frost_item(frost_id,db_session)
    if not frost_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No frost item exists with this id.")
    return frost_item

async def get_frost_item2():
    pass

async def update_frost_item(old_item,new_item,session):
    update_data=new_item.model_dump(exclude_unset=True)

    for field,value in update_data.items():
        setattr(old_item,field,value)

    await session.commit()
    await session.refresh(old_item)


@frosties_router.patch("/{frost_id}")
async def update_frosty(frost_id:int,frost_item:dict,jwt_token:dict=Depends(AccessTokenBearer()),db_session:AsyncSession=Depends(get_session)):
    token_email=jwt_token["user"]["email"]
    user=await user_service.get_user_id_email(token_email,db_session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found.")
    
    old_frost_item=await get_frost_item(frost_id,db_session) 

    if not old_frost_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Frost item not found.")
    
    if old_frost_item.user_id != user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this item.")
    
    
    await update_frost_item(old_frost_item,frost_item,db_session)
    return old_frost_item  # * convert to dict  in schema automatically while returning 

@frosties_router.delete("/{frost_id}")
async def delete_frosty(frost_id:int,jwt_token:dict=Depends(AccessTokenBearer()),db_session:AsyncSession=Depends(get_session)):
    token_email=jwt_token["user"]["email"]
    user=user_service.get_user_id_email(token_email,db_session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found.")
    
    frost_item=await get_frost_item(frost_id,db_session)
    if not frost_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No frost item exists with this id.")
    
    if frost_item.user_id != user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this item.")
    
    frost_item.deleted_at=datetime.now()
    await db_session.commit()
    
    return {"message": "Frost item deleted successfully"}
    
