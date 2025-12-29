"""
Simple authentication dependencies for FastAPI routes.

Following the Zen of Python: Simple is better than complex.
"""

import time
from typing import Dict, Tuple

from fastapi import Request
from loguru import logger

from plana.api.auth.oauth import discord_oauth
from plana.api.middleware.types import AuthConstants, AuthData, AuthType

# Permission cache: {(user_id, guild_id): (has_permission, timestamp)} avoid rate limiting Discord API
_permission_cache: Dict[Tuple[str, str], Tuple[bool, float]] = {}
PERMISSION_CACHE_TTL = 60  # 1 minute TTL in seconds


def get_auth(request: Request) -> AuthData:
    """Get authentication info from request"""
    if not hasattr(request.state, "auth"):
        raise AuthConstants.UNAUTHORIZED
    return request.state.auth


def get_current_user(request: Request) -> AuthData:
    """
    Get current authenticated user for AUTH ROUTES ONLY.

    This is for backward compatibility with existing auth routes.
    Other routes should use require_permission instead.
    """
    auth = get_auth(request)

    if auth.auth_type != AuthType.USER:
        raise AuthConstants.FORBIDDEN

    return auth


async def bot_only_operation(request: Request):
    """
    Bot only operation check.

    This is used for API key authenticated bots.
    """
    auth = get_auth(request)

    if auth.auth_type == AuthType.BOT:
        return

    logger.error(f"Bot operation denied: {auth.username} is not a bot")
    raise AuthConstants.FORBIDDEN


async def require_permission(request: Request):
    """
    Require permission for the current operation.

    Permission Rules:
    - API key authenticated bots: Always have full access
    - JWT authenticated users: Must have Discord admin permissions for guild operations
    """
    auth = get_auth(request)
    guild_id = getattr(request.state, "guild_id", None)

    # Handle based on authentication type
    if auth.auth_type == AuthType.BOT:
        # API key authenticated - full access granted
        logger.debug(f"API key authenticated bot '{auth.username}' granted access")
        return

    elif auth.auth_type == AuthType.USER and guild_id:
        # JWT authenticated Discord user
        await _verify_guild_admin_permission(auth, guild_id)
        logger.debug(
            f"User '{auth.username}' verified: has admin permissions in guild {guild_id}"
        )
        return

    # Catch-all for unsupported auth types
    raise AuthConstants.FORBIDDEN


async def _verify_guild_admin_permission(auth: AuthData, guild_id: str) -> None:
    """
    Verify that a Discord user has admin permissions in the specified guild.
    Uses caching to avoid rate limiting Discord API.

    Raises AuthConstants.FORBIDDEN if permission check fails.
    """
    if not auth.discord_token:
        logger.error(
            f"User '{auth.username}' missing Discord token for guild permission check"
        )
        raise AuthConstants.FORBIDDEN

    cache_key = (auth.user_id, guild_id)
    current_time = time.time()

    # Clean up expired cache entries first
    _cleanup_expired_cache(current_time)

    # Check cache for valid entry
    if cache_key in _permission_cache:
        has_permission, cached_time = _permission_cache[cache_key]
        logger.debug(
            f"User '{auth.username}' permission check cached: {'granted' if has_permission else 'denied'} for guild {guild_id}"
        )
        if not has_permission:
            raise AuthConstants.FORBIDDEN
        return

    # Cache miss - verify with Discord API
    try:
        has_permission = await discord_oauth.check_guild_permissions(
            guild_id, auth.discord_token
        )

        # Cache the result
        _permission_cache[cache_key] = (has_permission, current_time)

        if not has_permission:
            logger.warning(
                f"User '{auth.username}' denied: no admin permissions in guild {guild_id}"
            )
            raise AuthConstants.FORBIDDEN

        logger.debug(
            f"User '{auth.username}' verified: has admin permissions in guild {guild_id}"
        )

    except Exception as e:
        logger.error(
            f"Failed to verify guild permissions for user '{auth.username}': {e}"
        )
        raise AuthConstants.FORBIDDEN


def _cleanup_expired_cache(current_time: float) -> None:
    """Clean up expired cache entries to prevent memory leaks"""
    expired_keys = [
        key
        for key, (_, cached_time) in _permission_cache.items()
        if current_time - cached_time >= PERMISSION_CACHE_TTL
    ]
    for key in expired_keys:
        del _permission_cache[key]

    if expired_keys:
        logger.debug(f"Cleaned up {len(expired_keys)} expired permission cache entries")
