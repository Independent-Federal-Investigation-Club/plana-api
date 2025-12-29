import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List
from urllib.parse import urlencode

import jwt
from fastapi import HTTPException, status
from loguru import logger

from plana.api.utils.helper import make_request, validate_environment

# Discord API constants
DISCORD_API_BASE = "https://discord.com/api"
DISCORD_OAUTH_URL = f"{DISCORD_API_BASE}/oauth2"
DISCORD_API_V10 = f"{DISCORD_API_BASE}/v10"
ADMIN_PERMISSION = 0x00000008


class DiscordOAuth:
    """Discord OAuth 2.0 handler with permission checking"""

    def __init__(self):
        validate_environment()

        self.client_id = os.getenv("DISCORD_CLIENT_ID")
        self.client_secret = os.getenv("DISCORD_CLIENT_SECRET")
        self.redirect_uri = os.getenv("DISCORD_REDIRECT_URI")
        self.jwt_secret = os.getenv("JWT_SECRET")

    def get_oauth_url(self, state: str) -> str:
        """Generate Discord OAuth authorization URL"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "identify guilds",
            "state": state,
        }
        return f"{DISCORD_OAUTH_URL}/authorize?{urlencode(params)}"

    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        return await make_request("POST", f"{DISCORD_OAUTH_URL}/token", headers, data)

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Discord API"""
        headers = {"Authorization": f"Bearer {access_token}"}
        return await make_request("GET", f"{DISCORD_API_V10}/users/@me", headers)

    async def get_user_guilds(self, access_token: str) -> List[Dict[str, Any]]:
        """Get user's guilds from Discord API"""
        headers = {"Authorization": f"Bearer {access_token}"}
        return await make_request("GET", f"{DISCORD_API_V10}/users/@me/guilds", headers)

    async def check_guild_permissions(
        self,
        guild_id: str,
        access_token: str,
    ) -> bool:
        """Check if user has admin permissions in guild"""
        try:
            user_guilds = await self.get_user_guilds(access_token)

            # Find the target guild
            target_guild = next(
                (guild for guild in user_guilds if str(guild["id"]) == str(guild_id)),
                None,
            )

            if not target_guild:
                logger.warning(f"User not found in guild {guild_id}")
                return False

            # Check administrator permission
            permissions = int(target_guild.get("permissions", 0))

            logger.info(f"User permissions in guild {guild_id}: {permissions}")
            has_admin = bool(permissions & ADMIN_PERMISSION)

            if has_admin:
                logger.info(f"User has admin permissions in guild {guild_id}")
                return True

            logger.info(f"User does not have admin permissions in guild {guild_id}")
            return False

        except Exception as e:
            logger.error(f"Error checking guild permissions: {e}")
            return False

    def create_jwt_token(
        self, user_data: Dict[str, Any], discord_access_token: str
    ) -> str:
        """Create JWT token for authenticated user"""

        now = datetime.now(timezone.utc)
        payload = {
            "user_id": user_data["id"],
            "username": user_data["username"],
            "avatar": user_data.get("avatar"),
            "discord_access_token": discord_access_token,
            "iat": now,
            "exp": now + timedelta(hours=24),
        }
        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")

    def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            return jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )


# Singleton instance
discord_oauth = DiscordOAuth()
