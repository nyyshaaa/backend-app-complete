from fastapi import HTTPException,status
from src.auth.services import UserService

user_service=UserService()


async def get_current_user(token_user_id,session):
    user=await user_service.get_user_details(token_user_id,session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    return user



async def authorize_current_user(user_id,token_user_id,session):
    cur_user=await get_current_user(token_user_id,session)

    if not cur_user["id"]!=user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized ")
    return cur_user