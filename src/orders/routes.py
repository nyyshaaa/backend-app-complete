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
from .schema import OrderCreate, OrderDetailResponse
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
    print("entered in add_new_order")
    new_order=orders(amount=order_data["amount"],idempotency_key=i_key,status=orderstatus.INPROGRESS,buyer_id=order_data["buyer_id"])
    session.add(new_order)
    await session.flush()
    await session.refresh(new_order)
    return new_order

async def add_order_items(order_data,new_order,session):
    for item in order_data["order_items"]:
        new_item=orderitems(order_id=new_order.id,frost_id=item["frost_id"], quantity=item["quantity"])
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
async def create_order_with_items(order_input,session,i_key):
   
    existing_order_res=await session.execute(
        select(orders).where(orders.idempotency_key==i_key)
    )
    existing_order=existing_order_res.scalars().first()

    if existing_order:
        order_res=await order_with_details(existing_order.id,session)
        return order_res

    try:
        new_order=await add_new_order(order_input,session,i_key)
        await add_order_items(order_input,new_order,session)
        # await recalc_amount(new_order.id,session) 
        await session.commit()
    except Exception as e :
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    order_details=await order_with_details(new_order.id,session)
    
    return order_details

async def order_with_details(order_id,session):
    stmt=select(orders.id,orders.amount,Frosties.title,Frosties.item_image,Frosties.price,orderitems.quantity,orderitems.frost_id
                ).select_from(orders).where(orders.id==order_id
                ).join(orderitems,orderitems.order_id==orders.id
                ).join(Frosties,Frosties.id==orderitems.frost_id)
    
    result=await session.execute(stmt)
    rows=result.all() 
    # print(rows)
   
    order_id_val = rows[0][0]
    amount_val = rows[0][1]
    items = []
    for row in rows:
        items.append({
            "frost_id": row[6],
            "title": row[2],
            "item_image": row[3],
            "price": float(row[4]), 
            "quantity": row[5],
        })
    response_dict = {
        "order_id": order_id_val,
        "amount": float(amount_val),
        "order_items": items
    }
    return response_dict
    


@orders_router.post("/",response_model=OrderDetailResponse)
async def create_order(
    order_data:OrderCreate,
    jwt_token=Depends(AccessTokenBearer()),
    idempotency_key:str=Depends(get_idempotency_key),
    db_session:AsyncSession=Depends(get_session)):

    token_user_id=jwt_token["user"]["user_id"]
    cur_user=await get_current_user(token_user_id,db_session)
    
    order_data_dict=order_data.model_dump()
    order_data_dict["buyer_id"]=token_user_id
    
    if cur_user:
        new_order=await create_order_with_items(order_data_dict,db_session,idempotency_key)
        return new_order
    


