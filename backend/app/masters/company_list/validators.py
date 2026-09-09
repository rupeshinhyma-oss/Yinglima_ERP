"""Validation utilities for Company List data import."""

from __future__ import annotations

from typing import Any

from app.core.constants import RecordStatus
from app.core.exceptions import BadRequestException


def validate_company_row(row: dict[str, Any], index: int) -> dict[str, Any]:
    """Validate a single CSV/Excel row during bulk import."""
    name = str(
        row.get("name")
        or row.get("Organization Name")
        or row.get("organization_name")
        or row.get("company_name")
        or row.get("Company Name")
        or ""
    ).strip()
    if not name:
        raise BadRequestException(f"Row {index}: 'name' (Organization Name) is required.")

    code = str(row.get("code") or row.get("Organization Code") or row.get("Company Code") or "").strip() or None

    status_raw = str(row.get("status") or row.get("Status") or "active").strip().lower()
    if status_raw in ("inactive", "0", "disabled"):
        status = RecordStatus.INACTIVE
    else:
        status = RecordStatus.ACTIVE

    return {
        "name": name,
        "code": code,
        "status": status,
    }
