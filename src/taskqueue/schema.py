from pydantic import BaseModel

class EnqueueResponse(BaseModel):
    upload_id: int

