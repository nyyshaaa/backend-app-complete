from datetime import datetime
import asyncio,uuid
from typing import List
from fastapi import APIRouter , Depends ,HTTPException,status,BackgroundTasks,Request,Header
from fastapi.responses import JSONResponse
import stripe.error
from src.auth.services import UserService
from src.db.dependencies import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.dependencies import AccessTokenBearer
from src.users.utils import get_current_user
from .schema import OrderCreate,OrderResponse,OrderUpdate
from src.db.schema import orders,orderstatus,orderitems,Frosties
from .utils import fetch_order, get_idempotency_key
from sqlalchemy import func, select
from stripe._error import SignatureVerificationError

import stripe
from src.config import configSettgs

stripe.api_key=configSettgs.STRIPE_TEST_SECRET_KEY
WEBHOOK_SECRET=configSettgs.WEBHOOK_SECRET


orders_router=APIRouter()
user_service=UserService()
webhook_router=APIRouter()  


async def add_new_order(order_data,session,i_key):
    new_order=orders(amount=order_data.amount,idempotency_key=i_key,status=orderstatus.INPROGRESS)
    session.add(new_order)
    await session.flush()
    await session.refresh(new_order)
    return new_order

async def add_order_items(order_data,new_order,session):
    for item in order_data.order_items:
        new_item=orderitems(order_id=new_order.id,frost_id=item.frost_id, quantity=item.quantity)
        session.add(new_item)
    await session.flush()

# async def recalc_amount(order_id,session):
#     stmt=select(func.sum(Frosties.price*orderitems.quantity)).join(
#         Frosties,Frosties.id==orderitems.frost_id).where(orderitems.order_id==order_id)  #* check if we  can directly return the added order_items view
#     result=await session.execute(stmt)
#     total_amount=result.scalar() or 0

#     update_stmt=orders.update().where(orders.id==order_id).values(amount=total_amount)
#     await session.execute(update_stmt)

#* check the orm optimisation for joins
async def create_order_with_items(order_data,session,i_key):

    existing_order_res=await session.execute(
        select(orders).where(orders.idempotency_key==i_key)
    )
    existing_order=existing_order_res.scalars().first()

    if existing_order:
        order_data=await order_with_details(existing_order.id,session)
        return order_data

    try:
        new_order=await add_new_order(order_data,session,i_key)
        await add_order_items(order_data,new_order,session)
        # await recalc_amount(new_order.id,session) 
        await session.commit()
    except Exception as e :
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    order_details=await order_with_details(new_order.id,session)
    
    return order_details

async def order_with_details(order_id,session):
    stmt=select(orders.id,orders.amount,Frosties.title,Frosties.item_image,Frosties.price,orderitems.quantity).where(orders.id==order_id).join(
        orderitems,orderitems.order_id==order_id).join(
        Frosties,Frosties.id==orderitems.frost_id)
    
    result=await session.execute(stmt)
    order_with_details=result.all()  #* cnage the response format later 
    print(order_with_details)
    return order_with_details


@orders_router.post("/")
async def create_order(
    order_data:OrderCreate,
    jwt_token=Depends(AccessTokenBearer()),
    idempotency_key:str=Depends(get_idempotency_key),
    db_session:AsyncSession=Depends(get_session)):

    token_user_id=jwt_token["user"]["user_id"]
    cur_user=await get_current_user(token_user_id,db_session)
    
    if cur_user:
        new_order=await create_order_with_items(order_data,db_session,idempotency_key)
        return new_order
    


# async def patch_order(order_update,old_order,session):
#     update_data = order_update.dict(exclude_unset=True)
#     for field, value in update_data.items():
#         setattr(old_order, field, value)
#     try:
#         await session.commit()
#         await session.refresh(old_order)
#     except Exception as e:
#         await session.rollback()
#         raise HTTPException(status_code=500, detail=str(e))
    
# for admins 
# @orders_router.patch("/{order_id}")
# async def update_order(
#     order_id:int,order_update:OrderUpdate,jwt_token:dict=Depends(AccessTokenBearer()),db_session:AsyncSession=Depends(get_session())):
#     token_email=jwt_token["user"]["email"]
#     user=await user_service.get_user_id_email(token_email,db_session)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    
#     old_order=await fetch_order(order_id,db_session)

#     if not old_order:
#         raise HTTPException(status_code=404, detail="Order not found")
    
#     await patch_order(order_update,old_order,db_session)

#     return old_order


# async def cancel_patch(user,order_id,session):
#     order=fetch_order(order_id,session)

#     if not order or order.buyer_id!= user["id"]:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Order not found ")
    
#     if order.status!=orderstatus.INPROGRESS:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order cannot be cancelled")
#     order.status=orderstatus.cancelled

#     #* initiate paymnet refund

#     try:
#         await session.commit()
#         await session.refresh(order)
#     except Exception as e:
#         await session.rollback()
#         raise HTTPException(status_code=500, detail=str(e))
#     return order
    

# @orders_router.patch("/{order_id}/cancel",response_model=OrderResponse)
# async def cancel_order(order_id:int,
#                        jwt_token:dict=Depends(AccessTokenBearer()),
#                        db_session:AsyncSession=Depends(get_session())):
    
#     token_email=jwt_token["user"]["email"]
#     user=await user_service.get_user_id_email(token_email,db_session)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    
#     await cancel_patch(user,order_id,db_session)

# def refund_patch(order):
#     try:
#         refund=stripe.Refund.create(payment_intent=order.payment_transaction_id)
#         order.refund_transaction_id=refund.id
#         order.refund_status=orderstatus.refunded
#         order.status=orderstatus.refunded
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    

# async def return_patch(user,order_id,session):
#     order=fetch_order(order_id,session)

#     if not order or order.buyer_id!= user["id"]:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Order not found ")
    
#     #return only available after it has been completed/delievered
#     #* add delivery date check 
#     if order.status==orderstatus.COMPLETED:
#         order.status=orderstatus.returned
#         refund_patch(order)
#         order.status=orderstatus.refunded

#     try:
#         await session.commit()
#         await session.refresh(order)
#     except Exception as e:
#         await session.rollback()
#         raise HTTPException(status_code=500, detail=str(e))
#     return order


# @orders_router.patch("/{order_id}/return", response_model=OrderResponse)
# async def return_order(order_id: int,
#                        jwt_token:dict=Depends(AccessTokenBearer()),
#                        db_session: AsyncSession = Depends(get_session)):
    
#     token_email=jwt_token["user"]["email"]
#     user=await user_service.get_user_id_email(token_email,db_session)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    
#     await return_patch(user,order_id,db_session)


# @orders_router.get("/{order_id}",response_model=OrderResponse)
# async def get_order(order_id:int,jwt_token:dict=Depends(AccessTokenBearer()),db_session:AsyncSession=Depends(get_session())):
#     token_email=jwt_token["user"]["email"]
#     user=await user_service.get_user_id_email(token_email,db_session)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    
#     order=await fetch_order(order_id,db_session)
#     if not order:
#         raise HTTPException(status_code=404, detail="Order not found")
#     return order

# async def fetch_orders(user,session):
#     stmt=select(orders).where(orders.buyer_id==user["id"])
#     res=await session.execute(stmt)
#     return res.scalars().all()



# @orders_router.get("/",response_model=List[OrderResponse])
# async def get_orders(jwt_token:dict=Depends(AccessTokenBearer()),db_session:AsyncSession=Depends(get_session())):
#     token_email=jwt_token["user"]["email"]
#     user=await user_service.get_user_id_email(token_email,db_session)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    
#     orders_list=await fetch_orders(user,db_session)

#     return orders_list



