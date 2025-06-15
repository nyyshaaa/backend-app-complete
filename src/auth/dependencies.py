from fastapi.security import HTTPBearer , http
from fastapi import Request

from src.exceptions import InvalidAccessToken, InvalidRefreshToken, InvalidToken
from .utils import decode_token

class TokenBearer(HTTPBearer):

    def __init__(self,auto_error=True): 

        super().__init__(auto_error=auto_error)

    async def __call__(self, request:Request) -> http.HTTPAuthorizationCredentials|None:
        auth_creds=await super().__call__(request)
        token=auth_creds.credentials

        decoded_token=decode_token(token)

        if not decoded_token:
            raise InvalidToken()
        
        self.check_token_type(decoded_token)

        return decoded_token
    
    def check_token_type(self,decoded_token):
        raise NotImplementedError("To be implemented in child classes")
    
class AccessTokenBearer(TokenBearer):
    def check_token_type(self, dtoken:dict):
        if dtoken and dtoken["refresh"]:
            raise InvalidAccessToken()
        
class RefreshTokenBearer(TokenBearer):
    def check_token_type(self, dtoken:dict):
        if dtoken and not dtoken["refresh"]:
            raise InvalidRefreshToken()

        
