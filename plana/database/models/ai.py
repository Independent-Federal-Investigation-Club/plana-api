from typing import Any, List, Optional, Sequence

from pydantic import Field
from sqlalchemy import ARRAY, BigInteger, Boolean, Column, Float, Integer, String

from .base import PlanaDBModel, PlanaModel, SnowflakeId


class AISetting(PlanaModel):
    """Guild AI feature preferences and configuration."""

    id: Optional[SnowflakeId] = Field(
        default=None, description="ID of the guild for which AI preferences are set"
    )
    # Core Settings
    enabled: Optional[bool] = Field(
        default=False, description="Whether AI features are enabled"
    )

    stream: Optional[bool] = Field(
        default=True, description="Enable streaming responses from the AI"
    )

    engage_mode: Optional[bool] = Field(
        default=False,
        description="Engage mode for AI interactions: False=passive (only at mentioned), True=active (responds to messages)",
    )

    engage_rate: Optional[float] = Field(
        default=0.01,
        description="Probability of AI engaging in conversations when engage mode is active",
    )

    # Memory Configuration
    memory_type: Optional[int] = Field(
        default=1,
        description="Memory scope: 1=guild-wide, 2=per-category, 3=per-channel",
    )
    memory_limit: Optional[int] = Field(
        default=50, description="Maximum number of messages to include in the context"
    )
    # AI Behavior
    system_prompt: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Custom system prompt for AI personality",
    )
    input_template: Optional[str] = Field(
        default='{user.mention} asks: "{message.content}"',
        max_length=500,
        description="Template for formatting user input to AI",
    )

    target_roles: Optional[List[SnowflakeId]] = Field(
        default_factory=list, description="Role IDs to target for AI interactions"
    )
    target_roles_mode: Optional[bool] = Field(
        default=False,
        description="Mode for targeting roles: False=blacklist (ignore), True=whitelist (allow)",
    )

    # Channel Configuration
    target_channels: Optional[List[SnowflakeId]] = Field(
        default_factory=list, description="Channel IDs to target for AI interactions"
    )
    target_channels_mode: Optional[bool] = Field(
        default=False,
        description="Mode for targeting channels: False=blacklist (ignore), True=whitelist (allow)",
    )
    # Advanced Features
    ai_moderation: Optional[bool] = Field(
        default=False, description="Enable AI-assisted moderation"
    )
    reaction_responses: Optional[bool] = Field(
        default=True, description="Allow AI to respond with reactions"
    )


class AISettings(PlanaDBModel):
    """ORM model for guild AI feature configuration."""

    __tablename__ = "ai_settings"

    # Guild ID as primary key
    id = Column[int](BigInteger, primary_key=True, autoincrement=False)

    # Core Settings
    enabled = Column[bool](Boolean, nullable=False, default=False)

    stream = Column[bool](Boolean, nullable=False, default=True)

    engage_mode = Column[bool](Boolean, nullable=False, default=False)
    engage_rate = Column[Any](Float, nullable=False, default=0.01)

    # Memory Configuration
    memory_type = Column[int](Integer, nullable=False, default=1)
    memory_limit = Column[int](Integer, nullable=False, default=50)

    # AI Behavior
    system_prompt = Column[str](String(2048), nullable=True)
    input_template = Column[str](
        String(1024),
        nullable=False,
        default='{user.mention} asks: "{message.content}"',
    )

    # Role Configuration
    target_roles = Column[Sequence[int]](
        ARRAY[int](BigInteger), nullable=False, default=[]
    )
    target_roles_mode = Column[bool](Boolean, nullable=False, default=False)

    # Channel Configuration
    target_channels = Column[Sequence[int]](
        ARRAY[int](BigInteger), nullable=False, default=[]
    )
    target_channels_mode = Column[bool](Boolean, nullable=False, default=False)

    # Advanced Features
    ai_moderation = Column[bool](Boolean, nullable=False, default=False)
    reaction_responses = Column[bool](Boolean, nullable=False, default=True)
