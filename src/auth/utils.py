from passlib.context import CryptContext
from datetime import datetime,timedelta
from src.config import configSettgs
import uuid,jwt,logging

paswd_context=CryptContext(schemes=['bcrypt'],deprecated=["auto"])

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

def gen_pass_hash(password:str)->str:
    hashed=paswd_context.hash(password)
    return hashed

def verify_password(password:str,hash:str)->str:
    return paswd_context.verify(password,hash)

def create_token(user_identity:dict,expires_time:timedelta=None,refresh:bool=False):
    payload={}
    expiry=datetime.now() + (expires_time or timedelta(seconds=ACCESS_TOKEN_EXPIRE_MINUTES))

    payload["user"]=user_identity
    payload["exp"]=expiry
    payload["jti"]=str(uuid.uuid4())
    payload["refresh"]=refresh

    token=jwt.encode(payload=payload,key=configSettgs.JWT_SECRET,algorithm=configSettgs.JWT_ALGORITHM)
    return token

def decode_token(token:str):
    """To verify the signature , expiration and user claims of token"""
    try:
        token_data=jwt.decode(
        jwt=token,
        key=configSettgs.JWT_SECRET,
        algorithms=configSettgs.JWT_ALGORITHM
        )
        return token_data
    except jwt.PyJWTError as e:
        logging.exception(e)
        return None