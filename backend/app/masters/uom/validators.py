"""Unit of Measurement Validators. Row-level validation for CSV/Excel import."""

from __future__ import annotations

from typing import Any

from app.core.constants import RecordStatus
from app.core.exceptions import BadRequestException


def validate_uom_row(raw_row: dict[str, str], row_number: int) -> dict[str, Any]:
    """Validate one raw import row and return clean field kwargs, or raise on bad data."""
    code = (raw_row.get("code") or raw_row.get("Code") or raw_row.get("UOM Code") or "").strip().upper()
    name = (raw_row.get("name") or raw_row.get("UOM Name") or raw_row.get("Name") or "").strip()
    short_name = (raw_row.get("short_name") or raw_row.get("Short Name") or "").strip() or None

    if not name:
        raise BadRequestException(f"Row {row_number}: 'name' (UOM Name) is required.")

    if not code:
        code = (short_name or name).strip().upper().replace(" ", "_")[:20]

    status_raw = (raw_row.get("status") or raw_row.get("Status") or "active").strip().lower()
    try:
        status = RecordStatus(status_raw)
    except ValueError as exc:
        raise BadRequestException(
            f"Row {row_number}: invalid status {status_raw!r}. Must be 'active' or 'inactive'."
        ) from exc

    return {
        "code": code,
        "name": name,
        "short_name": short_name,
        "description": (raw_row.get("description") or raw_row.get("Description") or "").strip() or None,
        "status": status,
    }
