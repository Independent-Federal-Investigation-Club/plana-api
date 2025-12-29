import os
import secrets
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import traceback

from loguru import logger
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from plana.api.auth.oauth import discord_oauth
from plana.api.middleware.utils import get_current_user
from plana.api.middleware.types import AuthData, AuthConstants

from plana.database import GuildPreferences

router = APIRouter()


def generate_popup_html(
    success: bool, token: Optional[str] = None, error: Optional[str] = None
) -> str:
    """Generate HTML content for popup OAuth flow"""
    frontend_redirect = os.getenv("FRONTEND_REDIRECT_URI", "http://localhost:3000")

    if success:
        title = "Authentication Complete"
        message_type = "DISCORD_OAUTH_SUCCESS"
        message_data = f"token: '{token}'"
        fallback_message = "Authentication successful. Please close this window."
        auto_close_message = (
            "Authentication successful. This window should close automatically."
        )
    else:
        title = "Authentication Error"
        message_type = "DISCORD_OAUTH_ERROR"
        message_data = f"error: '{error}'"
        fallback_message = (
            "Authentication failed. Please close this window and try again."
        )
        auto_close_message = (
            "Authentication failed. Please close this window and try again."
        )

    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>{title}</title></head>
    <body>
      <script>
        if (window.opener) {{
          window.opener.postMessage({{
            type: '{message_type}',
            {message_data}
          }}, '{frontend_redirect}');
          setTimeout(function() {{
            window.close();
          }}, 2000);
        }} else {{
          document.body.innerHTML = '<p>{fallback_message}</p>';
        }}
      </script>
      <p>{auto_close_message}</p>
    </body>
    </html>
    """


class AuthCallbackRequest(BaseModel):
    """Request model for OAuth callback"""

    code: str = Field(..., description="OAuth authorization code")
    state: Optional[str] = Field(
        None,
        description="OAuth state parameter, Optional but recommended for CSRF protection",
    )


class AuthResponse(BaseModel):
    """Response model for successful authentication"""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: Dict[str, Any] = Field(..., description="User information")


class AuthUrlResponse(BaseModel):
    """Response model for OAuth URL generation"""

    url: str = Field(..., description="Discord OAuth authorization URL")
    state: str = Field(..., description="OAuth state parameter")


class UserInfo(BaseModel):
    """User information response model"""

    user: Dict[str, Any] = Field(..., description="Current user data")


class CustomGuildInfo(BaseModel):
    """Guild information model"""

    id: str = Field(..., description="Guild ID")
    name: str = Field(..., description="Guild name")
    icon: Optional[str] = Field(None, description="Guild icon hash")
    banner: Optional[str] = Field(None, description="Guild banner hash")
    owner: bool = Field(False, description="Whether user owns the guild")
    permissions: int = Field(..., description="User permissions in guild")
    bot_installed: bool = Field(False, description="Whether bot is installed in guild")


class UserGuildsResponse(BaseModel):
    """Response model for user guilds"""

    guilds: List[CustomGuildInfo] = Field(
        ..., description="List of user's admin guilds"
    )
    user_id: str = Field(..., description="User ID")


@router.get("/url", response_model=AuthUrlResponse)
async def get_auth_url():
    """Generate Discord OAuth authorization URL"""
    try:
        state = secrets.token_urlsafe(32)
        url = discord_oauth.get_oauth_url(state)
        return AuthUrlResponse(url=url, state=state)
    except Exception as e:
        logger.error(f"Failed to generate OAuth URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate authorization URL",
        )


# bot invite url
@router.get("/invite")
async def get_bot_invite_url():
    """Generate Discord OAuth authorization URL"""
    params = {
        "client_id": os.getenv("DISCORD_CLIENT_ID"),
        "permissions": AuthConstants.ADMIN_PERMISSION,
        "scope": "bot",
    }
    url = f"https://discord.com/oauth2/authorize?{urlencode(params)}"
    return {"url": url}


@router.get("/callback")
async def auth_callback(
    code: str = Query(..., description="OAuth authorization code"),
    state: Optional[str] = Query(None, description="OAuth state parameter"),
):
    """Handle Discord OAuth callback and create session"""
    try:
        # Exchange code for access token
        token_data = await discord_oauth.exchange_code_for_token(code)

        discord_access_token = token_data["access_token"]

        # Get user information
        user_data = await discord_oauth.get_user_info(discord_access_token)

        # Create JWT token
        jwt_token = discord_oauth.create_jwt_token(user_data, discord_access_token)

        # Return popup HTML with success message
        html_content = generate_popup_html(success=True, token=jwt_token)
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Authentication failed: {e}")

        # Return popup HTML with error message
        html_content = generate_popup_html(success=False, error="Authentication failed")
        return HTMLResponse(content=html_content)


@router.get("/me", response_model=UserInfo)
async def get_current_user_info(
    current_user: AuthData = Depends(get_current_user),
):
    """Get current authenticated user information"""
    return UserInfo(
        user={
            "id": current_user.user_id,
            "username": current_user.username,
            "avatar": current_user.avatar,
        }
    )


@router.post("/logout")
async def logout(current_user: AuthData = Depends(get_current_user)):
    """Logout user (client handles token removal)"""
    logger.info(f"User {current_user.username} logged out")
    return {"message": "Logged out successfully"}


@router.get("/guilds", response_model=UserGuildsResponse)
async def get_user_guilds(current_user: AuthData = Depends(get_current_user)):
    """Get user's Discord guilds where they have admin permissions"""
    try:
        discord_access_token = current_user.discord_token
        if not discord_access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Discord access token not found",
            )

        # Get user's guilds
        guilds = await discord_oauth.get_user_guilds(discord_access_token)

        # Filter guilds where user has admin permissions
        admin_guilds = [
            guild
            for guild in guilds
            if int(guild.get("permissions", 0)) & AuthConstants.ADMIN_PERMISSION != 0
        ]

        from loguru import logger

        logger.info(f"Admin guilds: {admin_guilds}")

        # Get bot status for all admin guilds in one query
        admin_guild_ids = [guild["id"] for guild in admin_guilds]
        guild_bot_status = await GuildPreferences.fetch_bot_status(admin_guild_ids)

        # Create CustomGuildInfo objects with bot_installed status
        final_admin_guilds = [
            CustomGuildInfo(
                id=guild["id"],
                name=guild["name"],
                banner=guild.get("banner"),
                icon=guild.get("icon"),
                owner=guild.get("owner", False),
                permissions=int(guild.get("permissions", 0)),
                bot_installed=guild_bot_status.get(guild["id"], False),
            )
            for guild in admin_guilds
        ]

        logger.info(
            f"User {current_user.username} has admin access to {len(final_admin_guilds)} guilds"
        )

        return UserGuildsResponse(
            guilds=final_admin_guilds, user_id=current_user.user_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch user guilds: {e}, {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user guilds",
        )
