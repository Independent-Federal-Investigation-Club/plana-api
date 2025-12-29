import asyncio
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    BigInteger,
    Column,
    String,
    DateTime,
    JSON,
    Boolean,
    ARRAY,
)
from pydantic import Field, field_validator, model_validator, model_serializer

from plana.database.models.core import GuildEmoji
from plana.database.models.base import PlanaDBModel, PlanaModel, SnowflakeId
from plana.database.utils.helper import SNOWFLAKE_GEN


class Button(PlanaModel):
    """Model for Discord button component."""

    custom_id: Optional[str] = Field(
        default=None, description="Custom ID for the button", max_length=100
    )
    label: str = Field(description="Button label text", max_length=80)
    style: int = Field(description="Button style (1-6)", ge=1, le=6)
    emoji: Optional[GuildEmoji] = Field(
        default=None, description="Optional emoji for the button"
    )
    url: Optional[str] = Field(default=None, description="URL for link-style buttons")
    disabled: Optional[bool] = Field(
        default=False, description="Whether the button is disabled"
    )

    @model_validator(mode="after")
    def validate_custom_id_or_url(self) -> "Button":
        if self.custom_id and self.url:
            raise ValueError("Button cannot have both custom_id and url")
        if not self.custom_id and not self.url:
            raise ValueError("Button must have either custom_id or url")
        return self


class SelectOption(PlanaModel):
    """Model for dropdown select option."""

    label: str = Field(description="Option label", max_length=100)
    value: str = Field(description="Option value", max_length=100)
    description: Optional[str] = Field(
        default=None, description="Option description", max_length=100
    )
    emoji: Optional[GuildEmoji] = Field(
        default=None, description="Optional emoji for the option"
    )
    default: Optional[bool] = Field(
        default=False, description="Whether this option is selected by default"
    )


class SelectMenu(PlanaModel):
    """Model for Discord select menu component."""

    custom_id: str = Field(description="Custom ID for the select menu", max_length=100)
    placeholder: Optional[str] = Field(
        default=None, description="Placeholder text", max_length=150
    )
    min_values: Optional[int] = Field(
        default=1, description="Minimum number of selections", ge=0, le=25
    )
    max_values: Optional[int] = Field(
        default=1, description="Maximum number of selections", ge=1, le=25
    )
    options: List[SelectOption] = Field(description="List of select options")
    disabled: Optional[bool] = Field(
        default=False, description="Whether the select menu is disabled"
    )


class EmbedFooter(PlanaModel):
    text: str = Field(description="Footer text content", max_length=2048)
    icon_url: Optional[str] = Field(
        default=None, description="URL of footer icon image"
    )


class EmbedField(PlanaModel):
    name: str = Field(description="Name of the field", max_length=256)
    value: str = Field(description="Value of the field", max_length=1024)
    inline: Optional[bool] = Field(
        default=True, description="Whether the field should be displayed inline"
    )


class EmbedAuthor(PlanaModel):
    name: str = Field(description="Name of the author")
    url: Optional[str] = Field(
        default=None, description="URL that the author name should link to"
    )
    icon_url: Optional[str] = Field(
        default=None, description="URL of author icon image"
    )


class Embed(PlanaModel):
    """Model for Discord embed."""

    title: Optional[str] = Field(
        default=None, max_length=256, description="Title of the embed"
    )
    description: Optional[str] = Field(
        default=None, max_length=2048, description="Description of the embed"
    )
    url: Optional[str] = Field(
        default=None, description="URL that the title should link to"
    )
    color: Optional[int] = Field(
        default=None, description="Color code of the embed (integer representation)"
    )
    footer: Optional[EmbedFooter] = Field(
        default=None, description="Footer information"
    )
    image: Optional[str] = Field(default=None, description="URL of the main image")
    thumbnail: Optional[str] = Field(
        default=None, description="URL of the thumbnail image"
    )
    author: Optional[EmbedAuthor] = Field(
        default=None, description="Author information"
    )
    fields: Optional[List[EmbedField]] = Field(
        default_factory=list, description="List of embed fields"
    )
    timestamp: Optional[datetime] = Field(
        default=None, description="Timestamp to display in the embed"
    )

    @model_serializer
    def serialize_model(self) -> dict:
        """Custom serializer that automatically integrates with model_dump()."""
        return {
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "color": self.color,
            "footer": self.footer.model_dump() if self.footer else None,
            "image": self.image,
            "thumbnail": self.thumbnail,
            "author": self.author.model_dump() if self.author else None,
            "fields": [field.model_dump() for field in self.fields],
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and not (0 <= v <= 16777215):  # 0xFFFFFF
            raise ValueError("Color must be between 0 and 16777215")
        return v

    @field_validator("fields")
    @classmethod
    def validate_fields(
        cls, v: Optional[List[EmbedField]]
    ) -> Optional[List[EmbedField]]:
        if v is not None and len(v) > 25:
            raise ValueError("Embed cannot have more than 25 fields")
        return v


class Message(PlanaModel):
    """Input validation for message creation/updates"""

    id: Optional[SnowflakeId] = Field(
        default=None, description="Custom ID of the message"
    )

    name: Optional[str] = Field(
        default=None,
        description="Name of the message (for identification purposes)",
        max_length=100,
    )

    message_id: Optional[SnowflakeId] = Field(
        default=None, description="ID of the message (if already sent)"
    )
    guild_id: Optional[SnowflakeId] = Field(default=None, description="ID of the guild")
    channel_id: Optional[SnowflakeId] = Field(
        default=None, description="ID of the channel"
    )

    content: Optional[str] = Field(
        default=None, description="Message content", max_length=2000
    )
    embeds: Optional[List[Embed]] = Field(
        default_factory=list, description="List of embeds"
    )
    components: Optional[List[Button | SelectMenu]] = Field(
        default_factory=list, description="List of buttons and select menus"
    )
    reactions: Optional[List[GuildEmoji]] = Field(
        default_factory=list, description="List of emojis attached to the message"
    )
    published: Optional[bool] = Field(
        default=False, description="Whether the message has been published to Discord"
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp of the last update to the message",
    )


class Messages(PlanaDBModel):
    """
    Model for Discord messages with embeds and components.
    """

    __tablename__ = "messages"

    id = Column(BigInteger, primary_key=True, default=lambda: next(SNOWFLAKE_GEN))
    name = Column(String(100), nullable=True, default=None)

    # Discord IDs
    message_id = Column(BigInteger, nullable=True, index=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    channel_id = Column(BigInteger, nullable=True, index=True)

    # Message content
    content = Column(String(2000), nullable=True)

    # Embedded structures stored as JSON arrays
    embeds = Column(ARRAY(JSON), nullable=True, default=list)
    components = Column(ARRAY(JSON), nullable=True, default=list)
    reactions = Column(ARRAY(JSON), nullable=True, default=list)

    # Message metadata
    published = Column(Boolean, nullable=False, default=False)
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    async def refresh_until_message_id(self):
        """
        Refresh the message until it has a valid message_id, might not be ideal for at least it works...
        """
        retry_delay = 0.3  # seconds
        retry_count = 0
        while self.message_id is None and retry_count <= 8:
            await asyncio.sleep(retry_delay)
            await self.refresh()
            retry_count += 1
            retry_delay *= 1.5

        return self
