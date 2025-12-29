"""
Guild Routes Package

This package organizes guild-related routes into separate modules by functionality:
- core: Basic guild CRUD operations
- preferences: Guild preference management
- messages: Guild message management
- react_roles: React role configurations
- welcome: Welcome message configurations
- levels: Level system configurations
- users: Guild user management
"""

from fastapi import APIRouter

from . import (
    core,
    preferences,
    messages,
    react_roles,
    welcome,
    levels,
    users,
    rss,
    images,
    ai,
)

# Create the main guild router
GUILD_ROUTER = APIRouter()

# Include all sub-routers
GUILD_ROUTER.include_router(core.router, tags=["Guild Core"])
GUILD_ROUTER.include_router(preferences.router, tags=["Guild Preferences"])
GUILD_ROUTER.include_router(messages.router, tags=["Guild Messages"])
GUILD_ROUTER.include_router(react_roles.router, tags=["Guild React Roles"])
GUILD_ROUTER.include_router(welcome.router, tags=["Guild Welcome"])
GUILD_ROUTER.include_router(levels.router, tags=["Guild Levels"])
GUILD_ROUTER.include_router(users.router, tags=["Guild Users"])
GUILD_ROUTER.include_router(rss.router, tags=["Guild RSS Feeds"])
GUILD_ROUTER.include_router(images.router, tags=["Guild Images"])
GUILD_ROUTER.include_router(ai.router, tags=["Guild AI Settings"])

__all__ = ["GUILD_ROUTER"]
