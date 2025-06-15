import logging
from fastapi import FastAPI,APIRouter
from contextlib import asynccontextmanager
from src.db.connection import db_activecheck,async_engine,async_session
from src.auth.routes import auth_router
from src.users.routes import profile_router
from src.products.routes import frosties_router
from src.orders.routes import orders_router
from src.payments.routes import webhook_router
from prometheus_fastapi_instrumentator import Instrumentator
from src.exceptions import register_exceptions

version="v1"

description="A REST API for sharing your best interests and frosty things"

version_prefix=f"/api/{version}"

@asynccontextmanager
async def app_lifespan(app:FastAPI):
    
    await db_activecheck()
   
    yield

    await async_engine.dispose()

app=FastAPI(
    title="Dreamer", 
    description=description,
    version=version,
    lifespan=app_lifespan
    )

register_exceptions(app)

app.include_router(auth_router,prefix=f"{version_prefix}/auth",tags=["auth"])
app.include_router(profile_router,prefix=f"{version_prefix}/profile",tags=["profile"])
app.include_router(frosties_router,prefix=f"{version_prefix}/frosties",tags=["frosties"])
app.include_router(orders_router,prefix=f"{version_prefix}/orders",tags=["orders"])
app.include_router(webhook_router,prefix=f"{version_prefix}/webhook",tags=["webhook"])

Instrumentator().instrument(app).expose(app) 



# api endpoints naming clarity,consistency 
# api versioning 
# versioning and communicating version updates,to maintain functionality regardless of updates,this ensures backward compatibility
# paginate large data sets e.g. GET/posts?page=5&pagesize=20 to enhance UX and data delivery
# (like load few posts and show them first and then load and show as scrolled)
# idempotency where necessary
# Robust monitoring and logging,consistent error handling,rate limiting 

