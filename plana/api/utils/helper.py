import os
import traceback

from loguru import logger
from dotenv import load_dotenv

import httpx
from typing import Any, Dict, Optional
from fastapi import HTTPException, status


def validate_environment() -> None:
    """Validate required environment variables"""

    load_dotenv()

    required_vars = [
        "DATABASE_URL",
        "REDIS_URL",
        "PLANA_DB_NAME",
        "PLANA_USER",
        "PLANA_PASSWORD",
        "DISCORD_CLIENT_ID",
        "DISCORD_CLIENT_SECRET",
        "DISCORD_REDIRECT_URI",
        "FRONTEND_REDIRECT_URI",
        "JWT_SECRET",
        "S3_ACCESS_KEY_ID",
        "S3_SECRET_ACCESS_KEY",
        "S3_ENDPOINT_URL",
        "S3_BUCKET_NAME",
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.error(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )


async def make_request(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Make HTTP request with proper error handling"""
    try:
        logger.info(f"Making {method} request to {url}.")

        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, headers=headers, data=data)
            response_data = response.json()

            if response.status_code not in [200, 201]:
                error_msg = response_data.get(
                    "error_description", "Unknown Discord API error"
                )
                logger.error(
                    f"Discord API error: {response.status_code} - {error_msg} - {response_data}"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Discord API request failed: {error_msg}",
                )
            return response_data
    except httpx.RequestError as e:
        logger.error(f"Network error during Discord API request: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to connect to Discord API",
        )


def _handle_database_error(operation: str, error: Exception) -> HTTPException:
    """Handle database errors consistently across endpoints."""
    logger.error(f"Error {operation}: {error}, Traceback: {traceback.format_exc()}")
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Failed to {operation}",
    )


def ids_string_to_int(**kwargs) -> tuple | int:
    """Validate and convert string IDs to integers."""
    result = []

    for key, value in kwargs.items():
        if value is None:
            result.append(None)
            continue

        try:
            result.append(int(value))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid format for {key}: '{value}'. Must be an integer.",
            )

    if len(result) == 1:
        return result[0]

    return tuple(result)
