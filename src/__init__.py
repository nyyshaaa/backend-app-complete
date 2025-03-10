from fastapi import FastAPI,APIRouter
from contextlib import asynccontextmanager
from src.db.connection import db_activecheck,async_engine,async_session
from src.auth.routes import auth_router

version="v1"

description="A REST API for sharing your best interests and frosty things"

version_prefix=f"/api/{version}"

@asynccontextmanager
async def app_lifespan(app:FastAPI):
    
    await db_activecheck()
    # app.state.engine=async_engine
    # app.state.session=async_session  

    yield

    await async_engine.dispose()


app=FastAPI(
    title="Dreamer",
    description=description,
    version=version,
    lifespan=app_lifespan
    )

app.include_router(auth_router,prefix=f"{version_prefix}/auth",tags=["auth"])



# api endpoints naming clarity,consistency 
# api versioning ?
# versioning and communicating version updates,to maintain functionality regardless of updates,this ensures backward compatibility
# paginate large data sets e.g. GET/posts?page=5&pagesize=20 to enhance UX and data delivery
# (like load few posts and show them first and then load and show as scrolled)
# idempotency where necessary
# Robust monitoring and logging,consistent error handling,rate limiting 

