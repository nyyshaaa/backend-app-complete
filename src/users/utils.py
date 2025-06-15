from fastapi import HTTPException,status
from src.auth.services import UserService
from src.exceptions import NotAuthorized, UserNotFound

user_service=UserService()



async def get_current_user(token_user_id,session):
    user=await user_service.get_user_details(token_user_id,session)
    if not user:
        raise UserNotFound()
    return user


async def get_current_user_id(token_user_id,session):
    """ returns: (id,) or None or raises error"""
    user_id=await user_service.get_user_id(token_user_id,session)
    print(user_id)
    if not user_id:
        raise UserNotFound()
    return user_id

# async def authorize_current_user(user_id,token_user_id,session):
#     cur_user=await get_current_user(token_user_id,session)

#     if not cur_user["id"]!=user_id:
#         raise NotAuthorized()
#     return cur_user