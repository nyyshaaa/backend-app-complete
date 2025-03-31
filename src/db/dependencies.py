from .connection import async_session
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import  AsyncSession

async def get_session() -> AsyncGenerator[AsyncSession,None]:
    async with async_session() as session:  
        yield session

async def get_session_factory() :
    yield async_session