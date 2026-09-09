"""Product Category Validators. Row-level validation for CSV/Excel import."""

from __future__ import annotations

from typing import Any

from app.core.constants import RecordStatus
from app.core.exceptions import BadRequestException


def validate_product_category_row(raw_row: dict[str, str], row_number: int) -> dict[str, Any]:
    """Validate one raw import row and return clean field kwargs, or raise on bad data."""
    name = (raw_row.get("name") or raw_row.get("Category Name") or raw_row.get("category_name") or raw_row.get("Category") or "").strip()
    code = (raw_row.get("code") or raw_row.get("Category Code") or raw_row.get("category_code") or "").strip()

    if not name:
        raise BadRequestException(f"Row {row_number}: 'name' (Category Name) is required.")

    status_raw = (raw_row.get("status") or raw_row.get("Status") or "active").strip().lower()
    try:
        status = RecordStatus(status_raw)
    except ValueError as exc:
        raise BadRequestException(
            f"Row {row_number}: invalid status {status_raw!r}. Must be 'active' or 'inactive'."
        ) from exc

    return {
        "code": code or None,
        "name": name,
        "description": (raw_row.get("description") or raw_row.get("Description") or "").strip() or None,
        "status": status,
    }
