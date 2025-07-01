from fastapi import APIRouter,HTTPException,Depends,status,UploadFile,File,BackgroundTasks
from src.auth.dependencies import AccessTokenBearer
import itertools,uuid

from src.taskqueue.schema import EnqueueResponse 
from .utils import process_and_upload

from .constants import images_store


queue_uploads_router=APIRouter()


upload_counter=itertools.count(1)



@queue_uploads_router.post("/",response_model=EnqueueResponse)
async def upload_via_server(background_tasks:BackgroundTasks,file:UploadFile=File(...),jwt_token:dict=Depends(AccessTokenBearer())):
    user_id=jwt_token["user"]["user_id"]
    
    #1. Generate upload id
    upload_id=next(upload_counter)
 
    #2. Update status in db to pending and secure url as None
    images_store[upload_id]={"status":"pending","secure_url":None}

    #3. Read bytes and enqueue task to process image
    read_file=await file.read()
    background_tasks.add_task(
        process_and_upload,
        upload_id,
        read_file,
        file.filename,
        user_id
    )

    return EnqueueResponse(upload_id=upload_id)





    