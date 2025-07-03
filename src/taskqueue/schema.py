from pydantic import BaseModel

class EnqueueResponse(BaseModel):
    upload_id: int

class UploadStatus(BaseModel):
    status: str
    secure_url: str | None = None