from fastapi import FastAPI, Request,status
from fastapi.responses import JSONResponse

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

class FrostyExists(Exception):
    def __init__(self, message:str="Product already exists"):
        self.status_code=status.HTTP_409_CONFLICT
        self.message=message

# class NotAuthorized(Exception):
#     def __init__(self,message:str="User Not authorized"):
#         self.message = message
#         self.status_code=status.HTTP_403_FORBIDDEN

def create_exception_handler(detail_fn):
    async def exception_handler(request:Request, exc:Exception):
        try:
            body = detail_fn(exc)     
            code = exc.status_code or detail_fn(exc).get("status_code", status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception:
            # Something *went wrong in your handler code itself*—
            # e.g. `` was missing and you got an AttributeError.
            body = {"message": str(exc)}
            code = status.HTTP_500_INTERNAL_SERVER_ERROR

        return JSONResponse(status_code=code, content=body)
      
    return exception_handler

def register_exceptions(app: FastAPI):

    app.add_exception_handler(
        InvalidAccessToken, 
        create_exception_handler(detail_fn=lambda exc: {"message": exc.message})   
    )

    app.add_exception_handler(
        InvalidRefreshToken, 
        create_exception_handler(detail_fn=lambda exc: {"message": exc.message})   
    )

    app.add_exception_handler(
        InvalidToken, 
        create_exception_handler(detail_fn=lambda exc: {"message": exc.message})                                    
    )

    app.add_exception_handler(
        AccountExists, 
        create_exception_handler(detail_fn=lambda exc: {"message": exc.message})                                  
    )

    app.add_exception_handler(
        NoAccountExists, 
        create_exception_handler(detail_fn=lambda exc: {"message": exc.message})                                        
    )

    app.add_exception_handler(
        IncorrectPassword, 
        create_exception_handler(detail_fn=lambda exc: {"message": exc.message})       
    )

    app.add_exception_handler(
        ExpiredToken, 
        create_exception_handler(detail_fn=lambda exc: {"message": exc.message})   
    )

    app.add_exception_handler(
        UserNotFound, 
        create_exception_handler(detail_fn=lambda exc: {"message": exc.message})                                       
    )
    
    app.add_exception_handler(
        FrostyNotFound, 
        create_exception_handler(detail_fn=lambda exc: {"message": exc.message})   
    )

    app.add_exception_handler(
        FrostyExists, 
        create_exception_handler(detail_fn=lambda exc: {"message": exc.message})   
    )

    app.add_exception_handler(
        500, # catch all unidentified/unhandled exceptions
        create_exception_handler(
            detail_fn=lambda exc: {
                "message": getattr(exc, "detail", "Internal server error"),
                "error_type": type(exc).__name__,
                "status_code": getattr(exc, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR),
            }
        )
    )

   
    

