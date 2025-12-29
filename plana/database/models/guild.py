from typing import Dict, List, Optional

from pydantic import Field, field_validator
from sqlalchemy import ARRAY, BigInteger, Boolean, Column, String

from plana.database.models.base import PlanaDBModel, PlanaModel, SnowflakeId


class GuildPreference(PlanaModel):
    """Guild preferences model for storing and retrieving guild settings."""

    id: Optional[SnowflakeId] = Field(
        default=None, description="ID of the guild for which preferences are set"
    )
    enabled: Optional[bool] = Field(
        default=None, description="Whether bot is enabled in guild"
    )
    command_prefix: Optional[str] = Field(
        default=None, max_length=10, description="Command prefix"
    )
    language: Optional[str] = Field(
        default=None, max_length=10, description="Bot language"
    )
    timezone: Optional[str] = Field(
        default=None, max_length=50, description="Server timezone"
    )
    embed_color: Optional[str] = Field(
        default=None, max_length=7, description="Default embed color"
    )
    embed_footer: Optional[str] = Field(
        default=None, max_length=100, description="Default embed footer"
    )
    embed_footer_images: Optional[list[str]] = Field(
        default=None, description="Default embed footer images"
    )

    @field_validator("embed_color")
    @classmethod
    def validate_hex_color(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not v.startswith("#") or len(v) != 7:
            raise ValueError("Color must be a valid hex color (e.g., #7289DA)")
        try:
            int(v[1:], 16)
        except ValueError:
            raise ValueError("Color must be a valid hex color (e.g., #7289DA)")
        return v


class GuildPreferences(PlanaDBModel):
    """
    Model for Discord server preferences.
    """

    __tablename__ = "server_preferences"

    # Discord Server ID
    id = Column(BigInteger, primary_key=True, autoincrement=False)

    # Whether the bot is enabled in this server, triggered by guild join/leave events
    enabled = Column(Boolean, nullable=False, default=True)

    # Command Prefix
    command_prefix = Column(String(10), nullable=False, default="!")

    # Bot Language, mapped to discord Locale
    language = Column(String(10), nullable=False, default="en-US")

    # Server Timezone
    timezone = Column(String(50), nullable=False, default="UTC")

    # Embed settings
    # Default Embed color
    embed_color = Column(String(7), nullable=False, default="#7289DA")
    # Default Embed Footer
    embed_footer = Column(
        String(256), nullable=False, default="Project Plana, Powered by S.C.H.A.L.E."
    )
    # Embed Footer Images (Images will be displayed randomly)
    embed_footer_images = Column(ARRAY(String(512)), nullable=False, default=[])

    @staticmethod
    async def fetch_bot_status(guild_ids: List[str]) -> Dict[str, bool]:
        """Get bot installation status for multiple guilds in one query."""
        if not guild_ids:
            return {}

        # Convert string IDs to integers for database query
        int_guild_ids = [int(gid) for gid in guild_ids]

        # Use the base model's filter method with SQLAlchemy condition
        guild_preferences = await GuildPreferences.filter(
            GuildPreferences.id.in_(int_guild_ids)
        )

        # Create dict from query results, defaulting to False for missing guilds
        found_guilds = {
            str(guild.id): bool(guild.enabled) for guild in guild_preferences
        }

        from loguru import logger

        logger.info(
            f"Fetched bot status for guilds: {guild_ids}, result {found_guilds}"
        )
        return found_guilds
