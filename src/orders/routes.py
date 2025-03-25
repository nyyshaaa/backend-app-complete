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
from .schema import OrderCreate,OrderResponse,OrderUpdate
from src.db.schema import orders,orderstatus,orderitems,Frosties
from .utils import get_idempotency_key
from sqlalchemy import func, select
from stripe._error import SignatureVerificationError

import stripe
from src.config import configSettgs

stripe.api_key=configSettgs.STRIPE_TEST_SECRET_KEY
WEBHOOK_SECRET=configSettgs.WEBHOOK_SECRET


orders_router=APIRouter()
user_service=UserService()
webhook_router=APIRouter()  

async def process_payment_simulation(order: orders, i_key: str, attempt: int = 1, max_attempts: int = 3) -> dict:
    """
    Create a PaymentIntent in Stripe in test mode.
    Stripe expects the amount in cents.
    """
    try:
        await asyncio.sleep(2)  # Simulate network delay
        amount_cents = int(float(order.amount) * 42)  # 1RS = 42 cents
        intent=stripe.PaymentIntent.create(amount=amount_cents,currency="usd",metadata={"order_id": order.id},idempotency_key=i_key)
        # For a real integration, return intent.client_secret for client-side confirmation.
        return {"success": True, "transaction_id": intent.id}
    except Exception as e:
        if attempt < max_attempts:
            await asyncio.sleep(2 ** attempt)
            return await process_payment_simulation(order, i_key, attempt + 1, max_attempts)
        else:
            return {"success": False}
    


async def process_payment_background(order_id: int, idempotency_key: str, session: AsyncSession):
    # Wait for a short delay to simulate payment processing
    await asyncio.sleep(3)
    order=fetch_order(order_id,session)

    if not order:
        return
    payment_result = await process_payment_simulation(order, idempotency_key)
    if payment_result["success"]:
        order.status = orderstatus.COMPLETED
        order.payment_transaction_id = payment_result["transaction_id"]
        order.payment_status = "INPROGRESS"
    else:
        order.status = orderstatus.failed
        order.payment_status = "failed"
    try:
        await session.commit()
    except Exception as e:
        await session.rollback()

async def add_new_order(order_data,session,i_key):

    existing_order_res=await session.execute(
        select(orders).where(orders.idempotency_key==i_key)
    )
    existing_order=existing_order_res.scalars().first()

    if existing_order:
        return existing_order

    new_order=orders(amount=order_data.amount,idempotency_key=i_key)
    session.add(new_order)
    try:
        await session.commit()
        session.refresh(new_order)
    except Exception as e :
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    return new_order

async def add_order_items(order_data,new_order,session):
    for item in order_data.order_items:
        new_item=orderitems(order_id=new_order.id,frost_id=item.frost_id, quantity=item.quantity)
        session.add(new_item)
    
    try:
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
async def recalc_amount(order_id,session):
    stmt=select(func.sum(Frosties.price*orderitems.quantity)).join(
        Frosties,Frosties.id==orderitems.frost_id).where(orderitems.order_id==order_id)  #* check if we  can directly return the added order_items view
    result=await session.execute(stmt)
    total_amount=result.scalar()

    update_stmt=orders.update().where(orders.id==order_id).values(amount=total_amount)
    await session.execute(update_stmt)
    await session.commit() 
    


