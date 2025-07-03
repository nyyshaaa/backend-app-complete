import itertools
import random
from fastapi import APIRouter,HTTPException,Depends,status,UploadFile,File
from src.auth.dependencies import AccessTokenBearer
import cloudinary
import cloudinary.utils
from .schema import AvatarUploadSignature
from .constants import images_store_direct

from src.config import cloudinary_config

direct_uploads_router=APIRouter()

upload_counter=itertools.count(1)

@direct_uploads_router.get("/avatar-signature",response_model=AvatarUploadSignature)
async def get_avatar_upload_signature():
    """
    Return the data the client needs to upload directly to Cloudinary.
    """
    # user_id=jwt_token["user"]["user_id"]

    upload_id = next(upload_counter)

    user_id=random.randint(1, 20)  # For demonstration purposes, replace with actual user ID retrieval logic
    

    timestamp = int(cloudinary.utils.now())

    # 1. Decide where & how you want this avatar stored
    folder    = f"users_direct/avatars/{user_id}"
    public_id = f"user_{user_id}_avatar_{upload_id}"      # fixed ID for easy overwrite(overwrite even if the avatar exists)

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
        upload_id=upload_id,
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
