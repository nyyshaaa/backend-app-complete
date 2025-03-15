from fastapi import APIRouter,Depends,status,HTTPException
from sqlalchemy.ext.asyncio import  AsyncSession
from src.db.dependencies import get_session
from src.auth.dependencies import AccessTokenBearer
from src.auth.services import UserService
from src.users.schemas import UserProfileResponse,UserUpdateRequest
from datetime import datetime

user_service=UserService()

profile_router=APIRouter()

@profile_router.get("/",response_model=UserProfileResponse)
async def get_my_profile(jwt_token:dict=Depends(AccessTokenBearer()), db_session:AsyncSession=Depends(get_session)):
    user_id=jwt_token["user"]["user_id"]
    user=user_service.get_user_details(user_id,db_session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    return user


@profile_router.patch("/")
async def update_user_profile(
    user_update:UserUpdateRequest,jwt_token:dict=Depends(AccessTokenBearer()),db_session:AsyncSession=Depends(get_session)):
    user_id=jwt_token["user"]["user_id"]
    user=user_service.get_user_details(user_id,db_session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    
    update_data=user_update.model_dump(exclude_unset=True) # convert a model ti dict & submodels too recursively ,only include fields passed by user

    for field,value in update_data.items():
        setattr(user,field,value)

    await db_session.commit()
    await db_session.refresh(user)
    return user

@profile_router.delete("/")
async def delete_user(jwt_token:dict=Depends(AccessTokenBearer()),db_session:AsyncSession=Depends(get_session)):
    user_id=jwt_token["user"]["user_id"]
    user=user_service.get_user_details(user_id,db_session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    
    #add password enter check 
    
    user.deleted_at=datetime.now()
    await db_session.commit()
    
    return {"message": "User deleted successfully"}


    





#**check for roles later