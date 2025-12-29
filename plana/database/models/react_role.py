from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy import (
    BigInteger,
    Column,
    String,
    JSON,
    Boolean,
    ARRAY,
    DateTime,
)

from pydantic import Field
from plana.database.utils.helper import SNOWFLAKE_GEN
from plana.database.models.base import PlanaDBModel, PlanaModel, SnowflakeId


class RoleAssignment(PlanaModel):
    """Model for role assignment configuration."""

    role_ids: List[SnowflakeId] = Field(
        description="List of Discord role IDs to assign"
    )
    trigger_id: str = Field(
        description="ID of the trigger (emoji.id or emoji.name), button custom_id, or menu.custom_id-option.value)"
    )


class ReactRoleSetting(PlanaModel):
    """Model for react role configuration."""

    id: Optional[SnowflakeId] = Field(
        default=None, description="ID of the react role config"
    )
    guild_id: Optional[SnowflakeId] = Field(default=None, description="ID of the guild")
    message_id: Optional[SnowflakeId] = Field(
        default=None, description="ID of the message to attach react roles to"
    )
    name: Optional[str] = Field(
        default=None,
        description="Name/description of this react role setup",
        max_length=100,
    )
    role_assignments: List[RoleAssignment] = Field(
        default_factory=list, description="List of role assignments"
    )
    enabled: Optional[bool] = Field(
        default=True, description="Whether this react role configuration is enabled"
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp of the last update to the message",
    )


class ReactRoles(PlanaDBModel):
    """Model for react role database entry."""

    __tablename__ = "react_roles"

    id = Column(BigInteger, primary_key=True, default=lambda: next(SNOWFLAKE_GEN))
    guild_id = Column(BigInteger, nullable=False, index=True)
    message_id = Column(BigInteger, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    role_assignments = Column(ARRAY(JSON), nullable=True, default=list)
    enabled = Column(Boolean, default=True)

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
