import httpx
import base64
import logging
import asyncio
from app.core.config import settings

logger = logging.getLogger(__name__)

MUX_BASE_URL = "https://api.mux.com/video/v1"

def _get_auth_header() -> dict:
    auth_str = f"{settings.MUX_TOKEN_ID}:{settings.MUX_TOKEN_SECRET}"
    encoded_auth = base64.b64encode(auth_str.encode()).decode()
    return {"Authorization": f"Basic {encoded_auth}"}

async def upload_video_to_mux(file_content: bytes) -> dict:
    """
    Uploads a video to Mux using the Direct Upload API.
    Returns a dict with asset_id and playback_id.
    """
    async with httpx.AsyncClient(timeout=600.0) as client:
        # 1. Create a Direct Upload
        try:
            upload_response = await client.post(
                f"{MUX_BASE_URL}/uploads",
                headers=_get_auth_header(),
                json={
                    "new_asset_settings": {
                        "playback_policy": ["public"]
                    },
                    "cors_origin": "*"
                }
            )
            upload_response.raise_for_status()
            upload_data = upload_response.json()["data"]
            upload_url = upload_data["url"]
            upload_id = upload_data["id"]
            
            # 2. PUT the file content to the signed URL
            put_response = await client.put(upload_url, content=file_content)
            put_response.raise_for_status()
            
            # 3. Poll for Asset ID (Since we want to be synchronous for simplicity)
            # In production, use Webhooks instead.
            asset_id = None
            playback_id = None
            
            for _ in range(10): # Try for 10 seconds
                await asyncio.sleep(1)
                status_response = await client.get(
                    f"{MUX_BASE_URL}/uploads/{upload_id}",
                    headers=_get_auth_header()
                )
                status_data = status_response.json()["data"]
                if status_data.get("asset_id"):
                    asset_id = status_data["asset_id"]
                    break
            
            if not asset_id:
                raise ValueError("Mux upload completed but Asset ID not found yet.")
                
            # 4. Get Playback ID from Asset
            asset_response = await client.get(
                f"{MUX_BASE_URL}/assets/{asset_id}",
                headers=_get_auth_header()
            )
            asset_data = asset_response.json()["data"]
            
            if asset_data.get("playback_ids"):
                playback_id = asset_data["playback_ids"][0]["id"]
            
            return {
                "asset_id": asset_id,
                "playback_id": playback_id,
                "duration": asset_data.get("duration", 0)
            }
            
        except Exception as e:
            logger.error(f"Mux upload error: {e}")
            raise ValueError(f"Failed to upload video to Mux: {str(e)}")
