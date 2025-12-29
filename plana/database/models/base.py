from datetime import datetime, timezone
from functools import wraps
from typing import Annotated, Any, Dict, List, Optional, Type, TypeVar

from loguru import logger
from pydantic import BaseModel, BeforeValidator
from sqlalchemy import and_, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import ColumnElement

from plana.database.utils.db import PlanaDB

T = TypeVar("T", bound="PlanaDBModel")


def snowflake_validator(v: Optional[str]) -> Optional[int]:
    """Validator function for snowflake ID fields"""
    if v is None:
        return None
    if isinstance(v, str) and v.isdigit():
        return int(v)
    if isinstance(v, int):
        return v
    return v


# Use BeforeValidator to actually apply the validator
SnowflakeId = Annotated[Optional[int], BeforeValidator(snowflake_validator)]


class PlanaModel(BaseModel):

    def __init__(self, **data: Any):
        super().__init__(**data)


def db_operation(func):
    """Decorator for database operations with error handling and logging."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = datetime.now()
        try:
            result = await func(*args, **kwargs)
            duration = (datetime.now() - start_time).total_seconds()
            if duration > 1.0:  # Log slow operations
                logger.warning(f"Slow DB operation: {func.__name__} took {duration:.2f}s")
            return result
        except SQLAlchemyError as e:
            logger.error(f"Database operation {func.__name__} failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
            raise

    return wrapper


class PlanaDBModel(PlanaDB.base):
    """Enhanced base model with database operations and validation."""

    __abstract__ = True

    # ========== Core Operations ==========

    @db_operation
    async def save(self) -> "PlanaDBModel":
        """Save model instance to database."""
        async with PlanaDB.get_session() as session:
            await self.validate()
            session.add(self)
            await session.commit()
            await session.refresh(self)
            return self

    @db_operation
    async def delete(self) -> bool:
        """Delete model instance from plana.database."""
        async with PlanaDB.get_session() as session:
            await session.delete(self)
            await session.commit()
            return True

    @db_operation
    async def update(self, **kwargs: Any) -> "PlanaDBModel":
        """Update model attributes with validation."""
        if not kwargs:
            return self

        # Validate attributes exist
        valid_attrs = {c.name for c in self.__table__.columns}
        invalid_attrs = set(kwargs.keys()) - valid_attrs

        if invalid_attrs:
            raise ValueError(f"Invalid attributes: {invalid_attrs}")

        # Check for actual changes
        changes = {}
        for key, value in kwargs.items():
            current_value = getattr(self, key)
            if current_value != value:
                changes[key] = value

        # Only proceed if there are actual changes
        if not changes:
            return self

        # Update attributes
        for key, value in changes.items():
            setattr(self, key, value)

        await self.validate()

        async with PlanaDB.get_session() as session:
            session.add(self)
            await session.commit()
            await session.refresh(self)
            return self

    @db_operation
    async def refresh(self) -> "PlanaDBModel":
        """Refresh model instance with latest data from plana.database."""
        primary_keys = [pk.name for pk in self.__table__.primary_key]
        if not any(getattr(self, pk, None) for pk in primary_keys):
            raise ValueError("Cannot refresh instance without primary key value")

        async with PlanaDB.get_session() as session:
            # Merge the instance with the current session
            merged_instance = await session.merge(self)
            await session.refresh(merged_instance)

            # Update current instance attributes with refreshed data
            for column in self.__table__.columns:
                setattr(self, column.name, getattr(merged_instance, column.name))

            return self

    # ========== Query Operations ==========

    @classmethod
    @db_operation
    async def get(cls: Type[T], id: Any) -> Optional[T]:
        """Get model instance by primary key."""
        async with PlanaDB.get_session() as session:
            return await session.get(cls, id)

    @classmethod
    @db_operation
    async def get_by(cls: Type[T], **kwargs: Any) -> Optional[T]:
        """Get single model instance by attributes."""
        async with PlanaDB.get_session() as session:
            result = await session.execute(select(cls).filter_by(**kwargs))
            return result.unique().scalar_one_or_none()

    @classmethod
    @db_operation
    async def filter(
        cls: Type[T],
        *conditions: ColumnElement,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[Any] = None,
        load_relations: Optional[List[str]] = None,
    ) -> List[T]:
        """
        Filter model instances with SQLAlchemy conditions.

        Args:
            *conditions: SQLAlchemy filter conditions
            limit: Maximum number of results
            offset: Number of results to skip
            order_by: Column or expression to order by
            load_relations: List of relationship names to eager load
        """
        async with PlanaDB.get_session() as session:
            query = select(cls)

            if conditions:
                query = query.where(and_(*conditions))

            if load_relations:
                for relation in load_relations:
                    query = query.options(selectinload(getattr(cls, relation)))

            if order_by is not None:
                query = query.order_by(order_by)

            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)

            result = await session.execute(query)
            return list(result.unique().scalars().all())

    @classmethod
    @db_operation
    async def filter_by(
        cls: Type[T],
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[Any] = None,
        load_relations: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> List[T]:
        """
        Filter model instances by simple key-value pairs.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip
            order_by: Column or expression to order by
            load_relations: List of relationship names to eager load
            **kwargs: Column-value pairs for filtering
        """
        async with PlanaDB.get_session() as session:
            query = select(cls).filter_by(**kwargs)

            if load_relations:
                for relation in load_relations:
                    query = query.options(selectinload(getattr(cls, relation)))

            if order_by is not None:
                query = query.order_by(order_by)

            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)

            result = await session.execute(query)
            return list(result.unique().scalars().all())

    @classmethod
    @db_operation
    async def all(
        cls: Type[T],
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[Any] = None,
        load_relations: Optional[List[str]] = None,
    ) -> List[T]:
        """Get all model instances."""
        return await cls.filter_by(
            limit=limit,
            offset=offset,
            order_by=order_by,
            load_relations=load_relations,
        )

    @classmethod
    @db_operation
    async def first(cls: Type[T], **kwargs: Any) -> Optional[T]:
        """Get first model instance matching criteria."""
        results = await cls.filter_by(limit=1, **kwargs)
        return results[0] if results else None

    @classmethod
    @db_operation
    async def exists(cls: Type[T], **kwargs: Any) -> bool:
        """Check if model instance exists."""
        return await cls.first(**kwargs) is not None

    # ========== Count Operations ==========

    @classmethod
    @db_operation
    async def count(cls: Type[T], *conditions: ColumnElement) -> int:
        """Count model instances with SQLAlchemy conditions."""
        async with PlanaDB.get_session() as session:
            # Use the first primary key column for counting
            primary_key = list(cls.__table__.primary_key.columns)[0]
            query = select(func.count(primary_key))

            if conditions:
                query = query.where(and_(*conditions))

            result = await session.execute(query)
            return result.scalar()

    @classmethod
    @db_operation
    async def count_by(cls: Type[T], **kwargs: Any) -> int:
        """Count model instances by key-value pairs."""
        async with PlanaDB.get_session() as session:
            # Use the first primary key column for counting
            primary_key = list(cls.__table__.primary_key.columns)[0]
            query = select(func.count(primary_key)).filter_by(**kwargs)
            result = await session.execute(query)
            return result.scalar()

    # ========== Bulk Operations ==========

    @classmethod
    @db_operation
    async def bulk_create(
        cls: Type[T],
        data: List[Dict[str, Any]],
        chunk_size: int = 1000,
        validate_each: bool = True,
    ) -> List[T]:
        """Bulk create instances with optimal performance."""
        if not data:
            return []

        instances = []
        async with PlanaDB.get_session() as session:
            for i in range(0, len(data), chunk_size):
                chunk = data[i : i + chunk_size]
                chunk_instances = [cls(**item) for item in chunk]

                if validate_each:
                    for instance in chunk_instances:
                        await instance.validate()

                session.add_all(chunk_instances)
                instances.extend(chunk_instances)

            await session.commit()

            # Refresh all instances to get generated IDs
            for instance in instances:
                await session.refresh(instance)

        return instances

    @classmethod
    @db_operation
    async def bulk_update(
        cls: Type[T],
        updates: List[Dict[str, Any]],
        key_field: str = "id",
    ) -> int:
        """Bulk update instances by key field."""
        if not updates:
            return 0

        async with PlanaDB.get_session() as session:
            updated_count = 0
            for update_data in updates:
                key_value = update_data.pop(key_field)
                result = await session.execute(
                    select(cls).where(getattr(cls, key_field) == key_value)
                )
                instance = result.scalar_one_or_none()

                if instance:
                    for key, value in update_data.items():
                        setattr(instance, key, value)
                    updated_count += 1

            await session.commit()
            return updated_count

    @classmethod
    @db_operation
    async def bulk_delete(cls: Type[T], *conditions: ColumnElement) -> int:
        """Bulk delete instances matching conditions."""
        async with PlanaDB.get_session() as session:
            query = select(cls)
            if conditions:
                query = query.where(and_(*conditions))

            result = await session.execute(query)
            instances = result.scalars().all()

            for instance in instances:
                await session.delete(instance)

            await session.commit()
            return len(instances)

    # ========== Create or Update Operations ==========

    @classmethod
    @db_operation
    async def get_or_create(
        cls: Type[T], defaults: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> tuple[T, bool]:
        """Get existing instance or create new one."""
        instance = await cls.get_by(**kwargs)
        if instance:
            return instance, False

        # Create new instance
        create_data = {**kwargs}
        if defaults:
            create_data.update(defaults)

        instance = cls(**create_data)
        await instance.save()
        return instance, True

    @classmethod
    @db_operation
    async def update_or_create(
        cls: Type[T], defaults: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> tuple[T, bool]:
        """Update existing instance or create new one."""
        instance = await cls.get_by(**kwargs)
        if instance:
            if defaults:
                await instance.update(**defaults)
            return instance, False

        # Create new instance
        create_data = {**kwargs}
        if defaults:
            create_data.update(defaults)

        instance = cls(**create_data)
        await instance.save()
        return instance, True

    # ========== Utility Methods ==========

    async def validate(self) -> None:
        """Hook for model-specific validation logic."""
        pass

    def to_dict(
        self,
        exclude: Optional[List[str]] = None,
        convert_big_int: bool = True,
    ) -> Dict[str, Any]:
        """Convert model to dictionary.

        Args:
            exclude: List of column names to exclude
            convert_big_int: Whether to convert large integers to strings for browser support
        """
        exclude = exclude or []
        result = {}

        # Handle columns
        for c in self.__table__.columns:
            if c.name not in exclude:
                value = getattr(self, c.name)
                result[c.name] = self._serialize_value(value, convert_big_int)

        return result

    def _serialize_value(self, value: Any, convert_big_int: bool = True) -> Any:
        """Serialize a single value for dictionary conversion."""
        # Handle None values
        if value is None:
            return None

        # Convert datetime to ISO format string
        if isinstance(value, datetime):
            value = value.replace(tzinfo=timezone.utc)  # Remove timezone info
            return value.isoformat()

        # Convert BigInteger/large integers to string for better browser support
        if (
            convert_big_int
            and isinstance(value, int)
            and (value > 2**53 - 1 or value < -(2**53 - 1))
        ):
            return str(value)

        # Handle dictionaries recursively
        if isinstance(value, dict):
            return {k: self._serialize_value(v, convert_big_int) for k, v in value.items()}

        # Handle lists recursively
        if isinstance(value, (list, tuple)):
            return [self._serialize_value(item, convert_big_int) for item in value]

        # Return value as-is for other types
        return value

    def __repr__(self) -> str:
        """String representation of model."""
        primary_key = self.__table__.primary_key.columns.keys()[0]
        pk_value = getattr(self, primary_key, None)
        return f"<{self.__class__.__name__}(id={pk_value})>"
