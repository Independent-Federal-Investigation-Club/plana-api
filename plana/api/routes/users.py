from typing import List
from fastapi import APIRouter, Depends, HTTPException

from plana.api.middleware.utils import bot_only_operation
from plana.api.utils.helper import (
    _handle_database_error,
)
from plana.database.models.user import User, Users


USER_ROUTER = APIRouter()


@USER_ROUTER.put("/bulk")
@USER_ROUTER.patch("/bulk")
async def bulk_update_guild_user(
    user_data: List[User],
    _: None = Depends(bot_only_operation),
):
    """Update user data for a guild"""
    try:
        updates = [
            user.model_dump(exclude={"guild_id", "user_id"}) for user in user_data
        ]

        count = await Users.bulk_update(
            updates,
            key_field="id",
        )

        return {"message": f"Successfully updated {count} users."}
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("update guild user", e)
