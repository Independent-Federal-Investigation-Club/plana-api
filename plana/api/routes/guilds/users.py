from typing import Optional, List
from loguru import logger
from fastapi import APIRouter, Depends, HTTPException, Path, Query

from plana.api.middleware.utils import require_permission, bot_only_operation
from plana.api.utils.helper import (
    _handle_database_error,
    ids_string_to_int,
)
from plana.api.utils.handler import raise_404_if_not_found
from plana.database.models.user import User, Users


router = APIRouter()


@router.get("/{guild_id}/users")
async def list_guild_users(
    guild_id: str = Path(..., description="Discord Guild ID"),
    limit: Optional[int] = Query(
        default=50, le=100, description="Maximum number of users to return"
    ),
    offset: Optional[int] = Query(
        default=0, ge=0, description="Number of users to skip"
    ),
    _: None = Depends(require_permission),
):
    """List all users for a guild"""
    guild_id_int = ids_string_to_int(guild_id=guild_id)

    try:
        users = await Users.filter(
            Users.guild_id == guild_id_int,
            limit=limit,
            offset=offset,
            order_by=Users.updated_at.desc(),
        )
        total_count = await Users.count(Users.guild_id == guild_id_int)

        return {
            "data": [user.to_dict() for user in users],
            "total": total_count,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("list guild users", e)


@router.get("/{guild_id}/users/{user_id}")
async def get_guild_user(
    guild_id: str = Path(..., description="Discord Guild ID"),
    user_id: str = Path(..., description="Discord User ID"),
    _: None = Depends(require_permission),
):
    """Get specific user data for a guild"""
    ids = ids_string_to_int(guild_id=guild_id, user_id=user_id)
    guild_id_int, user_id_int = ids if isinstance(ids, tuple) else (ids, ids)

    try:
        user = await Users.get_by(guild_id=guild_id_int, user_id=user_id_int)
        raise_404_if_not_found(user)

        return user.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("fetch guild user", e)


@router.post("/{guild_id}/users")
async def create_guild_user(
    user_data: User,
    guild_id: str = Path(..., description="Discord Guild ID"),
    _: None = Depends(require_permission),
):
    """Create user data for a guild"""
    guild_id_int = ids_string_to_int(guild_id=guild_id)

    try:
        user_data.guild_id = guild_id_int
        create_data = user_data.model_dump(exclude_unset=True)

        user = Users(**create_data)
        await user.save()

        logger.info(f"Created user data for guild {guild_id}")
        return user.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("create guild user", e)


@router.put("/{guild_id}/users/{user_id}")
@router.patch("/{guild_id}/users/{user_id}")
async def update_guild_user(
    user_data: User,
    guild_id: str = Path(..., description="Discord Guild ID"),
    user_id: str = Path(..., description="Discord User ID"),
    _: None = Depends(bot_only_operation),
):
    """Update user data for a guild"""
    ids = ids_string_to_int(guild_id=guild_id, user_id=user_id)
    guild_id_int, user_id_int = ids if isinstance(ids, tuple) else (ids, ids)

    try:
        user, created = await Users.get_or_create(
            guild_id=guild_id_int,
            user_id=user_id_int,
            defaults=user_data.model_dump(exclude_unset=True),
        )

        if not created:
            update_data = user_data.model_dump(exclude_unset=True)
            await user.update(**update_data)

        return user.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("update guild user", e)


@router.put("/{guild_id}/users/bulk")
@router.patch("/{guild_id}/users/bulk")
async def bulk_update_guild_user(
    user_data: List[User],
    guild_id: str = Path(..., description="Discord Guild ID"),
    _: None = Depends(bot_only_operation),
):
    """Update user data for a guild"""
    guild_id_int = ids_string_to_int(guild_id=guild_id)
    try:
        valid_users = [user for user in user_data if user.guild_id == guild_id_int]
        updates = [user.model_dump(exclude={"guild_id"}) for user in valid_users]

        count = await Users.bulk_update(
            updates,
            key_field="id",
        )

        return {"message": f"Successfully updated {count} users in guild {guild_id}"}
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("update guild user", e)


@router.delete("/{guild_id}/users/{user_id}")
async def delete_guild_user(
    guild_id: str = Path(..., description="Discord Guild ID"),
    user_id: str = Path(..., description="Discord User ID"),
    _: None = Depends(bot_only_operation),
):
    """Delete user data for a guild"""
    ids = ids_string_to_int(guild_id=guild_id, user_id=user_id)
    guild_id_int, user_id_int = ids if isinstance(ids, tuple) else (ids, ids)

    try:
        user = await Users.get_by(guild_id=guild_id_int, user_id=user_id_int)
        raise_404_if_not_found(user)

        await user.delete()
        logger.info(f"Deleted user data for guild {guild_id}, user {user_id}")

        return {"message": "User data deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("delete guild user", e)


@router.get("/{guild_id}/users/{user_id}/user_data/{param}")
async def get_guild_user_data(
    guild_id: str = Path(..., description="Discord Guild ID"),
    user_id: str = Path(..., description="Discord User ID"),
    param: str = Path(..., description="Parameter to fetch from user data"),
    _: None = Depends(bot_only_operation),
):
    """Get specific user data for a guild"""
    ids = ids_string_to_int(guild_id=guild_id, user_id=user_id)
    guild_id_int, user_id_int = ids if isinstance(ids, tuple) else (ids, ids)

    try:
        user = await Users.get_by(guild_id=guild_id_int, user_id=user_id_int)
        raise_404_if_not_found(user)

        return user.user_data[param] if param in user.user_data else None
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("fetch guild user", e)


@router.post("/{guild_id}/users/{user_id}/user_data/{param}")
@router.put("/{guild_id}/users/{user_id}/user_data/{param}")
@router.patch("/{guild_id}/users/{user_id}/user_data/{param}")
async def update_guild_user_data(
    value: dict,
    guild_id: str = Path(..., description="Discord Guild ID"),
    user_id: str = Path(..., description="Discord User ID"),
    param: str = Path(..., description="Parameter to update in user data"),
    _: None = Depends(bot_only_operation),
):
    """Update specific user data parameter for a guild"""
    ids = ids_string_to_int(guild_id=guild_id, user_id=user_id)
    guild_id_int, user_id_int = ids if isinstance(ids, tuple) else (ids, ids)

    try:
        user = await Users.get_by(guild_id=guild_id_int, user_id=user_id_int)
        raise_404_if_not_found(user)

        user.user_data[param] = value

        await user.save()
        return user.user_data[param] if param in user.user_data else None
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("update guild user param", e)
