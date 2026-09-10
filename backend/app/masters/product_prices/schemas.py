"""Pydantic Schemas for Product Prices Directory."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ProductPriceItem(BaseModel):
    """Product summary row with best supplier price."""

    model_config = ConfigDict(from_attributes=True)

    product_id: uuid.UUID
    product_code: str | None = None
    product_name: str
    product_name_tally: str
    barcode: str | None = None
    category_id: uuid.UUID | None = None
    category_name: str | None = None
    sub_category_id: uuid.UUID | None = None
    sub_category_name: str | None = None
    brand_id: uuid.UUID | None = None
    brand_name: str | None = None
    uom_id: uuid.UUID | None = None
    uom_code: str | None = None
    images: list[str] | None = None
    best_price: float | None = None
    best_currency: str | None = None
    primary_supplier_id: uuid.UUID | None = None
    primary_supplier_name: str | None = None
    primary_link_id: uuid.UUID | None = None
    supplier_count: int = 0
    has_price: bool = False


class ProductPriceSupplierItem(BaseModel):
    """Supplier quote and details for an individual product."""

    model_config = ConfigDict(from_attributes=True)

    link_id: uuid.UUID
    product_id: uuid.UUID
    supplier_id: uuid.UUID
    supplier_name: str
    supplier_code: str | None = None
    contact_calling_number: str | None = None
    contact_whatsapp_number: str | None = None
    contact_wechat_number: str | None = None
    city_name: str | None = None
    state_name: str | None = None
    country_name: str | None = None
    unit_price: float | None = None
    currency: str = "CNY"
    moq: float | None = None
    notes: str | None = None
    updated_at: datetime | None = None
    created_at: datetime | None = None


class AssignSupplierPricePayload(BaseModel):
    """Payload to link/update a supplier price for a product."""

    product_id: uuid.UUID
    supplier_id: uuid.UUID
    unit_price: float | None = None
    currency: str = Field(default="CNY", max_length=10)
    moq: float | None = None
    notes: str | None = None


class UpdatePricePayload(BaseModel):
    """Payload to inline-edit a price link."""

    unit_price: float | None = None
    currency: str | None = Field(default=None, max_length=10)
    moq: float | None = None
    notes: str | None = None


class PriceImportSummary(BaseModel):
    """Summary of universal bulk price import."""

    total_rows: int = 0
    created: int = 0
    updated: int = 0
    failed: int = 0
    errors: list[dict[str, Any]] = Field(default_factory=list)
