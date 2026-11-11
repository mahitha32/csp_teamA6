"""
app/services/image_service.py
Cloudinary image upload/delete for complaint & resolution photos.
Village Complaint Redressal System - Vemavaram Village

Firebase is NOT used for image storage — Cloudinary is used instead.
Firebase Admin SDK is kept only for Phone Auth token verification (mobile app).
"""

import uuid
from flask import current_app


def _get_cloudinary():
    """Lazily configure and return the cloudinary module."""
    try:
        import cloudinary
        import cloudinary.uploader
    except ImportError:
        raise RuntimeError(
            "cloudinary package is not installed. Run:  pip install cloudinary"
        )
    cloudinary.config(
        cloud_name=current_app.config.get("CLOUDINARY_CLOUD_NAME", ""),
        api_key=current_app.config.get("CLOUDINARY_API_KEY", ""),
        api_secret=current_app.config.get("CLOUDINARY_API_SECRET", ""),
    )
    return cloudinary


def upload_image(file_bytes: bytes, original_filename: str, folder: str = "complaints") -> str:
    """
    Upload image bytes to Cloudinary under the vemavaram_csp/<folder>/ path.
    Returns the HTTPS secure URL.
    If Cloudinary credentials are not configured in .env, falls back to local static storage.

    folders used:
      - 'complaints'   : citizen complaint evidence photos
      - 'resolutions'  : worker post-resolution proof photos
    """
    ext = original_filename.rsplit(".", 1)[-1].lower() if "." in original_filename else "jpg"
    allowed = {"jpg", "jpeg", "png", "gif", "webp", "heic"}
    if ext not in allowed:
        raise ValueError(f"Unsupported image format: {ext}. Allowed: {', '.join(allowed)}")

    cloud_name = current_app.config.get("CLOUDINARY_CLOUD_NAME", "").strip()
    api_key    = current_app.config.get("CLOUDINARY_API_KEY", "").strip()

    # Fallback to local static storage if Cloudinary keys not configured in local environment
    if not cloud_name or not api_key:
        import os
        upload_dir = os.path.join(current_app.root_path, "static", "uploads", folder)
        os.makedirs(upload_dir, exist_ok=True)
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(upload_dir, unique_name)
        with open(filepath, "wb") as f:
            f.write(file_bytes)
        return f"/static/uploads/{folder}/{unique_name}"

    cld = _get_cloudinary()
    public_id = f"vemavaram_csp/{folder}/{uuid.uuid4().hex}"

    result = cld.uploader.upload(
        file_bytes,
        public_id=public_id,
        resource_type="image",
        format=ext,
        overwrite=True,
    )
    return result["secure_url"]


def delete_image(url: str) -> bool:
    """
    Delete an image from Cloudinary or local static fallback by its URL.
    Returns True on success, False on failure (non-fatal).
    """
    if not url:
        return False

    cloud_name = current_app.config.get("CLOUDINARY_CLOUD_NAME", "").strip()
    if not cloud_name or "/static/uploads/" in url:
        try:
            import os
            rel = url.lstrip("/").replace("static/", "")
            full = os.path.join(current_app.root_path, "static", rel)
            if os.path.exists(full):
                os.remove(full)
            return True
        except Exception as e:
            current_app.logger.warning(f"[Storage] Could not delete local file: {e}")
            return False

    try:
        cld = _get_cloudinary()
        part = url.split("/upload/")[-1]
        if part.startswith("v") and "/" in part:
            part = part.split("/", 1)[1]
        public_id = part.rsplit(".", 1)[0]
        cld.uploader.destroy(public_id, resource_type="image")
        return True
    except Exception as e:
        current_app.logger.warning(f"[Cloudinary] Could not delete image: {e}")
        return False

