import logging
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession
from sqlalchemy import text
from src.config import configSettgs

async_engine=create_async_engine(configSettgs.DATABASE_URL,echo=True)
#                                  ,connect_args={"statement_cache_size": 0})
# async_engine=async_engine.execution_options(compiled_cache=None)  # just to check api performance diffs.
async_session=async_sessionmaker(bind=async_engine,class_=AsyncSession,expire_on_commit=False)


async def db_activecheck():
    async with async_engine.connect() as conn:
        stmt=text("SELECT 1 ;")
        res=await conn.execute(stmt)
        print(res.all())
