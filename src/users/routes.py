from fastapi import APIRouter,Depends,status,HTTPException
from sqlalchemy.ext.asyncio import  AsyncSession
from src.db.dependencies import get_session
from src.auth.dependencies import AccessTokenBearer
from src.auth.services import UserService
from src.users.schemas import UserProfileResponse,UserUpdateRequest
from datetime import datetime
from .utils import get_current_user


user_service=UserService()

profile_router=APIRouter()


@profile_router.get("/",response_model=UserProfileResponse)
async def get_my_profile(jwt_token:dict=Depends(AccessTokenBearer()), db_session:AsyncSession=Depends(get_session)):

    token_user_id=jwt_token["user"]["user_id"]
    return await get_current_user(token_user_id,db_session)
   
@profile_router.patch("/")
async def update_user_profile(
    user:UserUpdateRequest,jwt_token:dict=Depends(AccessTokenBearer()),db_session:AsyncSession=Depends(get_session)):
    
    token_user_id=jwt_token["user"]["user_id"]
    old_user=await get_current_user(token_user_id,db_session)

    update_data=user.model_dump(exclude_unset=True) # convert a model to dict & submodels too recursively ,only include fields passed by user

    for field,value in update_data.items():
        setattr(old_user,field,value)

    await db_session.commit()
    await db_session.refresh(old_user)
    return old_user  


@profile_router.delete("/")
async def delete_user(jwt_token:dict=Depends(AccessTokenBearer()),db_session:AsyncSession=Depends(get_session)):
    token_user_id=jwt_token["user"]["user_id"]
    cur_user=await get_current_user(token_user_id,db_session)
    
    #*add password enter check 
    
    cur_user.deleted_at=datetime.now()
    await db_session.commit()
    
    return {"message": "User deleted successfully"}



#**check for roles later