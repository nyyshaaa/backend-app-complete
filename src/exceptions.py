
from collections.abc import Callable
from typing import Any, Type, Union
from fastapi import FastAPI, Request,status
from fastapi.responses import JSONResponse



class FrostiesException(Exception):
    """
    Base for all domain errors:
      - default detail message
      - arbitrary extra attributes
      - subclasses *must* define `status_code` and `detail`
    """
    detail: str
    status_code: int

    def __init__(
        self,
        *,
        detail: str | None = None,
        status_code: int | None = None,
        **kwargs: Any,
    ):
        
        self.detail = detail if detail is not None else getattr(self, "detail")
        self.status_code = status_code if status_code is not None else getattr(self, "status_code")
        # attach extra context fields (e.g., cart_id, user_id)
        for key, value in kwargs.items():
            setattr(self, key, value)


class InvalidAccessToken(FrostiesException):
    detail = "Invalid access token provided."
    status_code = status.HTTP_403_FORBIDDEN

class InvalidRefreshToken(FrostiesException):
    detail = "Invalid refresh token provided."
    status_code = status.HTTP_403_FORBIDDEN

class InvalidToken(FrostiesException):
    detail = "Invalid or expired token provided."
    status_code = status.HTTP_403_FORBIDDEN

class AccountExists(FrostiesException):
    detail = "Account already exists with this email."
    status_code = status.HTTP_409_CONFLICT

class NoAccountExists(FrostiesException):
    detail = "No account exists for this email. Please signup."
    status_code = status.HTTP_404_NOT_FOUND

class IncorrectPassword(FrostiesException):
    detail = "Password is incorrect."
    status_code = status.HTTP_401_UNAUTHORIZED

class ExpiredToken(FrostiesException):
    detail = "Token has expired. Please login again."
    status_code = status.HTTP_401_UNAUTHORIZED

class UserNotFound(FrostiesException):
    detail = "User not found."
    status_code = status.HTTP_404_NOT_FOUND

class FrostyNotFound(FrostiesException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Frost item not found or unauthorized user."
    
    def __init__(self, *, frost_id:int, detail: str | None = None):
        message = detail or f"Frost item with id {frost_id} not found or unauthorized user."
        super().__init__(detail=message, frost_id=frost_id)

class FrostyExists(FrostiesException):
    detail = "Frosty already exists."
    status_code = status.HTTP_409_CONFLICT

# class NotAuthorized(Exception):
#     def ____init__(self,message:str="User Not authorized"):
#         self.message = message
#         self.status_code=status.HTTP_403_FORBIDDEN

# detail_fn can be allowed to accept any Exception as well 
DetailFn = Callable[[FrostiesException], Any]

def create_exception_handler(detail_fn:DetailFn):
    async def exception_handler(request:Request, exc:Exception):   
        if not isinstance(exc, FrostiesException):
            # (should never happen in per‑type registrations)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"message": "Internal server error", "error_type": type(exc).__name__},
            ) 
        try:
            body = detail_fn(exc)     
            code = exc.status_code
        except Exception as e:
            # Something *went wrong in handler code itself*—
            # e.g. `` was missing and got an AttributeError.
            body = {"detail": str(e)}
            code = status.HTTP_500_INTERNAL_SERVER_ERROR
        
        return JSONResponse(status_code=code, content=body)
      
    return exception_handler

# use a different handler for unhandled exceptions as detail_fn is denfined for FrostiesException subclasses
async def fallback_handler(request: Request, exc: Exception):
    
    body = {
        "message": getattr(exc, "detail", "Internal server error"),
        "error_type": type(exc).__name__
    }
    code = getattr(exc, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return JSONResponse(status_code=code, content=body)



def register_exceptions(app: FastAPI):

    mapping : list [tuple[Type[FrostiesException],DetailFn]]=[
        (InvalidAccessToken, lambda exc: {"message": exc.detail}),
        (InvalidRefreshToken, lambda exc: {"message": exc.detail}),
        (InvalidToken, lambda exc: {"message": exc.detail}),
        (AccountExists, lambda exc: {"message": exc.detail}),
        (NoAccountExists, lambda exc: {"message": exc.detail}),
        (IncorrectPassword, lambda exc: {"message": exc.detail}),
        (ExpiredToken, lambda exc: {"message": exc.detail}),
        (UserNotFound, lambda exc: {"message": exc.detail}),
        (FrostyNotFound, lambda exc: {"message": exc.detail, "frost_id": getattr(exc,"frost_id")}),
        (FrostyExists, lambda exc: {"message": exc.detail}),
    ]

    for exc_cls, fn in mapping:
        app.add_exception_handler(
            exc_cls,
            create_exception_handler(detail_fn=fn)
        )

    app.add_exception_handler(
        Exception, # catch all unidentified/unhandled exceptions
        fallback_handler
    )

