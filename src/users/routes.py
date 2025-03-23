from fastapi import APIRouter,Depends,status,HTTPException
from sqlalchemy.ext.asyncio import  AsyncSession
from src.db.dependencies import get_session
from src.auth.dependencies import AccessTokenBearer
from src.auth.services import UserService
from src.users.schemas import UserProfileResponse,UserUpdateRequest
from datetime import datetime

user_service=UserService()

profile_router=APIRouter()

#**check for routes names and reformat 
#check to modify get_user_details by email , which is more safe by user.id or user.email 
@profile_router.get("/",response_model=UserProfileResponse)
async def get_my_profile(jwt_token:dict=Depends(AccessTokenBearer()), db_session:AsyncSession=Depends(get_session)):
    user_id=jwt_token["user"]["user_id"]
    user=user_service.get_user_details(user_id,db_session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    return user


@profile_router.patch("/{user_id}")
async def update_user_profile(
    user_id:int,user:UserUpdateRequest,jwt_token:dict=Depends(AccessTokenBearer()),db_session:AsyncSession=Depends(get_session)):

    user=jwt_token["user"]
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    
    if not user["id"]==user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update another user.")
    
    old_user=await user_service.get_user_details(user_id,db_session)
    
    update_data=user.model_dump(exclude_unset=True) # convert a model ti dict & submodels too recursively ,only include fields passed by user

    for field,value in update_data.items():
        setattr(old_user,field,value)

    await db_session.commit()
    await db_session.refresh(old_user)
    return old_user  


@profile_router.delete("/{user_id}")
async def delete_user(user_id:int,jwt_token:dict=Depends(AccessTokenBearer()),db_session:AsyncSession=Depends(get_session)):
    user_id=jwt_token["user"]["user_id"]
    user=user_service.get_user_details(user_id,db_session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    
    if not user["id"]==user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update another user.")
    
    #*add password enter check 
    
    user.deleted_at=datetime.now()
    await db_session.commit()
    
    return {"message": "User deleted successfully"}


    





#**check for roles later