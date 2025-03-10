from .connection import async_session
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import  AsyncSession

async def get_session() -> AsyncGenerator[AsyncSession,None]:
    # async_session=app.state.async_session
    async with async_session() as session:  
        yield session