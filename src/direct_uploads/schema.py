from pydantic import BaseModel


class AvatarUploadSignature(BaseModel):
    api_key: str
    signature: str
    timestamp: int
    upload_url: str
    folder: str
    public_id: str
    overwrite: bool
    invalidate: bool
    eager: list[str]

class UploadStatus(BaseModel):
    status: str
    secure_url: str | None = None