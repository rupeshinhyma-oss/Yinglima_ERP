"""
Trash Conflict Detection Helpers.

Provides helper utilities to detect whether an active record or a soft-deleted
record (in the Trash) conflicts with unique fields (such as name, code, company_name)
during record creation or update, raising structured ConflictException with
details so the frontend can offer one-click restore actions.
"""

from __future__ import annotations

import uuid
from typing import Any, Type

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException


async def check_trash_or_duplicate(
    session: AsyncSession,
    model_cls: Type[Any],
    *,
    entity_type: str,
    name: str | None = None,
    code: str | None = None,
    name_field: str = "name",
    code_field: str = "code",
    exclude_id: uuid.UUID | None = None,
    extra_filters: dict[str, Any] | None = None,
) -> None:
    """
    Check if a record with matching name or code already exists in the table.

    - If found and deleted_at is NOT None -> raises ConflictException with in_trash=True.
    - If found and deleted_at IS None -> raises standard ConflictException.
    """
    if name and str(name).strip() and hasattr(model_cls, name_field):
        col = getattr(model_cls, name_field)
        clean_name = str(name).strip()
        stmt = select(model_cls).where(func.lower(func.trim(col)) == clean_name.lower())
        if extra_filters:
            for k, v in extra_filters.items():
                if v is not None and hasattr(model_cls, k):
                    stmt = stmt.where(getattr(model_cls, k) == v)
        if exclude_id is not None and hasattr(model_cls, "id"):
            stmt = stmt.where(model_cls.id != exclude_id)
        result = await session.execute(stmt)
        existing = result.scalars().first()
        if existing is not None:
            if hasattr(existing, "deleted_at") and existing.deleted_at is not None:
                raise ConflictException(
                    f"{entity_type} '{clean_name}' already exists in the Trash.",
                    details={
                        "in_trash": True,
                        "trash_id": str(existing.id),
                        "entity_type": entity_type,
                        "name": getattr(existing, name_field, clean_name),
                        "code": getattr(existing, code_field, None),
                    },
                )
            raise ConflictException(
                f"{entity_type} name {clean_name!r} is already in use.",
                details={"existing": {"id": str(existing.id), "name": getattr(existing, name_field, clean_name)}},
            )

    if code and str(code).strip() and hasattr(model_cls, code_field):
        col = getattr(model_cls, code_field)
        clean_code = str(code).strip()
        stmt = select(model_cls).where(func.lower(func.trim(col)) == clean_code.lower())
        if extra_filters:
            for k, v in extra_filters.items():
                if v is not None and hasattr(model_cls, k):
                    stmt = stmt.where(getattr(model_cls, k) == v)
        if exclude_id is not None and hasattr(model_cls, "id"):
            stmt = stmt.where(model_cls.id != exclude_id)
        result = await session.execute(stmt)
        existing = result.scalars().first()
        if existing is not None:
            if hasattr(existing, "deleted_at") and existing.deleted_at is not None:
                raise ConflictException(
                    f"{entity_type} with code '{clean_code}' already exists in the Trash.",
                    details={
                        "in_trash": True,
                        "trash_id": str(existing.id),
                        "entity_type": entity_type,
                        "name": getattr(existing, name_field, None),
                        "code": getattr(existing, code_field, clean_code),
                    },
                )
            raise ConflictException(
                f"{entity_type} code {clean_code!r} is already in use.",
                details={"existing": {"id": str(existing.id), "code": getattr(existing, code_field, clean_code)}},
            )


async def code_exists_anywhere(
    session: AsyncSession,
    model_cls: Type[Any],
    code: str,
    *,
    code_field: str = "code",
    exclude_id: uuid.UUID | None = None,
    extra_filters: dict[str, Any] | None = None,
) -> bool:
    """Check if code exists anywhere in the table (active or soft-deleted)."""
    if not hasattr(model_cls, code_field):
        return False
    col = getattr(model_cls, code_field)
    clean_code = str(code).strip()
    stmt = select(model_cls.id).where(func.lower(func.trim(col)) == clean_code.lower())
    if extra_filters:
        for k, v in extra_filters.items():
            if v is not None and hasattr(model_cls, k):
                stmt = stmt.where(getattr(model_cls, k) == v)
    if exclude_id is not None and hasattr(model_cls, "id"):
        stmt = stmt.where(model_cls.id != exclude_id)
    result = await session.execute(stmt.limit(1))
    return result.scalar_one_or_none() is not None
