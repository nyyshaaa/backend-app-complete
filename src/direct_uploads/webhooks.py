from fastapi import Depends, Request, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import cloudinary.utils
import hmac
import hashlib
import itertools
from src.auth.dependencies import AccessTokenBearer
from src.config import cloudinary_config  # the Pydantic settings
from src.direct_uploads.routes import direct_uploads_router

demo_store = {}                    # upload_id → {"status": "...", "secure_url": "..."}
upload_counter = itertools.count(1)


# not actually using this file for now . as benchmarking is done to test upload flow.


@direct_uploads_router.post("/webhook/cloudinary")
async def cloudinary_webhook(request: Request):
    """
    Cloudinary will POST here after a successful upload.
    We validate the signature to ensure authenticity, then store the result.
    """
    form = await request.form()
    payload = dict(form)

    # 1) Signature validation
    #    Cloudinary signs webhook payload by creating an HMAC of all params except 'signature'
    received_sig = payload.get("signature")
    if not received_sig:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing signature")

    # build the string to sign: sorted "<k>=<v>&<k>=<v>..."
    signing_data = "&".join(
        f"{k}={payload[k]}" for k in sorted(payload) if k != "signature"
    )
    expected_sig = hmac.new(
        cloudinary_config.CLOUDINARY_API_SECRET.encode("utf-8"),
        signing_data.encode("utf-8"),
        hashlib.sha1
    ).hexdigest()

    print(f"received_sig type: {type(received_sig)}, value: {received_sig}")
    print(f"expected_sig type: {type(expected_sig)}, value: {expected_sig}")

    if not hmac.compare_digest(received_sig, expected_sig):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid webhook signature")

    # 2) Store the secure_url under a new upload_id
    secure_url = payload.get("secure_url")
    if not secure_url:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No secure_url in payload")
    
    public_id = payload.get("public_id")
    if not public_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="No public_id in payload"
        )

    uid = next(upload_counter)
    demo_store[uid] = {"status": "done", "secure_url": secure_url}

    return JSONResponse({"received": True, "upload_id": uid})



