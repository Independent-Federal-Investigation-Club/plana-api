from fastapi import APIRouter, File, HTTPException, Path, UploadFile
from fastapi.responses import JSONResponse
from loguru import logger

from plana.api.utils.s3 import S3

# Initialize router
router = APIRouter()
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/{guild_id}/images")
async def upload_guild_image(
    guild_id: int = Path(..., description="Discord Guild ID"),
    file: UploadFile = File(..., description="Image file to upload"),
) -> JSONResponse:
    """
    Upload an image for a specific guild.

    Args:
        guild_id: The Discord guild ID
        file: Image file (JPG, PNG, GIF, WebP)

    Returns:
        JSON response with image URL and metadata

    Raises:
        HTTPException: For validation errors or upload failures
    """
    # Validate file presence
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    # Validate file size
    if hasattr(file, "size") and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024 * 1024)}MB",
        )

    # Validate content type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        # Upload image and get URL
        image_url = await S3.upload_image(file)

        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "message": "Image uploaded successfully",
                "data": {
                    "url": image_url,
                    "guild_id": str(guild_id),  # Convert snowflake ID to string
                    "filename": file.filename,
                    "content_type": file.content_type,
                },
            },
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in upload endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
