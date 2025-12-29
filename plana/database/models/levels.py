from typing import List, Optional
from pydantic import Field
from enum import Enum
from datetime import datetime, timezone
from sqlalchemy import (
    BigInteger,
    Column,
    String,
    Boolean,
    JSON,
    DateTime,
    Integer,
    Float,
    ARRAY,
)

from plana.database.models.base import PlanaDBModel, PlanaModel, SnowflakeId
from .message import Message


class AnnouncementType(str, Enum):
    """Enum for level up announcement types."""

    DISABLED = "disabled"
    CURRENT_CHANNEL = "current_channel"
    PRIVATE_MESSAGE = "private_message"
    CUSTOM_CHANNEL = "custom_channel"


class RoleReward(PlanaModel):
    """Model for role rewards at specific levels."""

    level: int = Field(description="Level required to earn this role")
    role_ids: List[SnowflakeId] = Field(
        default_factory=list, description="List of Discord role IDs to assign"
    )


class XPBooster(PlanaModel):
    """Model for XP rate boosters."""

    role_id: SnowflakeId = Field(description="Discord role ID that gets the boost")
    multiplier: float = Field(
        default=1.0, description="XP multiplier (e.g., 1.5 for 50% bonus)"
    )


class LevelSetting(PlanaModel):
    """Model for guild level system configuration."""

    id: Optional[SnowflakeId] = Field(default=None, description="Discord guild ID")

    # Basic settings
    enabled: Optional[bool] = Field(
        default=False, description="Whether the level system is enabled"
    )
    xp_per_message: Optional[int] = Field(
        default=15, description="Base XP earned per message", ge=1, le=100
    )
    xp_cooldown: Optional[int] = Field(
        default=5, description="Cooldown between XP gains in seconds", ge=0, le=300
    )

    # Level calculation
    base_xp: Optional[int] = Field(
        default=100, description="XP required for level 1", ge=50, le=1000
    )
    xp_multiplier: Optional[float] = Field(
        default=1.2, description="Multiplier for each level", ge=1.0, le=3.0
    )

    # Announcements
    announcement_type: Optional[AnnouncementType] = Field(
        default=AnnouncementType.CURRENT_CHANNEL,
        description="How to announce level ups",
    )
    announcement_channel_id: Optional[SnowflakeId] = Field(
        default=None, description="Channel ID for custom announcements"
    )
    announcement_message: Optional[Message] = Field(
        default=None,
        description="Custom level up message",
        max_length=500,
    )

    # Role rewards
    role_rewards: Optional[List[RoleReward]] = Field(
        default_factory=list, description="Role rewards for reaching levels"
    )

    # XP boosters
    xp_boosters: Optional[List[XPBooster]] = Field(
        default_factory=list, description="XP multipliers for specific roles"
    )

    # No-XP roles
    target_xp_roles: Optional[List[SnowflakeId]] = Field(
        default_factory=list, description="Roles that will either gain or not gain XP"
    )
    target_xp_roles_mode: Optional[bool] = Field(
        default=False,
        description="Whether target_xp_roles is whitelist (gain) or blacklist (not gain)",
    )

    # No-XP channels
    target_xp_channels: Optional[List[SnowflakeId]] = Field(
        default_factory=list, description="Channels where XP isn't gained"
    )
    target_xp_channels_mode: Optional[bool] = Field(
        default=False,
        description="Whether target_xp_channels is whitelist (gain) or blacklist (not gain)",
    )

    # Advanced settings
    stack_rewards: Optional[bool] = Field(
        default=True, description="Whether to stack role rewards or replace them"
    )
    message_length_bonus: Optional[bool] = Field(
        default=True, description="Whether longer messages give more XP"
    )
    max_xp_per_message: Optional[int] = Field(
        default=25,
        description="Maximum XP that can be earned from a single message",
        ge=1,
        le=200,
    )

    updated_at: Optional[datetime] = Field(
        default=None, description="Timestamp of last update"
    )


class LevelSettings(PlanaDBModel):
    """ORM model for guild level system configuration."""

    __tablename__ = "level_settings"

    id = Column(BigInteger, nullable=False, primary_key=True)

    # Basic settings
    enabled = Column(Boolean, nullable=False, default=False)
    xp_per_message = Column(Integer, nullable=False, default=15)
    xp_cooldown = Column(Integer, nullable=False, default=5)

    # Level calculation
    base_xp = Column(Integer, nullable=False, default=100)
    xp_multiplier = Column(Float, nullable=False, default=1.2)

    # Announcements
    announcement_type = Column(String(20), nullable=False, default="current_channel")
    announcement_channel_id = Column(BigInteger, nullable=True)
    announcement_message = Column(JSON, nullable=True)

    # Role rewards stored as JSON array
    role_rewards = Column(JSON, nullable=True, default=list)

    # XP boosters stored as JSON array
    xp_boosters = Column(JSON, nullable=True, default=list)

    # Target XP configuration
    target_xp_roles = Column(ARRAY(BigInteger), nullable=True, default=list)
    target_xp_roles_mode = Column(Boolean, nullable=False, default=False)
    target_xp_channels = Column(ARRAY(BigInteger), nullable=True, default=list)
    target_xp_channels_mode = Column(Boolean, nullable=False, default=False)

    # Advanced settings
    stack_rewards = Column(Boolean, nullable=False, default=True)
    message_length_bonus = Column(Boolean, nullable=False, default=True)
    max_xp_per_message = Column(Integer, nullable=False, default=25)

    # Timestamp
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
