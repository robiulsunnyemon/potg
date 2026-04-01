import cloudinary
import cloudinary.uploader
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# Configure cloudinary using settings from .env
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)

async def upload_image_to_cloudinary(file_content: bytes, filename: str) -> str:
    """
    Uploads a file directly to Cloudinary and returns the secure URL.
    """
    try:
        # We process the upload synchronously, but since Cloudinary API 
        # is synchronous we call it. For a pure async app, we could run 
        # this in a threadpool, but for simplicity we rely on standard approach.
        response = cloudinary.uploader.upload(
            file_content,
            folder="potg_profiles",
            public_id=filename.split(".")[0] # Removes extension
        )
        return response.get("secure_url")
    except Exception as e:
        logger.error(f"Error uploading image to Cloudinary: {e}")
        raise ValueError("Failed to upload image. Please check configuration.")
