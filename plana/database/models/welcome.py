from datetime import datetime, timezone
from typing import List, Optional

from pydantic import Field, field_validator
from sqlalchemy import JSON, BigInteger, Boolean, Column, DateTime
from sqlalchemy.sql import func

from plana.database.models.base import PlanaDBModel, PlanaModel, SnowflakeId

from .message import Message


class WelcomeAction(PlanaModel):
    """Model for welcome actions configuration."""

    type: str = Field(description="Type of action (add_role, remove_role, send_dm)")
    target_ids: List[SnowflakeId] = Field(
        description="List of role IDs or user IDs depending on action type"
    )
    delay_seconds: Optional[int] = Field(
        default=0, description="Delay in seconds before executing the action", ge=0
    )
    conditions: Optional[dict] = Field(
        default_factory=dict, description="Conditions for action execution"
    )


class WelcomeSetting(PlanaModel):
    """Model for guild welcome system configuration."""

    id: Optional[SnowflakeId] = Field(default=None, description="ID of the guild")
    enabled: Optional[bool] = Field(
        default=False, description="Whether welcome system is enabled"
    )

    # Channel settings
    welcome_channel_id: Optional[SnowflakeId] = Field(
        default=None, description="Channel ID for welcome messages"
    )
    goodbye_channel_id: Optional[SnowflakeId] = Field(
        default=None, description="Channel ID for goodbye messages"
    )
    dm_new_users: Optional[bool] = Field(
        default=False, description="Whether to send DM to new users"
    )

    # Message content
    welcome_message: Optional[Message] = Field(
        default=None, description="Welcome message template"
    )
    goodbye_message: Optional[Message] = Field(
        default=None, description="Goodbye message template"
    )
    dm_message: Optional[Message] = Field(
        default=None, description="DM message template for new users"
    )

    # Auto roles and actions
    auto_roles: Optional[List[int]] = Field(
        default_factory=list, description="List of role IDs to assign to new members"
    )

    updated_at: Optional[datetime] = Field(
        default=None, description="Timestamp of last update"
    )

    @field_validator("auto_roles")
    @classmethod
    def validate_auto_roles(cls, v: List[int]) -> List[int]:
        if len(v) > 20:  # Discord limit
            raise ValueError("Cannot assign more than 20 auto roles")
        return v


class WelcomeSettings(PlanaDBModel):
    """ORM model for guild welcome system configuration."""

    __tablename__ = "welcome_settings"

    id = Column(BigInteger, nullable=False, primary_key=True)

    # Basic settings
    enabled = Column(Boolean, nullable=False, default=False)

    # Channel settings
    welcome_channel_id = Column(BigInteger, nullable=True)
    goodbye_channel_id = Column(BigInteger, nullable=True)
    dm_new_users = Column(Boolean, nullable=False, default=False)

    # Message content stored as JSON
    welcome_message = Column(JSON, nullable=True)
    goodbye_message = Column(JSON, nullable=True)
    dm_message = Column(JSON, nullable=True)

    # Auto roles stored as JSON array
    auto_roles = Column(JSON, nullable=False, default=list)

    # Timestamp
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
