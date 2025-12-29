from datetime import datetime
from typing import Optional

from pydantic import Field
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    String,
)

from plana.database.models.base import PlanaDBModel, PlanaModel, SnowflakeId
from plana.database.utils.helper import SNOWFLAKE_GEN


class RssFeed(PlanaModel):
    """Model for RSS feed configuration."""

    id: Optional[SnowflakeId] = Field(default=None, description="ID of the RSS feed")
    guild_id: Optional[SnowflakeId] = Field(default=None, description="ID of the guild")
    channel_id: Optional[SnowflakeId] = Field(
        default=None, description="ID of the channel to post RSS updates"
    )
    url: Optional[str] = Field(
        default=None, description="URL of the RSS feed", max_length=500
    )
    name: Optional[str] = Field(
        default=None, description="Name of the RSS feed", max_length=100
    )
    enabled: bool = Field(default=True, description="Whether this RSS feed is enabled")
    message: Optional[str] = Field(
        default=None,
        description="Custom message to prepend to RSS updates. Supports template variables: "
        "{title}, {link}, {description}, {author}, {pubDate}, {pubDateShort}, "
        "{pubDateTime}, {pubDateISO}, {categories}, {feedName}, {feedUrl}",
        max_length=500,
    )
    last_updated: Optional[datetime] = Field(
        default=None,
        description="Timestamp of the last update to the RSS feed",
    )


class RssFeeds(PlanaDBModel):
    """Model for RSS feed settings."""

    __tablename__ = "rss_feeds"
    id = Column(BigInteger, primary_key=True, default=lambda: next(SNOWFLAKE_GEN))
    guild_id = Column(BigInteger, nullable=False, index=True)
    channel_id = Column(BigInteger, nullable=True, index=True)
    url = Column(String(500), nullable=True, index=True)
    name = Column(String(100), nullable=True)
    enabled = Column(Boolean, default=True)
    message = Column(String(500), nullable=True)
    last_updated = Column(DateTime(timezone=True), nullable=True)
