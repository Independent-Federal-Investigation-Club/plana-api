"""
Simple and secure authentication middleware.

Handles two auth methods:
1. JWT tokens for Discord users (for auth routes only)
2. API keys for bots (for all routes)

Follows the Zen of Python: Simple is better than complex.
"""

import re
from typing import Optional, Set

from fastapi import Request, status
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from plana.api.auth.oauth import discord_oauth
from plana.api.middleware.types import AuthConstants, AuthData, AuthType


class AuthMiddleware(BaseHTTPMiddleware):
    """Simple authentication middleware"""

    # Routes that don't require authentication
    PUBLIC_ROUTES: Set[str] = {
        "/",
        "/health",
        "/docs",
        "/redoc",
        "/favicon.ico",
        "/openapi.json",
        "/api/auth/url",
        "/api/auth/invite",
        "/api/auth/callback",
    }

    # Pattern to extract guild ID from URLs like /api/guilds/123456/...
    GUILD_ID_PATTERN = re.compile(r"/api/guilds/(\d+)/")

    async def dispatch(self, request: Request, call_next):
        """Process authentication for incoming requests"""

        # Allow OPTIONS for CORS
        if request.method == "OPTIONS":
            return await call_next(request)

        # Skip auth for public routes
        if self._is_public_route(request.url.path):
            return await call_next(request)

        try:
            # Authenticate request
            auth_info = await self._authenticate(request)

            # Set simple auth state
            request.state.auth = auth_info
            request.state.guild_id = self._extract_guild_id(request)

            logger.debug(f"Auth success: {auth_info}")

        except Exception as e:
            logger.warning(f"Auth failed for {request.url.path}: {e}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": str(e)}
            )

        return await call_next(request)

    async def _authenticate(self, request: Request) -> AuthData:
        """Authenticate request and return auth info"""

        # Check for API key first (bots)
        api_key = request.headers.get(AuthConstants.API_KEY_HEADER)
        if api_key:
            if api_key not in AuthConstants.API_KEYS:
                raise Exception("Invalid API key")

            return AuthData(
                auth_type=AuthType.BOT,
                user_id=AuthConstants.BOT_USER_ID,
                username=AuthConstants.BOT_USERNAME,
            )

        # Check for JWT token (Discord users)
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
            if not token:
                raise Exception("Empty token")

            # Verify JWT
            jwt_data = discord_oauth.verify_jwt_token(token)

            return AuthData(
                auth_type=AuthType.USER,
                user_id=jwt_data["user_id"],
                username=jwt_data["username"],
                avatar=jwt_data.get("avatar"),
                discord_token=jwt_data["discord_access_token"],
                iat=jwt_data.get("iat"),
                exp=jwt_data.get("exp"),
            )

        # No valid auth method found
        raise Exception("Authentication required")

    def _is_public_route(self, path: str) -> bool:
        """Check if route is public"""
        if path in self.PUBLIC_ROUTES:
            return True

        # Check for sub-paths of public routes (except root)
        return any(
            path.startswith(f"{route}/") for route in self.PUBLIC_ROUTES if route != "/"
        )

    def _extract_guild_id(self, request: Request) -> Optional[str]:
        """Extract guild ID from URL path or query parameters"""
        # First try path parameters (like /api/guilds/123456/...)
        match = self.GUILD_ID_PATTERN.search(request.url.path)
        if match:
            return match.group(1)

        # Then try query parameters (like ?guild_id=123456)
        guild_id = request.query_params.get("guild_id")
        if guild_id:
            return guild_id

        return None
