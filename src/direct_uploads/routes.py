from fastapi import APIRouter,HTTPException,Depends,status,UploadFile,File
from src.auth.dependencies import AccessTokenBearer
import cloudinary
import cloudinary.utils
from .schema import AvatarUploadSignature

from src.config import cloudinary_config

direct_uploads_router=APIRouter()


@direct_uploads_router.get("/avatar-signature",response_model=AvatarUploadSignature)
async def get_avatar_upload_signature(jwt_token:dict=Depends(AccessTokenBearer())):
    """
    Return the data the client needs to upload directly to Cloudinary.
    """
    user_id=jwt_token["user"]["user_id"]
    

    timestamp = int(cloudinary.utils.now())

    # 1. Decide where & how you want this avatar stored
    folder    = f"users/avatars/{user_id}"
    public_id = f"user_{user_id}_avatar"      # fixed ID for easy overwrite(overwrite even if the avatar exists)

    # 2. On‑upload eager transformations (pre‑generate this size)
    eager_transforms = ["c_fill,h_300,w_300"]

    # 4. Build the exact params we will sign
    params_to_sign = {
        "timestamp": timestamp,
        "folder": folder,
        "public_id": public_id,
        "overwrite": "true",
        "invalidate": "true",
        "eager": ",".join(eager_transforms),
    }

    # sign required set of params
    signature=cloudinary.utils.api_sign_request(
        params_to_sign,
        cloudinary_config.CLOUDINARY_API_SECRET
    )

    return AvatarUploadSignature(
        api_key=cloudinary_config.CLOUDINARY_API_KEY,
        signature=signature,
        timestamp=timestamp,
        upload_url=f"https://api.cloudinary.com/v1_1/{cloudinary_config.CLOUDINARY_CLOUD_NAME}/image/upload",
        folder=folder,
        public_id=public_id,
        overwrite=True,
        invalidate=True,
        eager=eager_transforms
    )
