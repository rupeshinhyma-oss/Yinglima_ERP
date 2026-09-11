"""Product Prices Router.

API endpoints for Product Price Directory:
- List products with lowest quoted prices (server-side pagination, search, filters)
- Sub-table supplier price listing
- Inline price editing & supplier assignment
- Bulk import & export
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, File, Query, Request, Response, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.service import CurrentUser
from app.core.logging import get_logger
from app.core.responses import build_success_response
from app.database.session import get_db_session
from app.masters.product_prices.schemas import (
    AssignSupplierPricePayload,
    ProductPriceItem,
    ProductPriceSupplierItem,
    UpdatePricePayload,
)
from app.masters.product_prices.service import ProductPriceService
from app.rbac.dependencies import require_permission

logger = get_logger(__name__)

router = APIRouter(prefix="/inventory/product-prices", tags=["Inventory - Product Prices"])


def get_service(session: AsyncSession = Depends(get_db_session)) -> ProductPriceService:
    return ProductPriceService(session)


@router.get("", summary="List products with their best supplier prices")
async def list_product_prices(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    search: str | None = Query(default=None),
    category_id: uuid.UUID | None = Query(default=None),
    sub_category_id: uuid.UUID | None = Query(default=None),
    brand_id: uuid.UUID | None = Query(default=None),
    has_price: bool | None = Query(default=None),
    sort_by: str = Query(default="product_name_tally"),
    sort_dir: str = Query(default="asc"),
    service: ProductPriceService = Depends(get_service),
    _current_user: CurrentUser = Depends(require_permission("product.view")),
) -> dict:
    items, total = await service.list_prices(
        page=page,
        page_size=page_size,
        search=search,
        category_id=category_id,
        sub_category_id=sub_category_id,
        brand_id=brand_id,
        has_price=has_price,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )

    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return build_success_response(
        data=[item.model_dump() for item in items],
        meta={
            "page": page,
            "page_size": page_size,
            "total_items": total,
            "total_pages": total_pages,
        },
        request_id=getattr(request.state, "request_id", "-"),
    )


@router.get("/suppliers-lookup", summary="Lightweight active suppliers lookup for pricing catalog")
async def get_suppliers_lookup(
    request: Request,
    service: ProductPriceService = Depends(get_service),
    _current_user: CurrentUser = Depends(require_permission("product.view")),
) -> dict:
    suppliers = await service.list_suppliers_lookup()
    return build_success_response(
        data=suppliers,
        request_id=getattr(request.state, "request_id", "-"),
    )


@router.get("/{product_id}/suppliers", summary="Get all suppliers and quotes for a product")
async def get_product_suppliers(
    request: Request,
    product_id: uuid.UUID,
    service: ProductPriceService = Depends(get_service),
    _current_user: CurrentUser = Depends(require_permission("product.view")),
) -> dict:
    suppliers = await service.get_product_suppliers(product_id)
    return build_success_response(
        data=[s.model_dump() for s in suppliers],
        request_id=getattr(request.state, "request_id", "-"),
    )


@router.post("/assign", summary="Assign or update supplier price for a product", status_code=status.HTTP_201_CREATED)
async def assign_supplier_price(
    request: Request,
    payload: AssignSupplierPricePayload,
    service: ProductPriceService = Depends(get_service),
    _current_user: CurrentUser = Depends(require_permission("product.update")),
) -> dict:
    link_id = await service.assign_price(payload)
    return build_success_response(
        data={"link_id": str(link_id), "message": "Supplier price successfully assigned"},
        request_id=getattr(request.state, "request_id", "-"),
    )


@router.patch("/{link_id}", summary="Inline update price or terms for a supplier link")
async def update_supplier_price(
    request: Request,
    link_id: uuid.UUID,
    payload: UpdatePricePayload,
    service: ProductPriceService = Depends(get_service),
    _current_user: CurrentUser = Depends(require_permission("product.update")),
) -> dict:
    await service.update_price(link_id, payload)
    return build_success_response(
        data={"link_id": str(link_id), "message": "Price updated successfully"},
        request_id=getattr(request.state, "request_id", "-"),
    )


@router.delete("/{link_id}", summary="Remove supplier pricing link")
async def delete_supplier_price(
    request: Request,
    link_id: uuid.UUID,
    service: ProductPriceService = Depends(get_service),
    _current_user: CurrentUser = Depends(require_permission("product.update")),
) -> dict:
    await service.delete_price(link_id)
    return build_success_response(
        data={"message": "Supplier price removed successfully"},
        request_id=getattr(request.state, "request_id", "-"),
    )


@router.get("/export", summary="Export product prices to Excel or CSV")
async def export_product_prices(
    format: str = Query(default="xlsx", regex="^(xlsx|csv)$"),
    search: str | None = Query(default=None),
    category_id: uuid.UUID | None = Query(default=None),
    sub_category_id: uuid.UUID | None = Query(default=None),
    brand_id: uuid.UUID | None = Query(default=None),
    has_price: bool | None = Query(default=None),
    service: ProductPriceService = Depends(get_service),
    _current_user: CurrentUser = Depends(require_permission("product.export")),
) -> Response:
    content, media_type, filename = await service.export_prices(
        file_format=format,
        search=search,
        category_id=category_id,
        sub_category_id=sub_category_id,
        brand_id=brand_id,
        has_price=has_price,
    )
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/sample-template", summary="Download bulk price import template")
async def download_price_import_template(
    service: ProductPriceService = Depends(get_service),
    _current_user: CurrentUser = Depends(require_permission("product.import")),
) -> Response:
    content, media_type, filename = await service.generate_template()
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/import", summary="Bulk import product prices from Excel")
async def import_product_prices(
    request: Request,
    file: UploadFile = File(...),
    service: ProductPriceService = Depends(get_service),
    _current_user: CurrentUser = Depends(require_permission("product.import")),
) -> dict:
    content = await file.read()
    summary = await service.import_prices(content)
    return build_success_response(
        data=summary.model_dump(),
        request_id=getattr(request.state, "request_id", "-"),
    )
