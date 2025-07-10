from celery import Celery
import cloudinary.uploader as cloudinary_uploader

from src.via_server.constants import images_store

# async def process_and_upload(upload_id,image_bytes,filename,user_id):

#     try:
#         result=await cloudinary_uploader.upload(
#             image_bytes,
#             public_id=f"user_{user_id}_avatar_{upload_id}",
#             folder=f"users_taskqueue/avatars/{user_id}",
#             invalidate=True,
#             overwrite=True,
#             eager=["c_fill,h_300,w_300"]
#         )
#         secure_url=result["secure_url"]

#         images_store[upload_id]["status"]="completed"
#         images_store[upload_id]["secure_url"]=secure_url
    
#     except Exception as e:
#         #*log error
#         images_store[upload_id]["status"]="error"
    
    