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
from src.db.schema import orders,orderstatus,orderitems,Frosties
from src.orders.utils import fetch_order
from src.users.utils import get_current_user
from src.orders.utils import get_idempotency_key
from sqlalchemy import func, select
from stripe._error import SignatureVerificationError
from src.orders.routes import orders_router
from src.db.dependencies import get_session_factory

import stripe
from src.config import configSettgs

stripe.api_key=configSettgs.STRIPE_TEST_SECRET_KEY
WEBHOOK_SECRET=configSettgs.WEBHOOK_SECRET


user_service=UserService()

webhook_router=APIRouter()  

async def process_payment_simulation(order, i_key: str, attempt: int = 1, max_attempts: int = 3) -> dict:
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
    

#for pay first case there will be no order_id ,so checks will be done based on order and pay status plus i_key 
async def process_payment_background(order_id: int, idempotency_key: str, session_factory):
    # Wait for a short delay to simulate payment processing
    async with session_factory() as session:
        await asyncio.sleep(3)
        order=await fetch_order(order_id,session)

        if not order:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Bad request.")
        
        # use in memory caches to store results by i_key , some request specificity of order , and response .
        if order.payment_status=="completed" and order.status==orderstatus.COMPLETED:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Payment already done!")
        elif order.payment_status=="failed" and order.status==orderstatus.failed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Payment failed.")
        
        
        payment_result = await process_payment_simulation(order, idempotency_key)
        if payment_result["success"]:
             order.status = orderstatus.COMPLETED
             order.payment_transaction_id = payment_result["transaction_id"]
             order.payment_status = "completed"
        else:
            order.status = orderstatus.failed
            order.payment_status = "failed"
        try:
            await session.commit()
        except Exception as e:
            await session.rollback()


# --- PAY NOW (COD CASE AFTER ORDER HAS BEEN PLACED SUCCESSFULLY)
@orders_router.post("/{order_id}/pay")
async def pay_later_payment(
    order_id: int, background_tasks:BackgroundTasks,idempotency_key: str=Depends(get_idempotency_key),
    jwt_token=Depends(AccessTokenBearer()), session_factory: AsyncSession=Depends(get_session_factory)):
    
    token_user_id=jwt_token["user"]["user_id"]
    async with session_factory() as session:
        cur_user=await get_current_user(token_user_id,session)  #* in case of error what will authorize return check again 
    
    if cur_user:
        # Trigger asynchronous payment processin via a background task.
        background_tasks.add_task(process_payment_background, order_id, idempotency_key, session_factory)
        return {"message": "Payment processing initiated for order"}

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
            order.delivered_at=datetime.now() 
            try:
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise HTTPException(status_code=500, detail=str(e))


# -----Webhook endpoint for payment updates-----
@webhook_router.post("/stripe")
async def payment_webhook(request: Request, db_session: AsyncSession = Depends(get_session), stripe_signature: str = Header(None)):
    """
    Handle Stripe webhook events.
    Verifies if the signature is from stripe.
    
    Expected payload:
    {
      "order_id": <order_id>,
      "status": "completed" or "failed",
      "transaction_id": <stripe_transaction_id>
    }
    """
    payload=await request.body()
    try:
        event=stripe.Webhook.construct_event(payload,stripe_signature,configSettgs.WEBHOOK_SECRET)
    except ValueError:
        # Invalid payload
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload")
    except SignatureVerificationError:
        # Invalid signature
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")
    
    
    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]
        print(f"Payment succeeded for PaymentIntent {intent['id']}")
        await update_payment_status(intent,db_session,success=True)
    elif event["type"] == "payment_intent.payment_failed":
        intent = event["data"]["object"]
        print(f"Payment failed for PaymentIntent {intent['id']}") 
        await update_payment_status(intent,db_session,success=False) 
    
    return JSONResponse(content={"status": "success"})
    