"""HSN Validators. Row-level validation for CSV/Excel import."""

from __future__ import annotations

from typing import Any

from app.core.constants import RecordStatus
from app.core.exceptions import BadRequestException


def validate_hsn_row(raw_row: dict[str, str], row_number: int) -> dict[str, Any]:
    """Validate one raw import row and return clean field kwargs, or raise on bad data."""
    code = (raw_row.get("code") or raw_row.get("HSN Code") or raw_row.get("HSN") or "").strip()

    if not code:
        raise BadRequestException(f"Row {row_number}: 'code' (HSN Code) is required.")

    gst_raw = (raw_row.get("gst_percent") or raw_row.get("GST %") or raw_row.get("gst") or "0").strip().replace("%", "")
    try:
        gst_percent = float(gst_raw)
    except ValueError as exc:
        raise BadRequestException(f"Row {row_number}: 'gst_percent' must be numeric.") from exc
    if gst_percent < 0 or gst_percent > 100:
        raise BadRequestException(f"Row {row_number}: 'gst_percent' must be between 0 and 100.")

    refund_vat_raw = (
        raw_row.get("refund_vat_percent")
        or raw_row.get("Refund VAT %")
        or raw_row.get("refund_vat")
        or "0"
    ).strip().replace("%", "")
    try:
        refund_vat_percent = float(refund_vat_raw)
    except ValueError as exc:
        raise BadRequestException(f"Row {row_number}: 'refund_vat_percent' must be numeric.") from exc
    if refund_vat_percent < 0 or refund_vat_percent > 100:
        raise BadRequestException(f"Row {row_number}: 'refund_vat_percent' must be between 0 and 100.")

    status_raw = (raw_row.get("status") or raw_row.get("Status") or "active").strip().lower()
    try:
        status = RecordStatus(status_raw)
    except ValueError as exc:
        raise BadRequestException(
            f"Row {row_number}: invalid status {status_raw!r}. Must be 'active' or 'inactive'."
        ) from exc

    return {
        "code": code,
        "description": (raw_row.get("description") or raw_row.get("Description") or "").strip() or None,
        "gst_percent": gst_percent,
        "refund_vat_percent": refund_vat_percent,
        "status": status,
    }
