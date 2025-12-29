"""
Simplified authentication types and constants.

Following the Zen of Python: Simple is better than complex.
"""

import os
from enum import Enum
from typing import Optional, Set

from fastapi import HTTPException, status


class AuthType(Enum):
    """Authentication method"""

    USER = "user"  # JWT authenticated Discord user
    BOT = "bot"  # API key authenticated bot


class AuthConstants:
    """Authentication constants and configuration"""

    # Headers
    API_KEY_HEADER = "Plana-API-Key"

    # Bot configuration
    BOT_USER_ID = "plana_bot"
    BOT_USERNAME = "Plana Bot"

    # Discord permissions
    ADMIN_PERMISSION = 0x00000008

    # Load API keys once at startup
    API_KEYS: Set[str] = {
        key.strip() for key in os.getenv("PLANA_API_KEYS", "").split(",") if key.strip()
    }

    UNAUTHORIZED_MESSAGE = "Unauthorized: Access is denied due to invalid credentials."
    FORBIDDEN_MESSAGE = "Forbidden: You do not have permission to access this resource."

    # Common exceptions
    UNAUTHORIZED = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=UNAUTHORIZED_MESSAGE,
    )

    FORBIDDEN = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=FORBIDDEN_MESSAGE,
    )


class AuthData:

    def __init__(
        self,
        auth_type: AuthType,
        user_id: str,
        username: str,
        avatar: Optional[str] = None,
        discord_token: Optional[str] = None,
        iat: Optional[int] = None,
        exp: Optional[int] = None,
    ):
        self.auth_type = auth_type
        self.user_id = user_id
        self.username = username
        self.avatar = avatar
        self.discord_token = discord_token
        self.iat = iat
        self.exp = exp

    def __repr__(self):
        return f"AuthInfo(type={self.auth_type.value}, user={self.username})"
