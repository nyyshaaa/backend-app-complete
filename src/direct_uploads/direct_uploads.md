## Image Upload Benchmarking Documentation

This document summarizes two patterns for handling image uploads in the Cool Things app ("Dreamer"), the comparison plan, and the implementation details for **Pattern A** (Direct → Cloudinary + Webhook).

---

### 1. Patterns Overview

| Pattern                              | Flow Steps                                                                 | Pros | Cons |
| ------------------------------------ | -------------------------------------------------------------------------- | ---- | ---- |
| **A: Direct → Cloudinary + Webhook** | 1. Client requests upload signature from server (`GET /avatar-signature`). |      |      |

2. Client uploads file directly to Cloudinary (`POST https://api.cloudinary.com/v1_1/{cloud}/image/upload`).
3. Cloudinary calls server webhook (`POST /webhook/cloudinary`).
4. Client polls status (`GET /upload-status/{id}`). | - Offloads file bytes to CDN

* Low server bandwidth
* Scales effortlessly
* Pre-signed short-lived credentials | - Requires webhook setup
* Eventual consistency (polling) |
  \| **B: Server → Queue → Cloudinary** | 1. Client POSTs image URL (or file) to server endpoint (`POST /upload-via-server`).

2. Server enqueues background task.
3. Worker downloads/validates/processes image, then calls Cloudinary API.
4. Worker writes URL to store.
5. Client polls status (`GET /upload-status/{id}`). | - Centralized control

* Uniform API interface
* Simpler error handling (no webhook) | - Server ingests file bytes
* Higher bandwidth & CPU load
* Additional task infrastructure |

---

### 2. Benchmark Goals

* Compare end-to-end latency (p50/p90/p99) of Pattern A vs. Pattern B under identical load.
* Measure server resource utilization (CPU, bandwidth).
* Evaluate complexity and operational overhead of each pattern.

---

### 3. Implemented: Pattern A (Direct → Cloudinary + Webhook)

#### 3.1 Configuration

```python
class CloudinarySettings(BaseSettings):
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    CLOUDINARY_CLOUD_NAME: str
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )
cloudinary_config = CloudinarySettings()
```

#### 3.2 Signature Endpoint

```python
@cdn_uploads_router.get(
    "/avatar-signature", response_model=AvatarUploadSignature
)
async def get_avatar_upload_signature(
    jwt_token: dict = Depends(AccessTokenBearer())
):
    user_id = jwt_token["user"]["user_id"]
    folder = f"users/avatars/{user_id}"
    public_id = f"user_{user_id}_avatar"
    eager_transforms = ["c_fill,h_300,w_300"]
    timestamp = int(cloudinary.utils.now())
    params_to_sign = {
        "timestamp": timestamp,
        "folder": folder,
        "public_id": public_id,
        "overwrite": "true",
        "invalidate": "true",
        "eager": ",".join(eager_transforms),
    }
    signature = cloudinary.utils.api_sign_request(
        params_to_sign,
        cloudinary_config.CLOUDINARY_API_SECRET
    )
    return AvatarUploadSignature(
        api_key=cloudinary_config.CLOUDINARY_API_KEY,
        signature=signature,
        timestamp=timestamp,
        upload_url=(
            f"https://api.cloudinary.com/v1_1/"
            f"{cloudinary_config.CLOUDINARY_CLOUD_NAME}/image/upload"
        ),
        folder=folder,
        public_id=public_id,
        overwrite=True,
        invalidate=True,
        eager=eager_transforms
    )
```

#### 3.3 Webhook Handler

```python
@demo_router.post("/webhook/cloudinary")
async def cloudinary_webhook(request: Request):
    form = await request.form()
    payload = dict(form)
    # Validate signature HMAC of payload (excluding 'signature')
    received_sig = payload.get("signature")
    signing_data = "&".join(
        f"{k}={payload[k]}"
        for k in sorted(payload)
        if k != "signature"
    )
    expected_sig = hmac.new(
        cloudinary_config.CLOUDINARY_API_SECRET.encode(),
        signing_data.encode(), hashlib.sha1
    ).hexdigest()
    if not hmac.compare_digest(received_sig, expected_sig):
        raise HTTPException(403, "Invalid webhook signature")
    secure_url = payload.get("secure_url")
    uid = next(upload_counter)
    demo_store[uid] = {"status": "done", "secure_url": secure_url}
    return {"received": True, "upload_id": uid}
```

#### 3.4 Status Endpoint

```python
@demo_router.get("/upload-status/{upload_id}", response_model=UploadStatus)
async def get_upload_status(upload_id: int):
    entry = demo_store.get(upload_id)
    if entry is None:
        return UploadStatus(status="pending")
    return UploadStatus(**entry)
```

---

### 4. Next Steps: Pattern B & Benchmarking

1. Implement `POST /demo/upload-via-server` + background worker.
2. Extend k6 script to include Pattern B.
3. Run comparative load tests and analyze p50/p90/p99 and resource metrics.

---

*Document version: 2025-06-29*
