"""
Inquiry Service.

Business logic for the Inquiry (Requirement) workflow, encoding the
document's rules:

- Product Name / Quantity / Status are mandatory; Brand Preference and
  Product Specs/Remarks are optional (document: "these 2 fields
  Optional, Rest all Mandatory").
- UOM is copied from the selected Product automatically, never entered
  by the user directly (document: "UOM to reflect automatically as per
  inventory master of that item").
- If the selected Product has ``license_certificate_required`` set, the
  item is flagged so the list can highlight it in red and surface the
  requirement in its remarks (document: "highlight in RED colour and
  show that in Remark in List").
- Proposed/Approved Date and Proposed/Approved By are always
  auto-generated from the acting user, never accepted as input (document:
  "field not needed, but auto generated from user login").
- A consignment's rollup status is Proposed / Partial Approved / Fully
  Approved depending on its items' individual statuses.
- Bulk "mark as Tally Entry Posted" is supported across multiple items in
  one call (document: "some easy way to select and change multiple items
  to 'Posted'").
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from app.buyers.repository import BuyerRepository
from app.core.exceptions import BadRequestException, ConflictException, NotFoundException
from app.inquiries.models import (
    ConsignmentCode,
    Inquiry,
    InquiryConsignmentStatus,
    InquiryItem,
    InquiryItemStatus,
    Quotation,
    QuotationStatus,
    RFQ,
)
from app.inquiries.repository import (
    ConsignmentCodeRepository,
    InquiryItemRepository,
    InquiryRepository,
    QuotationRepository,
    RFQRepository,
)
from app.inquiries.schemas import QuotationCreate, QuotationUpdate, RFQCreate
from app.masters.products.repository import ProductRepository
from app.suppliers.repository import SupplierRepository


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class InquiryService:
    """Orchestrates the Inquiry (Requirement) workflow on top of its repositories."""

    def __init__(
        self,
        inquiry_repository: InquiryRepository,
        item_repository: InquiryItemRepository,
        consignment_code_repository: ConsignmentCodeRepository,
        buyer_repository: BuyerRepository,
        product_repository: ProductRepository,
        quotation_repository: QuotationRepository | None = None,
        rfq_repository: RFQRepository | None = None,
        supplier_repository: SupplierRepository | None = None,
    ) -> None:
        self.inquiry_repository = inquiry_repository
        self.item_repository = item_repository
        self.consignment_code_repository = consignment_code_repository
        self.buyer_repository = buyer_repository
        self.product_repository = product_repository
        self.quotation_repository = quotation_repository
        self.rfq_repository = rfq_repository
        self.supplier_repository = supplier_repository

    # ------------------------------------------------------------------
    # Consignment Codes (admin-managed master)
    # ------------------------------------------------------------------

    async def create_consignment_code(
        self, *, code: str, label: str | None, buyer_id: uuid.UUID, branch_id: str | None = None
    ) -> ConsignmentCode:
        """Document: "Master to create and choose from dropdown menu"."""
        code = code.strip().upper()
        if not code:
            raise BadRequestException("Consignment code is required.")
        if await self.buyer_repository.get_by_id(buyer_id) is None:
            raise BadRequestException("The specified buyer does not exist.")
        if await self.consignment_code_repository.get_by_code(code):
            raise ConflictException(f"Consignment code {code!r} already exists.")
        return await self.consignment_code_repository.create(code=code, label=label, buyer_id=buyer_id, branch_id=branch_id)

    async def list_consignment_codes(self, *, buyer_id: uuid.UUID | None = None) -> list[ConsignmentCode]:
        if buyer_id is not None:
            return await self.consignment_code_repository.list_for_buyer(buyer_id)
        return await self.consignment_code_repository.list(limit=1000)

    async def deactivate_consignment_code(self, consignment_code_id: uuid.UUID) -> ConsignmentCode:
        code = await self.consignment_code_repository.get_by_id(consignment_code_id)
        if code is None:
            raise NotFoundException("Consignment code not found.")
        from app.core.constants import RecordStatus

        return await self.consignment_code_repository.update(code, status=RecordStatus.INACTIVE)

    # ------------------------------------------------------------------
    # Layer 1: consignments, company-wise summary
    # ------------------------------------------------------------------

    async def get_inquiry_or_raise(self, inquiry_id: uuid.UUID) -> Inquiry:
        inquiry = await self.inquiry_repository.get_by_id(inquiry_id)
        if inquiry is None:
            raise NotFoundException("Inquiry (consignment) not found.")
        return inquiry

    async def get_or_create_consignment(
        self, *, buyer_id: uuid.UUID, consignment_code_id: uuid.UUID, user_id: uuid.UUID
    ) -> Inquiry:
        """
        Fetch the consignment for (buyer, consignment_code), creating it on first use.

        A consignment header only really matters once it has at least one
        item; rather than force a separate "create consignment" step
        before "add item" (which the document never describes as a
        distinct action), the header is created transparently the first
        time an item is added against a given buyer+code pair.
        """
        if await self.buyer_repository.get_by_id(buyer_id) is None:
            raise BadRequestException("The specified buyer does not exist.")
        code = await self.consignment_code_repository.get_by_id(consignment_code_id)
        if code is None:
            raise BadRequestException("The specified consignment code does not exist.")
        if code.buyer_id != buyer_id:
            raise BadRequestException("This consignment code does not belong to the specified buyer.")

        existing = await self.inquiry_repository.get_by_buyer_and_code(buyer_id, consignment_code_id)
        if existing is not None:
            return existing
        return await self.inquiry_repository.create(
            buyer_id=buyer_id, consignment_code_id=consignment_code_id, created_by=user_id
        )

    async def list_companies_summary(self) -> list[dict]:
        """
        Layer 1, company-wise: one row per buyer with at least one consignment.
        Computed via a single fast query across buyers, inquiries, and codes.
        """
        return await self.inquiry_repository.get_all_company_summaries()

    async def list_consignments_for_buyer(self, buyer_id: uuid.UUID) -> list[dict]:
        """Layer 1 inside one company: every consignment code for that buyer (document: "FB1, FB2...")."""
        if await self.buyer_repository.get_by_id(buyer_id) is None:
            raise NotFoundException("Buyer not found.")
        return await self.inquiry_repository.list_consignments_with_details_for_buyer(buyer_id)

    async def get_inquiry_with_details(self, inquiry_id: uuid.UUID) -> dict:
        """Fetch consignment with joined buyer, code, and enriched items."""
        inquiry_dict = await self.inquiry_repository.get_inquiry_with_details(inquiry_id)
        if inquiry_dict is None:
            raise NotFoundException("Inquiry (consignment) not found.")
        items = await self.item_repository.list_for_inquiry_with_details(inquiry_id)
        inquiry_dict["items"] = items
        return inquiry_dict

    async def export_consignment(self, inquiry_id: uuid.UUID, file_format: str = "xlsx") -> bytes:
        """
        Export all line items for a specific consignment to CSV or XLSX
        with enriched product, UOM, and supplier quotation details.
        """
        from app.masters.import_export import build_csv_export, build_excel_export

        inquiry_data = await self.get_inquiry_with_details(inquiry_id)
        consignment_code = inquiry_data.get("consignment_code") or "N/A"
        buyer_name = inquiry_data.get("buyer_name") or "N/A"
        items = inquiry_data.get("items") or []

        headers = [
            "Sr No",
            "Consignment Code",
            "Buyer Company",
            "Product Code",
            "Product Name",
            "Quantity",
            "UOM",
            "Brand Preference",
            "Product Specs / Remarks",
            "License Required",
            "Item Status",
            "Tally Entry Posted",
            "Quotation Count",
            "Best Quote Price",
            "Best Quote Currency",
            "Selected Supplier",
            "Procurement Remarks",
        ]

        rows: list[dict[str, Any]] = []
        for idx, item in enumerate(items, start=1):
            item_id = item.get("id")
            best_quote_price = ""
            best_quote_currency = ""
            selected_supplier = ""

            if self.quotation_repository and item_id:
                try:
                    quotes = await self.quotation_repository.list_for_item_with_details(item_id)
                    if quotes:
                        # Prioritize approved quotation, otherwise lowest unit price
                        approved_quotes = [
                            q for q in quotes if q.get("status") in (QuotationStatus.APPROVED.value, "approved")
                        ]
                        target_quote = (
                            approved_quotes[0]
                            if approved_quotes
                            else min(
                                quotes,
                                key=lambda q: float(q.get("unit_price") or float("inf")),
                            )
                        )
                        if target_quote:
                            u_price = target_quote.get("unit_price")
                            if u_price is not None:
                                best_quote_price = f"{float(u_price):,.2f}"
                            best_quote_currency = target_quote.get("currency") or "CNY"
                            selected_supplier = target_quote.get("supplier_name") or ""
                except Exception:
                    pass

            status_val = item.get("status")
            status_str = (
                status_val.value
                if hasattr(status_val, "value")
                else str(status_val or "proposed").capitalize()
            )

            rows.append(
                {
                    "Sr No": idx,
                    "Consignment Code": consignment_code,
                    "Buyer Company": buyer_name,
                    "Product Code": item.get("product_code") or "",
                    "Product Name": item.get("product_name") or item.get("product_name_tally") or "",
                    "Quantity": item.get("quantity") if item.get("quantity") is not None else "",
                    "UOM": item.get("uom_name") or item.get("uom_code") or "",
                    "Brand Preference": item.get("brand_preference") or "",
                    "Product Specs / Remarks": item.get("product_specs_remarks") or "",
                    "License Required": "Yes" if item.get("requires_license") else "No",
                    "Item Status": status_str,
                    "Tally Entry Posted": "Yes" if item.get("tally_entry_posted") else "No",
                    "Quotation Count": item.get("quotation_count") or 0,
                    "Best Quote Price": best_quote_price,
                    "Best Quote Currency": best_quote_currency,
                    "Selected Supplier": selected_supplier,
                    "Procurement Remarks": item.get("procurement_remarks") or "",
                }
            )

        sheet_title = f"{consignment_code} Items"[:31]
        if file_format.lower() == "csv":
            return build_csv_export(headers, rows)
        return build_excel_export(headers, rows, sheet_title=sheet_title)


    async def _refresh_rollup(self, inquiry_id: uuid.UUID) -> Inquiry:
        """Recompute and persist one consignment's Layer-1 rollup fields from its current items."""
        inquiry = await self.get_inquiry_or_raise(inquiry_id)
        rollup = await self.item_repository.compute_rollup(inquiry_id)
        return await self.inquiry_repository.update(
            inquiry,
            total_cbm=rollup["total_cbm"],
            total_weight=rollup["total_weight"],
            consignment_status=rollup["status"],
        )

    async def delete_consignment(self, inquiry_id: uuid.UUID) -> None:
        """Document: Layer-1 list Action "Delete"."""
        inquiry = await self.get_inquiry_or_raise(inquiry_id)
        await self.inquiry_repository.delete(inquiry)
        if inquiry.consignment_code_id:
            cc = await self.consignment_code_repository.get_by_id(inquiry.consignment_code_id)
            if cc:
                await self.consignment_code_repository.delete(cc)

    # ------------------------------------------------------------------
    # Layer 2: items within a consignment
    # ------------------------------------------------------------------

    async def list_items(self, inquiry_id: uuid.UUID) -> list[dict]:
        await self.get_inquiry_or_raise(inquiry_id)
        return await self.item_repository.list_for_inquiry_with_details(inquiry_id)

    async def get_item_or_raise(self, inquiry_id: uuid.UUID, item_id: uuid.UUID) -> InquiryItem:
        item = await self.item_repository.get_by_id(item_id)
        if item is None or item.inquiry_id != inquiry_id:
            raise NotFoundException("Inquiry item not found.")
        return item

    async def add_item(
        self,
        *,
        buyer_id: uuid.UUID,
        consignment_code_id: uuid.UUID,
        product_id: uuid.UUID,
        quantity: float,
        brand_preference: str | None,
        product_specs_remarks: str | None,
        status: InquiryItemStatus,
        user_id: uuid.UUID,
    ) -> InquiryItem:
        """
        Add one product line to a consignment (creating the consignment header on first use).
        """
        if quantity <= 0:
            raise BadRequestException("Quantity must be greater than zero.")

        product = await self.product_repository.get_by_id(product_id)
        if product is None:
            raise BadRequestException("The specified product does not exist.")

        inquiry = await self.get_or_create_consignment(
            buyer_id=buyer_id, consignment_code_id=consignment_code_id, user_id=user_id
        )

        now = _utcnow()
        item = await self.item_repository.create(
            inquiry_id=inquiry.id,
            product_id=product_id,
            uom_id=product.uom_id,
            quantity=quantity,
            brand_preference=brand_preference,
            product_specs_remarks=product_specs_remarks,
            status=status,
            proposed_at=now,
            proposed_by=user_id,
            approved_at=now if status == InquiryItemStatus.APPROVED else None,
            approved_by=user_id if status == InquiryItemStatus.APPROVED else None,
            tally_entry_posted=False,
            requires_license=bool(getattr(product, "license_certificate_required", None)),
        )
        await self._refresh_rollup(inquiry.id)
        return item

    async def add_items_bulk(
        self,
        *,
        buyer_id: uuid.UUID,
        consignment_code_id: uuid.UUID,
        items_payload: list[dict],
        user_id: uuid.UUID,
    ) -> list[InquiryItem]:
        """
        Add multiple product lines to a consignment in a single roundtrip.
        """
        inquiry = await self.get_or_create_consignment(
            buyer_id=buyer_id, consignment_code_id=consignment_code_id, user_id=user_id
        )
        now = _utcnow()
        created_items = []
        for p in items_payload:
            prod_id = uuid.UUID(str(p["product_id"]))
            qty = float(p["quantity"])
            if qty <= 0:
                continue
            product = await self.product_repository.get_by_id(prod_id)
            if not product:
                continue
            st = InquiryItemStatus(p.get("status", "proposed"))
            item = await self.item_repository.create(
                inquiry_id=inquiry.id,
                product_id=prod_id,
                uom_id=product.uom_id,
                quantity=qty,
                brand_preference=p.get("brand_preference"),
                product_specs_remarks=p.get("product_specs_remarks"),
                status=st,
                proposed_at=now,
                proposed_by=user_id,
                approved_at=now if st == InquiryItemStatus.APPROVED else None,
                approved_by=user_id if st == InquiryItemStatus.APPROVED else None,
                tally_entry_posted=False,
                requires_license=bool(getattr(product, "license_certificate_required", None)),
            )
            created_items.append(item)

        await self._refresh_rollup(inquiry.id)
        return created_items

    async def import_items(
        self,
        inquiry_id: uuid.UUID,
        filename: str,
        raw_bytes: bytes,
        user_id: uuid.UUID,
    ) -> Any:
        """
        Validate and import product line items from an uploaded CSV/XLSX file into a consignment.

        Matches each row's product by Product Code or Product Name against Product Master,
        copies UOM and license flags automatically, and updates consignment rollups.
        """
        from app.masters.import_export import parse_rows_from_file, ImportSummary

        inquiry = await self.get_inquiry_or_raise(inquiry_id)
        rows = parse_rows_from_file(filename, raw_bytes)

        # Pre-fetch all active products for fast lookup
        all_products = await self.product_repository.list(limit=None)
        product_by_code = {p.product_code.strip().lower(): p for p in all_products if p.product_code}
        product_by_name = {p.product_name.strip().lower(): p for p in all_products if p.product_name}
        product_by_tally = {
            getattr(p, "product_name_tally", "").strip().lower(): p
            for p in all_products
            if getattr(p, "product_name_tally", None)
        }

        summary = ImportSummary(total_rows=len(rows))
        now = _utcnow()

        for idx, row in enumerate(rows):
            row_num = idx + 2  # Excel row 2 is first data row after header

            # Extract fields with flexible key names (human-readable or snake_case)
            def _val(*keys: str) -> str:
                for k in keys:
                    v = row.get(k)
                    if v is not None:
                        s = f"{v}".strip()
                        if s:
                            return s
                return ""

            raw_code = _val("Product Code", "product_code", "SKU", "Item Code", "item_code")
            raw_name = _val("Product Name", "product_name", "Item Name", "item_name", "Title")
            raw_qty = _val("Quantity", "quantity", "Qty", "qty")
            brand_pref = _val("Brand Preference", "brand_preference", "Brand", "brand") or None
            specs_remarks = _val("Product Specs / Remarks", "product_specs_remarks", "Remarks", "remarks", "Specifications") or None
            raw_status = _val("Status", "status").lower()

            # 1. Resolve Product
            product = None
            if raw_code and raw_code.lower() in product_by_code:
                product = product_by_code[raw_code.lower()]
            elif raw_name and raw_name.lower() in product_by_name:
                product = product_by_name[raw_name.lower()]
            elif raw_name and raw_name.lower() in product_by_tally:
                product = product_by_tally[raw_name.lower()]

            if not product:
                search_term = raw_name or raw_code or "Unknown"
                summary.failed += 1
                summary.errors.append({
                    "row": row_num,
                    "error": f"Product '{search_term}' not found in Product Master. Please ensure product exists.",
                    "row_data": row,
                })
                continue

            # 2. Validate Quantity
            try:
                clean_qty = raw_qty.replace(",", "")
                qty = float(clean_qty)
                if qty <= 0:
                    raise ValueError("Quantity must be greater than zero.")
            except (ValueError, TypeError):
                summary.failed += 1
                summary.errors.append({
                    "row": row_num,
                    "error": f"Invalid quantity '{raw_qty}'. Must be a positive number.",
                    "row_data": row,
                })
                continue

            # 3. Determine Status
            st = (
                InquiryItemStatus.APPROVED
                if raw_status in ("approved", "yes", "true", "1")
                else InquiryItemStatus.PROPOSED
            )

            # 4. Create InquiryItem
            try:
                await self.item_repository.create(
                    inquiry_id=inquiry.id,
                    product_id=product.id,
                    uom_id=product.uom_id,
                    quantity=qty,
                    brand_preference=brand_pref,
                    product_specs_remarks=specs_remarks,
                    status=st,
                    proposed_at=now,
                    proposed_by=user_id,
                    approved_at=now if st == InquiryItemStatus.APPROVED else None,
                    approved_by=user_id if st == InquiryItemStatus.APPROVED else None,
                    tally_entry_posted=False,
                    requires_license=bool(getattr(product, "license_certificate_required", None)),
                )
                summary.created += 1
            except Exception as ex:
                summary.failed += 1
                summary.errors.append({
                    "row": row_num,
                    "error": f"Failed to save item: {ex}",
                    "row_data": row,
                })

        if summary.created > 0:
            await self._refresh_rollup(inquiry.id)

        return summary

    async def update_item(self, inquiry_id: uuid.UUID, item_id: uuid.UUID, **field_values: Any) -> InquiryItem:
        """
        Update an inquiry item's editable fields.

        Document (Process Flow): "editable in quantity, shifting between
        FB1 & FB2 (but weight, CBM etc will not be editable)" -- weight/
        CBM are consignment-level rollups computed by the service, never
        accepted as direct input here, so there is no field for them on
        this call in the first place.
        """
        item = await self.get_item_or_raise(inquiry_id, item_id)

        new_quantity = field_values.get("quantity")
        if new_quantity is not None and new_quantity <= 0:
            raise BadRequestException("Quantity must be greater than zero.")

        changes = {k: v for k, v in field_values.items() if v is not None}
        if changes:
            await self.item_repository.update(item, **changes)
            await self._refresh_rollup(inquiry_id)
        return item

    async def shift_item(self, from_inquiry_id: uuid.UUID, item_id: uuid.UUID, *, to_consignment_code_id: uuid.UUID, user_id: uuid.UUID) -> InquiryItem:
        """
        Move an item from one consignment to another under the same buyer.

        Document (Process Flow): "shifting between FB1 & FB2" -- both
        consignment codes must belong to the same buyer; shifting across
        buyers is not described by the document and is rejected here
        rather than silently allowed.
        """
        item = await self.get_item_or_raise(from_inquiry_id, item_id)
        from_inquiry = await self.get_inquiry_or_raise(from_inquiry_id)

        to_inquiry = await self.get_or_create_consignment(
            buyer_id=from_inquiry.buyer_id, consignment_code_id=to_consignment_code_id, user_id=user_id
        )
        if to_inquiry.id == from_inquiry_id:
            return item

        await self.item_repository.update(item, inquiry_id=to_inquiry.id)
        await self._refresh_rollup(from_inquiry_id)
        await self._refresh_rollup(to_inquiry.id)
        return item

    async def approve_item(self, inquiry_id: uuid.UUID, item_id: uuid.UUID, *, user_id: uuid.UUID) -> InquiryItem:
        """Document: Status moves Proposed -> Approved; Approved Date/By auto-generated from the acting user."""
        item = await self.get_item_or_raise(inquiry_id, item_id)
        await self.item_repository.update(
            item, status=InquiryItemStatus.APPROVED, approved_at=_utcnow(), approved_by=user_id
        )
        await self._refresh_rollup(inquiry_id)
        return item

    async def revert_item_to_proposed(self, inquiry_id: uuid.UUID, item_id: uuid.UUID) -> InquiryItem:
        """Move an approved item back to Proposed (e.g. approved in error)."""
        item = await self.get_item_or_raise(inquiry_id, item_id)
        await self.item_repository.update(item, status=InquiryItemStatus.PROPOSED, approved_at=None, approved_by=None)
        await self._refresh_rollup(inquiry_id)
        return item

    async def set_procurement_remarks(self, inquiry_id: uuid.UUID, item_id: uuid.UUID, *, remarks: str | None) -> InquiryItem:
        """Document: "Remarks (by Yinglima China Procurement Team) ... added or edited from 'Action' Panel"."""
        item = await self.get_item_or_raise(inquiry_id, item_id)
        await self.item_repository.update(item, procurement_remarks=remarks)
        return item

    async def bulk_mark_tally_posted(self, item_ids: list[uuid.UUID], *, user_id: uuid.UUID) -> list[InquiryItem]:
        """
        Mark multiple items as Tally Entry Posted in one call.

        Document: "some easy way to select and change multiple items to
        'Posted'." Silently skips IDs that don't exist rather than
        failing the whole batch over one bad ID, since this is meant to
        be a fast bulk action, not a validating single-item form.
        """
        updated: list[InquiryItem] = []
        affected_inquiry_ids: set[uuid.UUID] = set()
        now = _utcnow()
        for item_id in item_ids:
            item = await self.item_repository.get_by_id(item_id)
            if item is None:
                continue
            await self.item_repository.update(
                item, tally_entry_posted=True, tally_posted_at=now, tally_posted_by=user_id
            )
            updated.append(item)
            affected_inquiry_ids.add(item.inquiry_id)
        for inquiry_id in affected_inquiry_ids:
            await self._refresh_rollup(inquiry_id)
        return updated

    async def delete_item(self, inquiry_id: uuid.UUID, item_id: uuid.UUID) -> None:
        item = await self.get_item_or_raise(inquiry_id, item_id)
        await self.item_repository.delete(item)
        await self._refresh_rollup(inquiry_id)

    # ------------------------------------------------------------------
    # Quotations & RFQs
    # ------------------------------------------------------------------

    async def list_quotations_for_item(self, inquiry_item_id: uuid.UUID) -> list[dict]:
        """List all quotations submitted for a specific inquiry item."""
        if not self.quotation_repository:
            raise BadRequestException("Quotation repository not initialized.")
        return await self.quotation_repository.list_for_item_with_details(inquiry_item_id)

    async def create_quotation(
        self, inquiry_item_id: uuid.UUID, data: QuotationCreate, *, user_id: uuid.UUID
    ) -> Quotation:
        """Create a supplier quotation for an item."""
        if not self.quotation_repository:
            raise BadRequestException("Quotation repository not initialized.")
        item = await self.item_repository.get_by_id(inquiry_item_id)
        if item is None:
            raise NotFoundException("Inquiry item not found.")

        quote_number = await self.quotation_repository.generate_quote_number()

        from datetime import date
        exp_date = None
        if data.expected_receiving_date:
            try:
                exp_date = date.fromisoformat(data.expected_receiving_date)
            except ValueError:
                exp_date = None

        return await self.quotation_repository.create(
            quote_number=quote_number,
            inquiry_item_id=inquiry_item_id,
            supplier_id=data.supplier_id,
            quantity=data.quantity,
            unit_price=data.unit_price,
            total_cost=data.total_cost,
            currency=data.currency or "CNY",
            expected_receiving_date=exp_date,
            terms_and_conditions=data.terms_and_conditions,
            remarks=data.remarks,
            status=QuotationStatus.PENDING,
            created_by=user_id,
        )

    async def update_quotation_status(
        self, quotation_id: uuid.UUID, status_str: str, *, user_id: uuid.UUID
    ) -> Quotation:
        """Update a quotation status (e.g. approve or reject)."""
        if not self.quotation_repository:
            raise BadRequestException("Quotation repository not initialized.")
        quote = await self.quotation_repository.get_by_id(quotation_id)
        if quote is None:
            raise NotFoundException("Quotation not found.")

        try:
            status_enum = QuotationStatus(status_str.lower())
        except ValueError:
            raise BadRequestException(f"Invalid quotation status: {status_str}")

        updated_quote = await self.quotation_repository.update(quote, status=status_enum)

        # Sync inquiry item status with its quotations:
        # If any approved quotation exists for this item -> item is APPROVED.
        # If no approved quotations remain -> item reverts to PROPOSED.
        approved_count = await self.quotation_repository.count_approved_for_item(quote.inquiry_item_id)
        item = await self.item_repository.get_by_id(quote.inquiry_item_id)
        if item:
            if approved_count > 0:
                await self.item_repository.update(
                    item,
                    status=InquiryItemStatus.APPROVED,
                    approved_at=_utcnow(),
                    approved_by=user_id,
                )
            else:
                await self.item_repository.update(
                    item,
                    status=InquiryItemStatus.PROPOSED,
                    approved_at=None,
                    approved_by=None,
                )
            await self._refresh_rollup(item.inquiry_id)

        return updated_quote

    async def update_quotation(
        self, quotation_id: uuid.UUID, data: QuotationUpdate, *, user_id: uuid.UUID
    ) -> Quotation:
        """Update commercial details of a supplier quotation."""
        if not self.quotation_repository:
            raise BadRequestException("Quotation repository not initialized.")
        quote = await self.quotation_repository.get_by_id(quotation_id)
        if quote is None:
            raise NotFoundException("Quotation not found.")

        update_dict: dict[str, Any] = {}
        if data.quantity is not None:
            update_dict["quantity"] = data.quantity
        if data.unit_price is not None:
            update_dict["unit_price"] = data.unit_price
        if data.total_cost is not None:
            update_dict["total_cost"] = data.total_cost
        elif data.quantity is not None or data.unit_price is not None:
            qty = data.quantity if data.quantity is not None else (quote.quantity or 1.0)
            uprice = data.unit_price if data.unit_price is not None else (quote.unit_price or 0.0)
            update_dict["total_cost"] = round(qty * uprice, 2)
        if data.currency is not None:
            update_dict["currency"] = data.currency.upper()
        if data.expected_receiving_date is not None:
            from datetime import date
            try:
                update_dict["expected_receiving_date"] = (
                    date.fromisoformat(data.expected_receiving_date) if data.expected_receiving_date else None
                )
            except ValueError:
                pass
        if data.terms_and_conditions is not None:
            update_dict["terms_and_conditions"] = data.terms_and_conditions.strip() or None
        if data.remarks is not None:
            update_dict["remarks"] = data.remarks.strip() or None
        if data.attachment_url is not None:
            update_dict["attachment_url"] = data.attachment_url
        if data.attachment_filename is not None:
            update_dict["attachment_filename"] = data.attachment_filename

        updated = await self.quotation_repository.update(quote, **update_dict)
        return updated

    async def delete_quotation(
        self, quotation_id: uuid.UUID, *, user_id: uuid.UUID
    ) -> Quotation:
        """Soft-delete a quotation and resync inquiry item status."""
        if not self.quotation_repository:
            raise BadRequestException("Quotation repository not initialized.")
        quote = await self.quotation_repository.get_by_id(quotation_id)
        if quote is None:
            raise NotFoundException("Quotation not found.")

        item_id = quote.inquiry_item_id
        await self.quotation_repository.delete(quote)

        # Sync inquiry item status with remaining quotations:
        if self.item_repository:
            approved_count = await self.quotation_repository.count_approved_for_item(item_id)
            item = await self.item_repository.get_by_id(item_id)
            if item:
                if approved_count > 0:
                    await self.item_repository.update(
                        item,
                        status=InquiryItemStatus.APPROVED,
                        approved_at=_utcnow(),
                        approved_by=user_id,
                    )
                else:
                    await self.item_repository.update(
                        item,
                        status=InquiryItemStatus.PROPOSED,
                        approved_at=None,
                        approved_by=None,
                    )
                await self._refresh_rollup(item.inquiry_id)

        return quote

    async def create_rfq(
        self, inquiry_item_id: uuid.UUID, data: RFQCreate, *, user_id: uuid.UUID
    ) -> RFQ:
        """Create and dispatch an RFQ."""
        if not self.rfq_repository:
            raise BadRequestException("RFQ repository not initialized.")
        item = await self.item_repository.get_by_id(inquiry_item_id)
        if item is None:
            raise NotFoundException("Inquiry item not found.")

        from datetime import date
        exp_date = None
        if data.expected_receiving_date:
            try:
                exp_date = date.fromisoformat(data.expected_receiving_date)
            except ValueError:
                exp_date = None

        supplier_ids_str = [str(s) for s in data.supplier_ids] if data.supplier_ids else []

        return await self.rfq_repository.create(
            inquiry_item_id=inquiry_item_id,
            expected_receiving_date=exp_date,
            supplier_type=data.supplier_type or "selected",
            supplier_ids=supplier_ids_str,
            notes=data.notes,
            status="sent",
            created_by=user_id,
        )

    async def list_rfqs_for_item(self, inquiry_item_id: uuid.UUID) -> list[RFQ]:
        if not self.rfq_repository:
            raise BadRequestException("RFQ repository not initialized.")
        return await self.rfq_repository.list_for_item(inquiry_item_id)

    async def get_last_purchase_for_product(self, product_id: uuid.UUID) -> dict | None:
        """Fetch the latest approved quote or recent quotation for a product."""
        if not self.quotation_repository:
            return None
        return await self.quotation_repository.get_last_purchase_for_product(product_id)


