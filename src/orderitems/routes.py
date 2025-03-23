from fastapi import APIRouter,Depends,HTTPException,status
from src.auth.services import UserService
from src.auth.services import UserService
from src.db.dependencies import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.dependencies import AccessTokenBearer
from src.db.schema import orderitems
from sqlalchemy import select
from .schema import OrderItemResponse,OrderItemCreate,OrderItemUpdate
from typing import List


orderitems_router=APIRouter()
user_service=UserService()

async def add_order_item(item_data,session):
    new_item = orderitems(**item_data.dict())
    session.add(new_item)
    try:
        await session.commit()
        await session.refresh(new_item)
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@orderitems_router.post("/", response_model=OrderItemResponse)
async def create_order_item(
    item_data: OrderItemCreate,jwt_token:dict=Depends(AccessTokenBearer()),db_session: AsyncSession = Depends(get_session)):
    new_item=await add_order_item(item_data,db_session)
    return new_item

async def fetch_item(item_id,session):
    stmt = select(orderitems).where(orderitems.id == item_id)
    res = await session.execute(stmt)
    item_obj = res.scalars().first()
    return item_obj

@orderitems_router.get("/{order_item_id}", response_model=OrderItemResponse)
async def get_order_item(
    order_item_id: int,jwt_token:dict=Depends(AccessTokenBearer()),db_session: AsyncSession = Depends(get_session)):
    token_email=jwt_token["user"]["email"]
    user=await user_service.get_user_id_email(token_email,db_session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    item_obj=await fetch_item(order_item_id,db_session)

    if not item_obj:
        raise HTTPException(status_code=404, detail="Order item not found")
    
    return item_obj

#to be only updated via admin 
# @orderitems_router.patch("/{order_item_id}", response_model=OrderItemResponse)
# async def update_order_item(
#     order_item_id: int,item_update: OrderItemUpdate,jwt_token:dict=Depends(AccessTokenBearer()),db_session: AsyncSession = Depends(get_session)):
    
#     stmt = select(orderitems).where(orderitems.id == order_item_id)
#     res = await db_session.execute(stmt)
#     item_obj = res.scalars().first()
#     if not item_obj:
#         raise HTTPException(status_code=404, detail="Order item not found")
    
#     update_data = item_update.dict(exclude_unset=True)
#     for field, value in update_data.items():
#         setattr(item_obj, field, value)
#     try:
#         await db_session.commit()
#         await db_session.refresh(item_obj)
#     except Exception as e:
#         await db_session.rollback()
#         raise HTTPException(status_code=500, detail=str(e))
#     return item_obj



