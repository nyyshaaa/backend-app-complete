from fastapi.security import HTTPBearer , http
from fastapi import Request,HTTPException,status
from .utils import decode_token

class TokenBearer(HTTPBearer):
    def __init__(self,auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request:Request) -> http.HTTPAuthorizationCredentials|None:
        auth_creds=await super().__call__(request)
        token=auth_creds.credentials

        decoded_token=decode_token(token)

        if not decoded_token:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Invalid or expired token")
        
        self.check_token_type(decoded_token)

        return decoded_token
    
    def check_token_type(self,decoded_token): 
        raise NotImplementedError("To be implemented in child classes")
    

class AccessTokenBearer(TokenBearer):
    def check_token_type(self, dtoken:dict):
        if dtoken and dtoken["refresh"]:
            raise HTTPException(status_code=400,detail="Please provide valid access token")
        
class RefreshTokenBearer(TokenBearer):
    def check_token_type(self, dtoken:dict):
        if dtoken and not dtoken["refresh"]:
            raise HTTPException(status_code=400,detail="Please provide valid refresh token")

        
