from typing import Optional
from fastapi import Header,HTTPException,status
from sqlalchemy import func, select

from src.db.schema import Frosties, orderitems, orders

def get_idempotency_key(idempotency_key:Optional[str]=Header(...))->str:
    if idempotency_key is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='Cannot initiate request ')   #*check better way to handle this error
    return idempotency_key


async def fetch_order(order_id,session):
    stmt=select(orders).where(orders.id==order_id)
    res=await session.execute(stmt)
    return res.scalars.first()

async def recalc_amount(order_id,session):
    stmt=select(func.sum(Frosties.price*orderitems.quantity)).join(
        Frosties,Frosties.id==orderitems.frost_id).where(orderitems.order_id==order_id)  #* check if we  can directly return the added order_items view
    result=await session.execute(stmt)
    total_amount=result.scalar() or 0
    return total_amount