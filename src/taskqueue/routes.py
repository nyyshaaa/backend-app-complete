from fastapi import APIRouter,HTTPException,Depends,status,UploadFile,File
from src.auth.dependencies import AccessTokenBearer
import uuid , shutil
from .utils import process_image_task


upload_router=APIRouter()

@upload_router.post("/image")
async def upload_image(file:UploadFile=File(...),jwt_token:dict=Depends(AccessTokenBearer())):
    user_id=jwt_token["user"]["user_id"]
    print(user_id)
    temp_filename=f"/tmp/{uuid.uuid4()}_{file.filename}" #To ensure uniqueness across file names attach uuid.

    with open(temp_filename,"wb") as buffer:
        shutil.cop(file.file,buffer)

    #Enqueue background task : pass temp file path and user_id
    process_image_task.delay(temp_filename,user_id)
    return {"status":"processing","message":"Your image is being processed."}





    