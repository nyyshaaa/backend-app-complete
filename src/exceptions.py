from fastapi import FastAPI,status

class InvalidAccessToken(Exception):
    def init__(self, message:str="Invalid access token provided."):
        self.message = message
        self.status_code=status.HTTP_403_FORBIDDEN

class InvalidRefreshToken(Exception):
    def init__(self, message:str="Invalid refresh token provided."):
        self.message = message
        self.status_code=status.HTTP_403_FORBIDDEN

class InvalidToken(Exception):
    def init__(self, message:str="Invalid or expired token provided."):
        self.message = message
        self.status_code=status.HTTP_403_FORBIDDEN

class AccountExists():
    def __init__(self,message:str="Account already exists with this email."):
        self.message = message
        self.status_code=status.HTTP_409_CONFLICT

class NoAccountExists(Exception):
    def __init__(self,message:str="No account exists for this email."):
        self.message = message
        self.status_code=status.HTTP_404_NOT_FOUND   #* 401 OR 404

class IncorrectPassword(Exception):
    def __init__(self,message:str="Password is incorrect"):
        self.message = message
        self.status_code=status.HTTP_401_UNAUTHORIZED

class ExpiredToken(Exception):
    def __init__(self, message: str = "Token has expired. Please login again."):
        self.message = message
        self.status_code = status.HTTP_401_UNAUTHORIZED

class UserNotFound(Exception):
    def __init__(self, message: str = "User not found"):
        self.message = message
        self.status_code = status.HTTP_404_NOT_FOUND

class FrostyNotFound(Exception):
    def __init__(self, frost_id: int,message:str="Frost item not found or unautorized user."):
        self.status_code=status.HTTP_404_NOT_FOUND
        self.message=f"Frost item with id {frost_id} not found or unautorized user."

# class NotAuthorized(Exception):
#     def __init__(self,message:str="User Not authorized"):
#         self.message = message
#         self.status_code=status.HTTP_403_FORBIDDEN

def register_exceptions(app: FastAPI):
   
    pass