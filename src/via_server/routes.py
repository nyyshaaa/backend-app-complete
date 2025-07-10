import random
from fastapi import APIRouter,HTTPException,Depends,status,UploadFile,File,BackgroundTasks
from src.auth.dependencies import AccessTokenBearer
import itertools,uuid
import cloudinary.uploader as cloudinary_uploader
from src.via_server.schema import EnqueueResponse,UploadStatus
# from .utils import process_and_upload

from .constants import images_store


server_uploads_router=APIRouter()


upload_counter=itertools.count(1)



@server_uploads_router.post("/")
async def upload_via_server(background_tasks:BackgroundTasks,file:UploadFile=File(...)):
    
    #1. Generate upload id
    upload_id=next(upload_counter)

    user_id=random.randint(1, 20)

    
    result= cloudinary_uploader.upload(
            file.file,
            public_id=f"user_{user_id}_avatar_{upload_id}",
            folder=f"users_taskqueue/avatars/{user_id}",
            invalidate=True,
            overwrite=True,
            eager=["c_fill,h_300,w_300"]
        )   
    # return {"url": result["secure_url"]}  
    # background_tasks.add_task(
    #     process_and_upload,
    #     upload_id,
    #     read_file,
    #     file.filename,
    #     user_id
    # )

    # return EnqueueResponse(upload_id=upload_id)


@server_uploads_router.get("/upload-status/{upload_id}", response_model=UploadStatus)
async def get_upload_status(upload_id: int):
    """
    Poll this to check if the background task has finished uploading.
    """
    entry = images_store.get(upload_id)
    if not entry:
        return UploadStatus(status="pending")
    return UploadStatus(**entry)






    