# Copy from the Plana-API Database models

from typing import List, Optional

from pydantic import Field
from sqlalchemy import ARRAY, JSON, BigInteger, Column, Integer, String

from plana.database.models.base import PlanaDBModel, PlanaModel, SnowflakeId


class GuildUser(PlanaModel):
    """
    Pydantic Model for Discord Guild User Data
    """

    user_id: SnowflakeId = Field(..., description="Discord User ID")
    username: str = Field(..., max_length=100, description="Username of the user")
    avatar: Optional[str] = Field(None, max_length=32, description="User's avatar hash")


class GuildRole(PlanaModel):
    """
    Pydantic Model for Discord Guild Role Data
    """

    role_id: SnowflakeId = Field(..., description="Discord Role ID")
    name: str = Field(..., max_length=100, description="Name of the role")
    color: Optional[int] = Field(None, description="Role color in decimal format")
    permissions: Optional[int] = Field(None, description="Role permissions bitfield")
    position: int = Field(0, description="Position of the role in the hierarchy")


class GuildEmoji(PlanaModel):
    """
    Pydantic Model for Discord Guild Emoji Data
    """

    emoji_id: Optional[SnowflakeId] = Field(default=None, description="Discord Emoji ID")
    name: str = Field(..., max_length=100, description="Name of the emoji")
    url: Optional[str] = Field(
        None, max_length=256, description="URL of the emoji [for emoji uploads]"
    )
    animated: bool = Field(False, description="Whether the emoji is animated")


class GuildSticker(PlanaModel):
    """
    Pydantic Model for Discord Guild Sticker Data
    """

    sticker_id: SnowflakeId = Field(..., description="Discord Sticker ID")
    name: str = Field(..., max_length=100, description="Name of the sticker")
    url: Optional[str] = Field(..., max_length=256, description="URL of the sticker")
    description: Optional[str] = Field(
        None, max_length=512, description="Description of the sticker"
    )
    emoji: str = Field(..., max_length=100, description="Emoji representation of the sticker")

    format: int = Field(
        ...,
        description="Format type of the sticker (1 = PNG, 2 = APNG, 3 = LOTTIE, 4 = GIF)",
    )
    available: bool = Field(True, description="Whether the sticker is available")


class TextChannel(PlanaModel):
    """
    Pydantic Model for Discord Guild Channel Data
    """

    channel_id: SnowflakeId = Field(..., description="Discord Channel ID")
    category_id: Optional[SnowflakeId] = Field(
        default=None, description="ID of the category this channel belongs to"
    )
    name: str = Field(..., max_length=100, description="Name of the channel")
    position: int = Field(0, description="Position of the channel in the list")
    topic: Optional[str] = Field(None, max_length=1024, description="Channel topic")
    nsfw: bool = Field(
        False, description="Whether the channel is marked as NSFW (Not Safe For Work)"
    )


class GuildCategory(PlanaModel):
    """
    Pydantic Model for Discord Guild Category Data
    """

    category_id: SnowflakeId = Field(..., description="Discord Category ID")
    name: str = Field(..., max_length=100, description="Name of the category")
    position: int = Field(0, description="Position of the category in the list")


class Guild(PlanaModel):
    """
    Pydantic Model for Discord Guild Data for Input Validation
    """

    id: SnowflakeId = Field(..., description="Discord Server ID")
    name: str = Field(..., max_length=100, description="Name of the server")
    icon: Optional[str] = Field(None, max_length=34, description="Server icon hash")
    banner: Optional[str] = Field(None, max_length=34, description="Server banner hash")
    owner_id: SnowflakeId = Field(..., description="ID of the server owner")

    premium_tier: Optional[int] = Field(
        0, description="Server premium tier (0 = None, 1 = Tier 1, etc.)"
    )
    premium_subscription_count: Optional[int] = Field(
        0, description="Number of premium subscriptions"
    )

    users: List[GuildUser] = Field(default_factory=list, description="List of users in the guild")
    roles: List[GuildRole] = Field(default_factory=list, description="List of roles in the guild")
    emojis: List[GuildEmoji] = Field(
        default_factory=list, description="List of emojis in the guild"
    )
    stickers: List[GuildSticker] = Field(
        default_factory=list, description="List of stickers in the guild"
    )
    channels: List[TextChannel] = Field(
        default_factory=list, description="List of channels in the guild"
    )
    categories: List[GuildCategory] = Field(
        default_factory=list, description="List of categories in the guild"
    )


class Guilds(PlanaDBModel):
    """
    ORM Model for Discord Guild (Server) Data
    """

    __tablename__ = "guilds"

    # Discord Server ID
    id = Column(BigInteger, primary_key=True)
    name = Column(String(100), nullable=False, default="")

    icon = Column(String(32), nullable=True, default=None)
    banner = Column(String(32), nullable=True, default=None)
    owner_id = Column(BigInteger, nullable=False, default=0)

    # Basic Guild Information
    premium_tier = Column(
        Integer, nullable=True, default=0
    )  # 0 = None, 1 = Tier 1, 2 = Tier 2, 3 = Tier 3
    premium_subscription_count = Column(Integer, nullable=True, default=0)

    # Guild Specific Data
    users = Column(ARRAY(JSON), nullable=True, default=list)
    roles = Column(ARRAY(JSON), nullable=True, default=list)
    emojis = Column(ARRAY(JSON), nullable=True, default=list)
    stickers = Column(ARRAY(JSON), nullable=True, default=list)
    channels = Column(ARRAY(JSON), nullable=True, default=list)
    categories = Column(ARRAY(JSON), nullable=True, default=list)