#*check background taaks
@orders_router.post("/")
async def create_order_with_payment(
    order_data:OrderCreate,
    background_tasks=BackgroundTasks,
    jwt_token:dict=Depends(AccessTokenBearer()),
    idempotency_key:str=Depends(get_idempotency_key),
    db_session:AsyncSession=Depends(get_session)):

    token_email=jwt_token["user"]["email"]
    user=await user_service.get_user_id_email(token_email,db_session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    
    new_order=await add_new_order(order_data,db_session,idempotency_key)
    await add_order_items(order_data,new_order,db_session)
    await recalc_amount(new_order.id,db_session)
    # Trigger asynchronous payment processin via a background task.
    background_tasks.add_task(process_payment_background, new_order.id, idempotency_key, db_session)
    return new_order

async def fetch_order(order_id,session):
    stmt=select(orders).where(orders.id==order_id)
    res=await session.execute(stmt)
    return res.scalars.first()


    

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


async def cancel_patch(user,order_id,session):
    order=fetch_order(order_id,session)

    if not order or order.buyer_id!= user["id"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Order not found ")
    
    if order.status!=orderstatus.INPROGRESS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order cannot be cancelled")
    order.status=orderstatus.cancelled

    #* initiate paymnet refund

    try:
        await session.commit()
        await session.refresh(order)
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    return order
    

@orders_router.patch("/{order_id}/cancel",response_model=OrderResponse)
async def cancel_order(order_id:int,
                       jwt_token:dict=Depends(AccessTokenBearer()),
                       db_session:AsyncSession=Depends(get_session())):
    
    token_email=jwt_token["user"]["email"]
    user=await user_service.get_user_id_email(token_email,db_session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    
    await cancel_patch(user,order_id,db_session)

def refund_patch(order):
    try:
        refund=stripe.Refund.create(payment_intent=order.payment_transaction_id)
        order.refund_transaction_id=refund.id
        order.refund_status=orderstatus.refunded
        order.status=orderstatus.refunded
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    

async def return_patch(user,order_id,session):
    order=fetch_order(order_id,session)

    if not order or order.buyer_id!= user["id"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Order not found ")
    
    #return only available after it has been completed/delievered
    #* add delivery date check 
    if order.status==orderstatus.COMPLETED:
        order.status=orderstatus.returned
        refund_patch(order)
        order.status=orderstatus.refunded

    try:
        await session.commit()
        await session.refresh(order)
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    return order


@orders_router.patch("/{order_id}/return", response_model=OrderResponse)
async def return_order(order_id: int,
                       jwt_token:dict=Depends(AccessTokenBearer()),
                       db_session: AsyncSession = Depends(get_session)):
    
    token_email=jwt_token["user"]["email"]
    user=await user_service.get_user_id_email(token_email,db_session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    
    await return_patch(user,order_id,db_session)


@orders_router.get("/{order_id}",response_model=OrderResponse)
async def get_order(order_id:int,jwt_token:dict=Depends(AccessTokenBearer()),db_session:AsyncSession=Depends(get_session())):
    token_email=jwt_token["user"]["email"]
    user=await user_service.get_user_id_email(token_email,db_session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    
    order=await fetch_order(order_id,db_session)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

async def fetch_orders(user,session):
    stmt=select(orders).where(orders.buyer_id==user["id"])
    res=await session.execute(stmt)
    return res.scalars().all()



@orders_router.get("/",response_model=List[OrderResponse])
async def get_orders(jwt_token:dict=Depends(AccessTokenBearer()),db_session:AsyncSession=Depends(get_session())):
    token_email=jwt_token["user"]["email"]
    user=await user_service.get_user_id_email(token_email,db_session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    
    orders_list=await fetch_orders(user,db_session)

    return orders_list

async def update_payment_status(intent,session,success):
    order_id = intent.get("metadata",{}).get("order_id")
    if order_id:
        stmt = select(orders).where(orders.id == int(order_id))
        result = await session.execute(stmt)
        order = result.scalars().first()
        if order:
            order.status = orderstatus.COMPLETED if success else orderstatus.failed
            order.payment_transaction_id = intent["id"]
            order.payment_status = "completed" if success else "failed"
            order.delivered_at=datetime.now()  #* check syntax 
            try:
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise HTTPException(status_code=500, detail=str(e))

# -----Webhook endpoint for payment updates-----
# @webhook_router.post("/webhook/stripe")
# async def payment_webhook(request: Request, db_session: AsyncSession = Depends(get_session), stripe_signature: str = Header(None)):
#     """
#     Handle Stripe webhook events.
#     Verifies if the signature is from stripe.
    
#     Expected payload:
#     {
#       "order_id": <order_id>,
#       "status": "completed" or "failed",
#       "transaction_id": <stripe_transaction_id>
#     }
#     """
#     payload=await request.body()
#     try:
#         event=stripe.Webhook.construct_event(payload,stripe_signature,configSettgs.WEBHOOK_SECRET)
#     except ValueError:
#         # Invalid payload
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload")
#     except SignatureVerificationError:
#         # Invalid signature
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")
    
    
#     if event["type"] == "payment_intent.succeeded":
#         intent = event["data"]["object"]
#         print(f"Payment succeeded for PaymentIntent {intent['id']}")
#         update_payment_status(intent,db_session,success=True)
#     elif event["type"] == "payment_intent.payment_failed":
#         intent = event["data"]["object"]
#         print(f"Payment failed for PaymentIntent {intent['id']}") 
#         update_payment_status(intent,db_session,success=False) 
    
#     return JSONResponse(content={"status": "success"})
    