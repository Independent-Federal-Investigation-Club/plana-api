import os
import uuid
from typing import Final, Set

import aioboto3
from botocore.exceptions import ClientError
from fastapi import HTTPException, UploadFile
from loguru import logger
from pydantic import BaseModel, Field

# Supported image formats
ALLOWED_EXTENSIONS: Final[Set[str]] = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


class S3Settings(BaseModel):
    """S3 Configuration settings loaded from environment."""

    access_key: str = Field(default_factory=lambda: os.getenv("S3_ACCESS_KEY_ID", ""))
    secret_key: str = Field(
        default_factory=lambda: os.getenv("S3_SECRET_ACCESS_KEY", "")
    )
    endpoint: str = Field(default_factory=lambda: os.getenv("S3_ENDPOINT_URL", ""))
    bucket: str = Field(default_factory=lambda: os.getenv("S3_BUCKET_NAME", ""))
    region: str = Field(default_factory=lambda: os.getenv("S3_REGION", "us-east-1"))
    use_ssl: bool = Field(
        default_factory=lambda: os.getenv("S3_USE_SSL", "true").lower() == "true"
    )

    @property
    def base_url(self) -> str:
        """Returns the base URL for public access."""
        protocol = "https" if self.use_ssl else "http"
        # Clean endpoint by removing existing protocol and trailing slashes
        clean_endpoint = (
            self.endpoint.replace("http://", "").replace("https://", "").rstrip("/")
        )
        return f"{protocol}://{clean_endpoint}/{self.bucket}"


class ImageUploadService:
    """
    Service for managing image uploads to S3-compatible storage.

    Adheres to Zen of Python:
    - 'Simple is better than complex'
    - 'Explicit is better than implicit'
    """

    def __init__(self, settings: S3Settings):
        self.settings = settings
        self._session = aioboto3.Session(
            aws_access_key_id=settings.access_key,
            aws_secret_access_key=settings.secret_key,
            region_name=settings.region,
        )

    async def upload_image(self, file: UploadFile) -> str:
        """
        Uploads an image to S3 and returns its public URL.

        Args:
            file: The uploaded file from FastAPI.

        Returns:
            The public URL of the uploaded image.

        Raises:
            HTTPException: For validation or storage errors.
        """
        extension = self._validate_and_get_extension(file.filename)
        object_key = f"{uuid.uuid4()}{extension}"

        try:
            async with self._session.client(
                "s3", endpoint_url=self.settings.endpoint, use_ssl=self.settings.use_ssl
            ) as s3:
                await s3.upload_fileobj(
                    file.file,
                    self.settings.bucket,
                    object_key,
                    ExtraArgs={
                        "ContentType": file.content_type,
                        "ACL": "public-read",
                    },
                )

                return f"{self.settings.base_url}/{object_key}"

        except ClientError as e:
            logger.error(f"S3 ClientError during upload: {e}")
            raise HTTPException(status_code=500, detail="Storage service error")
        except Exception as e:
            logger.error(f"Unexpected error during image upload: {e}")
            raise HTTPException(status_code=500, detail="Internal upload error")

    def _validate_and_get_extension(self, filename: str | None) -> str:
        """Extracts and validates the file extension."""
        if not filename:
            raise HTTPException(status_code=400, detail="Filename is missing")

        ext = os.path.splitext(filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type '{ext}'. Allowed: {allowed}",
            )
        return ext


# Initialize singleton instance
_settings = S3Settings()
S3 = ImageUploadService(_settings)
