from typing import Optional
from loguru import logger
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request

from plana.api.middleware.utils import require_permission
from plana.api.utils.helper import (
    _handle_database_error,
    ids_string_to_int,
)
from plana.api.utils.handler import raise_404_if_not_found, handle_guild_config_refresh
from plana.database.models.rss import RssFeeds, RssFeed


router = APIRouter()


@router.get("/{guild_id}/rss")
async def list_guild_rss_feeds(
    guild_id: str = Path(..., description="Discord Guild ID"),
    limit: Optional[int] = Query(
        default=50, le=100, description="Maximum number of RSS feeds to return"
    ),
    offset: Optional[int] = Query(
        default=0, ge=0, description="Number of RSS feeds to skip"
    ),
    _: None = Depends(require_permission),
):
    """List all RSS feeds for a guild"""
    guild_id_int = ids_string_to_int(guild_id=guild_id)

    try:
        rss_feeds = await RssFeeds.filter(
            RssFeeds.guild_id == guild_id_int,
            limit=limit,
            offset=offset,
            order_by=RssFeeds.last_updated.desc(),
        )
        total_count = await RssFeeds.count(RssFeeds.guild_id == guild_id_int)

        return {
            "data": [rss_feed.to_dict() for rss_feed in rss_feeds],
            "total_count": total_count,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("list guild RSS feeds", e)


@router.post("/{guild_id}/rss")
async def create_guild_rss_feed(
    rss_data: RssFeed,
    guild_id: str = Path(..., description="Discord Guild ID"),
    _: None = Depends(require_permission),
):
    """Create a new RSS feed for the guild"""
    guild_id_int = ids_string_to_int(guild_id=guild_id)

    try:
        # Check if RSS feed with same URL already exists for this guild
        existing_feed = await RssFeeds.get_by(guild_id=guild_id_int, url=rss_data.url)

        if existing_feed:
            raise HTTPException(
                status_code=400,
                detail=f"RSS feed with URL {rss_data.url} already exists for guild {guild_id}",
            )

        create_data = rss_data.model_dump(exclude={"id", "guild_id", "updated_at"})
        rss_feed = RssFeeds(guild_id=guild_id_int, **create_data)

        await rss_feed.save()
        return rss_feed.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("create guild RSS feed", e)


@router.get("/{guild_id}/rss/{rss_id}")
async def get_guild_rss_feed(
    guild_id: str = Path(..., description="Discord Guild ID"),
    rss_id: str = Path(..., description="RSS Feed ID"),
    _: None = Depends(require_permission),
):
    """Get a specific RSS feed for the guild"""
    ids = ids_string_to_int(guild_id=guild_id, rss_id=rss_id)
    guild_id_int, rss_id_int = ids if isinstance(ids, tuple) else (ids, ids)

    try:
        rss_feed = await RssFeeds.get_by(id=rss_id_int, guild_id=guild_id_int)
        raise_404_if_not_found(rss_feed)

        return rss_feed.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("fetch guild RSS feed", e)


@router.put("/{guild_id}/rss/{rss_id}")
@router.patch("/{guild_id}/rss/{rss_id}")
async def update_guild_rss_feed(
    request: Request,
    rss_data: RssFeed,
    guild_id: str = Path(..., description="Discord Guild ID"),
    rss_id: str = Path(..., description="RSS Feed ID"),
    _: None = Depends(require_permission),
):
    """Update a guild RSS feed"""
    ids = ids_string_to_int(guild_id=guild_id, rss_id=rss_id)
    guild_id_int, rss_id_int = ids if isinstance(ids, tuple) else (ids, ids)

    try:
        rss_feed = await RssFeeds.get_by(id=rss_id_int, guild_id=guild_id_int)
        raise_404_if_not_found(rss_feed)

        if request.method == "PUT":
            update_data = rss_data.model_dump(exclude={"id", "guild_id", "updated_at"})
        else:
            update_data = rss_data.model_dump(
                exclude={"id", "guild_id", "updated_at"}, exclude_unset=True
            )

        await rss_feed.update(**update_data)
        await handle_guild_config_refresh(guild_id_int, "rss")
        return rss_feed.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("update guild RSS feed", e)


@router.delete("/{guild_id}/rss/{rss_id}")
async def delete_guild_rss_feed(
    guild_id: str = Path(..., description="Discord Guild ID"),
    rss_id: str = Path(..., description="RSS Feed ID"),
    _: None = Depends(require_permission),
):
    """Delete a guild RSS feed"""
    ids = ids_string_to_int(guild_id=guild_id, rss_id=rss_id)
    guild_id_int, rss_id_int = ids if isinstance(ids, tuple) else (ids, ids)

    try:
        rss_feed = await RssFeeds.get_by(id=rss_id_int, guild_id=guild_id_int)
        raise_404_if_not_found(rss_feed)

        await rss_feed.delete()
        await handle_guild_config_refresh(guild_id_int, "rss")
        return {"message": "RSS feed deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("delete guild RSS feed", e)
