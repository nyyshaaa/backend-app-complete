from celery import Celery
from PIL import Image
import os,cloudinary.uploader as cloudinary_uploader

from src.taskqueue.constants import images_store

def process_and_upload(upload_id,image_bytes,filename,user_id):

    try:
        result=cloudinary_uploader.upload(
            image_bytes,
            public_id=f"user_{user_id}_avatar",
            folder=f"users/avatars/{user_id}",
            overwrite=True,
            invalidate=True,
            eager=["c_fill,h_300,w_300"]
        )
        secure_url=result["secure_url"]

        images_store[upload_id]["status"]="completed"
        images_store[upload_id]["secure_url"]=secure_url
    
    except Exception as e:
        #*log error
        images_store[upload_id]["status"]="error"

    
    