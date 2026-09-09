"""SupplierType Validators."""

from __future__ import annotations

from typing import Any

from app.core.constants import RecordStatus
from app.core.exceptions import BadRequestException


def validate_supplier_type_row(raw_row: dict[str, str], row_number: int) -> dict[str, Any]:
    """Validate one raw import row."""
    name = (
        raw_row.get("name")
        or raw_row.get("Supplier Type Name")
        or raw_row.get("supplier_type_name")
        or raw_row.get("Supplier Type")
        or ""
    ).strip()
    code = (raw_row.get("code") or raw_row.get("Supplier Type Code") or raw_row.get("supplier_type_code") or "").strip()

    if not name:
        raise BadRequestException(f"Row {row_number}: 'name' (Supplier Type Name) is required.")

    status_raw = (raw_row.get("status") or raw_row.get("Status") or "active").strip().lower()
    try:
        status = RecordStatus(status_raw)
    except ValueError as exc:
        raise BadRequestException(
            f"Row {row_number}: invalid status {status_raw!r}. Must be 'active' or 'inactive'."
        ) from exc

    return {
        "name": name,
        "code": code or f"ST-{name.upper().replace(' ', '_')[:10]}",
        "description": (raw_row.get("description") or raw_row.get("Description") or "").strip() or None,
        "status": status,
    }
