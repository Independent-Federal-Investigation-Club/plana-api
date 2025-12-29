from typing import Optional
from sqlalchemy import BigInteger, Column, JSON, DateTime

from plana.database.models.base import PlanaDBModel, PlanaModel, SnowflakeId
from plana.database.utils.helper import SNOWFLAKE_GEN
from pydantic import Field
from datetime import datetime, timezone


class User(PlanaModel):
    """User model for storing and retrieving user data."""

    id: Optional[SnowflakeId] = Field(
        default=None, description="Custom Global Unique ID of the user"
    )

    user_id: SnowflakeId = Field(
        description="ID of the user for which users are set",
    )

    guild_id: Optional[SnowflakeId] = Field(
        default=None,
        description="ID of the guild for which users are set",
    )

    user_data: Optional[dict] = Field(
        default_factory=dict, description="User data dictionary"
    )


class Users(PlanaDBModel):
    """ORM model for user data storage."""

    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, default=lambda: next(SNOWFLAKE_GEN))
    user_id = Column(BigInteger, nullable=False, index=True)
    guild_id = Column(BigInteger, nullable=False, index=True)

    # User data stored as JSON
    user_data = Column(JSON, nullable=False, default=dict)

    # Timestamp
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
