"""Database repository for Product Prices Directory."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.masters.product_prices.schemas import (
    AssignSupplierPricePayload,
    ProductPriceItem,
    ProductPriceSupplierItem,
    UpdatePricePayload,
)
from app.suppliers.models import SupplierProductLink


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ProductPriceRepository:
    """Repository handling database queries for product pricing."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_product_prices(
        self,
        *,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        category_id: uuid.UUID | None = None,
        sub_category_id: uuid.UUID | None = None,
        brand_id: uuid.UUID | None = None,
        has_price: bool | None = None,
        sort_by: str = "product_name_tally",
        sort_dir: str = "asc",
    ) -> tuple[list[ProductPriceItem], int]:
        """
        List paginated products with their lowest supplier quoted price.
        Returns (items, total_count).
        """
        page = max(1, page)
        page_size = max(1, min(200, page_size))
        offset = (page - 1) * page_size

        filter_clauses = ["p.deleted_at IS NULL"]
        params: dict[str, Any] = {"limit": page_size, "offset": offset}

        if category_id:
            filter_clauses.append("p.category_id = :category_id")
            params["category_id"] = str(category_id)

        if sub_category_id:
            filter_clauses.append("p.sub_category_id = :sub_category_id")
            params["sub_category_id"] = str(sub_category_id)

        if brand_id:
            filter_clauses.append("p.brand_id = :brand_id")
            params["brand_id"] = str(brand_id)

        if has_price is True:
            filter_clauses.append(
                "EXISTS (SELECT 1 FROM supplier_product_links spl WHERE spl.product_id = p.id AND spl.unit_price IS NOT NULL)"
            )
        elif has_price is False:
            filter_clauses.append(
                "NOT EXISTS (SELECT 1 FROM supplier_product_links spl WHERE spl.product_id = p.id AND spl.unit_price IS NOT NULL)"
            )

        if search and search.strip():
            term = f"%{search.strip()}%"
            filter_clauses.append(
                "("
                "p.product_code ILIKE :search_term OR "
                "p.product_name ILIKE :search_term OR "
                "p.product_name_tally ILIKE :search_term OR "
                "p.barcode ILIKE :search_term OR "
                "EXISTS (SELECT 1 FROM supplier_product_links spl "
                "JOIN suppliers s ON s.id = spl.supplier_id "
                "WHERE spl.product_id = p.id AND s.company_name ILIKE :search_term AND s.deleted_at IS NULL)"
                ")"
            )
            params["search_term"] = term

        where_sql = " AND ".join(filter_clauses)

        # 1. Count query
        count_sql = f"SELECT COUNT(*) FROM products p WHERE {where_sql}"
        count_res = await self.session.execute(text(count_sql), params)
        total_count = count_res.scalar() or 0

        if total_count == 0:
            return [], 0

        # Determine order
        dir_clean = "DESC" if sort_dir.lower() == "desc" else "ASC"
        nulls_order = "NULLS LAST" if dir_clean == "ASC" else "NULLS FIRST"

        if sort_by == "best_price":
            order_sql = f"best.unit_price {dir_clean} {nulls_order}, p.product_name_tally ASC"
            paginate_in_cte = False
        elif sort_by == "product_code":
            order_sql = f"p.product_code {dir_clean} {nulls_order}"
            paginate_in_cte = True
        elif sort_by == "created_at":
            order_sql = f"p.created_at {dir_clean}"
            paginate_in_cte = True
        else:
            order_sql = f"p.product_name_tally {dir_clean}"
            paginate_in_cte = True

        if paginate_in_cte:
            # Fast path: paginate products first, then join aggregates for those 50 rows
            data_sql = f"""
                WITH paged AS (
                    SELECT
                        p.id,
                        p.product_code,
                        p.product_name,
                        p.product_name_tally,
                        p.barcode,
                        p.category_id,
                        p.sub_category_id,
                        p.brand_id,
                        p.uom_id,
                        p.images
                    FROM products p
                    WHERE {where_sql}
                    ORDER BY {order_sql}
                    LIMIT :limit OFFSET :offset
                )
                SELECT
                    p.id,
                    p.product_code,
                    p.product_name,
                    p.product_name_tally,
                    p.barcode,
                    p.category_id,
                    pc.name AS category_name,
                    p.sub_category_id,
                    psc.name AS sub_category_name,
                    p.brand_id,
                    b.name AS brand_name,
                    p.uom_id,
                    u.code AS uom_code,
                    p.images,
                    COALESCE(agg.supplier_count, 0) AS supplier_count,
                    best.id AS primary_link_id,
                    best.supplier_id AS primary_supplier_id,
                    best.company_name AS primary_supplier_name,
                    best.unit_price AS best_price,
                    best.currency AS best_currency
                FROM paged p
                LEFT JOIN product_categories pc ON pc.id = p.category_id
                LEFT JOIN product_sub_categories psc ON psc.id = p.sub_category_id
                LEFT JOIN brands b ON b.id = p.brand_id
                LEFT JOIN units_of_measurement u ON u.id = p.uom_id
                LEFT JOIN (
                    SELECT
                        spl.product_id,
                        COUNT(spl.id) AS supplier_count
                    FROM supplier_product_links spl
                    JOIN suppliers s ON s.id = spl.supplier_id AND s.deleted_at IS NULL
                    WHERE spl.product_id IN (SELECT id FROM paged)
                    GROUP BY spl.product_id
                ) agg ON agg.product_id = p.id
                LEFT JOIN (
                    SELECT DISTINCT ON (spl.product_id)
                        spl.product_id,
                        spl.id,
                        spl.supplier_id,
                        s.company_name,
                        spl.unit_price,
                        spl.currency
                    FROM supplier_product_links spl
                    JOIN suppliers s ON s.id = spl.supplier_id AND s.deleted_at IS NULL
                    WHERE spl.product_id IN (SELECT id FROM paged)
                      AND spl.unit_price IS NOT NULL
                    ORDER BY spl.product_id, spl.unit_price ASC, spl.updated_at DESC
                ) best ON best.product_id = p.id
                ORDER BY {order_sql};
            """
        else:
            # Sort by best_price across all filtered products
            data_sql = f"""
                SELECT
                    p.id,
                    p.product_code,
                    p.product_name,
                    p.product_name_tally,
                    p.barcode,
                    p.category_id,
                    pc.name AS category_name,
                    p.sub_category_id,
                    psc.name AS sub_category_name,
                    p.brand_id,
                    b.name AS brand_name,
                    p.uom_id,
                    u.code AS uom_code,
                    p.images,
                    COALESCE(agg.supplier_count, 0) AS supplier_count,
                    best.id AS primary_link_id,
                    best.supplier_id AS primary_supplier_id,
                    best.company_name AS primary_supplier_name,
                    best.unit_price AS best_price,
                    best.currency AS best_currency
                FROM products p
                LEFT JOIN product_categories pc ON pc.id = p.category_id
                LEFT JOIN product_sub_categories psc ON psc.id = p.sub_category_id
                LEFT JOIN brands b ON b.id = p.brand_id
                LEFT JOIN units_of_measurement u ON u.id = p.uom_id
                LEFT JOIN (
                    SELECT
                        spl.product_id,
                        COUNT(spl.id) AS supplier_count
                    FROM supplier_product_links spl
                    JOIN suppliers s ON s.id = spl.supplier_id AND s.deleted_at IS NULL
                    GROUP BY spl.product_id
                ) agg ON agg.product_id = p.id
                LEFT JOIN (
                    SELECT DISTINCT ON (spl.product_id)
                        spl.product_id,
                        spl.id,
                        spl.supplier_id,
                        s.company_name,
                        spl.unit_price,
                        spl.currency
                    FROM supplier_product_links spl
                    JOIN suppliers s ON s.id = spl.supplier_id AND s.deleted_at IS NULL
                    WHERE spl.unit_price IS NOT NULL
                    ORDER BY spl.product_id, spl.unit_price ASC, spl.updated_at DESC
                ) best ON best.product_id = p.id
                WHERE {where_sql}
                ORDER BY {order_sql}
                LIMIT :limit OFFSET :offset;
            """

        data_res = await self.session.execute(text(data_sql), params)
        rows = data_res.fetchall()

        items: list[ProductPriceItem] = []
        for r in rows:
            m = r._mapping
            items.append(
                ProductPriceItem(
                    product_id=m["id"],
                    product_code=m["product_code"],
                    product_name=m["product_name"],
                    product_name_tally=m["product_name_tally"],
                    barcode=m["barcode"],
                    category_id=m["category_id"],
                    category_name=m["category_name"],
                    sub_category_id=m["sub_category_id"],
                    sub_category_name=m["sub_category_name"],
                    brand_id=m["brand_id"],
                    brand_name=m["brand_name"],
                    uom_id=m["uom_id"],
                    uom_code=m["uom_code"],
                    images=m["images"] if isinstance(m["images"], list) else None,
                    best_price=float(m["best_price"]) if m["best_price"] is not None else None,
                    best_currency=m["best_currency"],
                    primary_supplier_id=m["primary_supplier_id"],
                    primary_supplier_name=m["primary_supplier_name"],
                    primary_link_id=m["primary_link_id"],
                    supplier_count=int(m["supplier_count"] or 0),
                    has_price=m["best_price"] is not None,
                )
            )

        return items, total_count

    async def get_product_suppliers(self, product_id: uuid.UUID) -> list[ProductPriceSupplierItem]:
        """Fetch all suppliers linked to a product with their quote details."""
        query = text("""
            SELECT
                spl.id AS link_id,
                spl.product_id,
                spl.supplier_id,
                s.company_name AS supplier_name,
                NULL AS supplier_code,
                s.contact_calling_number,
                s.contact_whatsapp_number,
                s.contact_wechat_number,
                c.name AS city_name,
                st.name AS state_name,
                co.name AS country_name,
                spl.unit_price,
                spl.currency,
                spl.moq,
                spl.notes,
                spl.updated_at,
                spl.created_at
            FROM supplier_product_links spl
            JOIN suppliers s ON s.id = spl.supplier_id AND s.deleted_at IS NULL
            LEFT JOIN cities c ON c.id = s.city_id
            LEFT JOIN states st ON st.id = s.state_id
            LEFT JOIN countries co ON co.id = s.country_id
            WHERE spl.product_id = :product_id
            ORDER BY spl.unit_price ASC NULLS LAST, spl.updated_at DESC;
        """)

        res = await self.session.execute(query, {"product_id": str(product_id)})
        rows = res.fetchall()

        items: list[ProductPriceSupplierItem] = []
        for r in rows:
            m = r._mapping
            items.append(
                ProductPriceSupplierItem(
                    link_id=m["link_id"],
                    product_id=m["product_id"],
                    supplier_id=m["supplier_id"],
                    supplier_name=m["supplier_name"],
                    supplier_code=m["supplier_code"],
                    contact_calling_number=m["contact_calling_number"],
                    contact_whatsapp_number=m["contact_whatsapp_number"],
                    contact_wechat_number=m["contact_wechat_number"],
                    city_name=m["city_name"],
                    state_name=m["state_name"],
                    country_name=m["country_name"],
                    unit_price=float(m["unit_price"]) if m["unit_price"] is not None else None,
                    currency=m["currency"] or "CNY",
                    moq=float(m["moq"]) if m["moq"] is not None else None,
                    notes=m["notes"],
                    updated_at=m["updated_at"],
                    created_at=m["created_at"],
                )
            )
        return items

    async def assign_supplier_price(self, payload: AssignSupplierPricePayload) -> uuid.UUID:
        """
        Insert or update a supplier-product quote link.
        Uses PostgreSQL ON CONFLICT (supplier_id, product_id) DO UPDATE.
        Returns the link_id.
        """
        now = _utcnow()
        query = text("""
            INSERT INTO supplier_product_links (
                id, supplier_id, product_id, unit_price, currency, moq, notes, created_at, updated_at
            )
            VALUES (
                :id, :supplier_id, :product_id, :unit_price, :currency, :moq, :notes, :created_at, :updated_at
            )
            ON CONFLICT (supplier_id, product_id)
            DO UPDATE SET
                unit_price = EXCLUDED.unit_price,
                currency = EXCLUDED.currency,
                moq = EXCLUDED.moq,
                notes = COALESCE(EXCLUDED.notes, supplier_product_links.notes),
                updated_at = EXCLUDED.updated_at
            RETURNING id;
        """)

        res = await self.session.execute(
            query,
            {
                "id": str(uuid.uuid4()),
                "supplier_id": str(payload.supplier_id),
                "product_id": str(payload.product_id),
                "unit_price": payload.unit_price,
                "currency": (payload.currency or "CNY").upper(),
                "moq": payload.moq,
                "notes": payload.notes,
                "created_at": now,
                "updated_at": now,
            },
        )
        row = res.fetchone()
        return row[0]

    async def update_supplier_price(self, link_id: uuid.UUID, payload: UpdatePricePayload) -> None:
        """Inline update of a supplier link's unit price, currency, moq, or notes."""
        updates: list[str] = ["updated_at = :updated_at"]
        params: dict[str, Any] = {"link_id": str(link_id), "updated_at": _utcnow()}

        if payload.unit_price is not None:
            updates.append("unit_price = :unit_price")
            params["unit_price"] = payload.unit_price

        if payload.currency is not None:
            updates.append("currency = :currency")
            params["currency"] = payload.currency.upper()

        if payload.moq is not None:
            updates.append("moq = :moq")
            params["moq"] = payload.moq

        if payload.notes is not None:
            updates.append("notes = :notes")
            params["notes"] = payload.notes

        query = text(f"""
            UPDATE supplier_product_links
            SET {", ".join(updates)}
            WHERE id = :link_id;
        """)
        res = await self.session.execute(query, params)
        if res.rowcount == 0:
            raise NotFoundException("Supplier price link not found")

    async def delete_supplier_price(self, link_id: uuid.UUID) -> None:
        """Remove a supplier price link."""
        query = text("DELETE FROM supplier_product_links WHERE id = :link_id;")
        res = await self.session.execute(query, {"link_id": str(link_id)})
        if res.rowcount == 0:
            raise NotFoundException("Supplier price link not found")

    async def get_link_by_id(self, link_id: uuid.UUID) -> dict[str, Any] | None:
        """Fetch link by id."""
        query = text("""
            SELECT id, supplier_id, product_id, unit_price, currency, moq, notes, updated_at
            FROM supplier_product_links
            WHERE id = :link_id;
        """)
        res = await self.session.execute(query, {"link_id": str(link_id)})
        row = res.fetchone()
        return dict(row._mapping) if row else None

    async def list_suppliers_lookup(self) -> list[dict[str, Any]]:
        """Fast, lightweight lookup of suppliers for price assignment dropdowns."""
        sql = text("""
            SELECT id, company_name, supplier_type
            FROM suppliers
            WHERE is_active = true
            ORDER BY company_name ASC
        """)
        res = await self.session.execute(sql)
        return [
            {"id": str(r[0]), "company_name": r[1], "supplier_type": r[2]}
            for r in res.fetchall()
        ]

