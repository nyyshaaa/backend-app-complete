from fastapi import APIRouter,HTTPException,Depends,status
from .schemas import UserCreateInput,UserCreateResponse,LoginUser
from .services import UserService
from sqlalchemy.ext.asyncio import  AsyncSession
from src.db.dependencies import get_session
from .utils import verify_password,create_token,decode_token,REFRESH_TOKEN_EXPIRE_DAYS
from datetime import timedelta,datetime
from .dependencies import RefreshTokenBearer

auth_router=APIRouter()
 
user_service = UserService()

@auth_router.post('/signup',response_model=UserCreateResponse)
async def create_user_account(user_payload:UserCreateInput,db_session:AsyncSession=Depends(get_session)):

    email=user_payload.email

    try:
        user_exists=await user_service.get_user_id_email(email,db_session)
        # print("user_exists",user_exists)

        if user_exists:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Account already exists with this email")
        
        new_user=await user_service.create_user(user_payload,db_session)
        return new_user
    except HTTPException as e:
        raise e
    except Exception as e :
        raise e
    #*this try ecxept block feels redundant check once 
    

@auth_router.post('/login')
async def login_user(login_payload:LoginUser,db_session:AsyncSession=Depends(get_session)):
    user=await user_service.get_user_identity(login_payload.email,db_session)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="No account exists for this email")
    
    is_pass_valid=verify_password(login_payload.password,user.password_hash)
    print(login_payload.password)

    if not is_pass_valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Password is incorrect")
    
    access_token=create_token(user_identity={'email':user.email,'user_id':user.id})
    refresh_token=create_token(user_identity=
                                       {'email':user.email,'user_id':user.id},
                                       expires_time=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
                                       refresh=True)
    
    return {"message":"Login successful","access_token":access_token,"refresh_token":refresh_token,"user":{'email':user.email,'user_id':user.id}}
    #**change the return response

@auth_router.get("/refresh")
async def refresh_new_token(jwt_token:dict=Depends(RefreshTokenBearer())):
    expiry=jwt_token["exp"]
    if datetime.fromtimestamp(expiry)>datetime.now():
        new_token=create_token(user_identity=jwt_token["user"])
        return {"access_token":new_token}
    
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,details="Expired Token")
