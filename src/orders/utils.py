from typing import Optional
from fastapi import Header,HTTPException,status

def get_idempotency_key(idempotency_key:Optional[str]=Header(...))->str:
    if idempotency_key is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='Cannot initiate request ')   #*check better way to handle this error
    return idempotency_key
