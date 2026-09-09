# AI Assistant & Developer Guidelines

## Living Documentation & Testing Manual Policy (Mandatory)

Whenever any features, functions, API endpoints, database schemas, frontend components, forms, fields, modals, or architecture components are added, modified, or removed in this codebase:

1. **Update `doc/SYSTEM_DOCUMENTATION.md`**:
   - Keep the file map, feature descriptions, and API route tables aligned with the current code.
   - If a new module, table, endpoint, page, or background worker is introduced, document its architecture, purpose, and usage in `doc/SYSTEM_DOCUMENTATION.md`.
   - Update the **Last Updated** timestamp and relevant section numbers.

2. **Update `MODULES_AND_FEATURES_TEST_MANUAL.md`**:
   - Keep the complete catalog of all UI views, tables, forms, fields, dropdown sources, action buttons, modals, and test checklists aligned with the active frontend.
   - If a new button, form tab, input field, modal, calculation, or module is introduced or edited, document its exact UI specifications, required validations, and test cases in `MODULES_AND_FEATURES_TEST_MANUAL.md`.

3. **Zero Inaccuracies & Zero Feature Loss**:
   - Ensure file paths, schema references, and code references reflect the exact codebase state.
   - Never remove or break existing cataloged features during development.

## 4. Git Push Policy (Strict)
- **NEVER push code to GitHub automatically.**
- Only push to the remote repository when the user explicitly instructs: *"push"*, *"push to github"*, or *"put this on github"*.

## 5. Git Pull & Remote Merge Cross-Verification Protocol
Whenever the user instructs to pull code from GitHub (e.g. incorporating work from their collaborator/friend):
1. **Fetch and Diff First**: Run `git fetch origin` and inspect incoming changes via `git log HEAD..origin/main` and `git diff HEAD..origin/main` before merging.
2. **Critical Module Protection (Inquiry, Email AI Quotation & Universal Bulk Import Engine)**:
   - **Inquiry module**: Primary production pipeline and must NEVER be broken or regressed:
     - Automated AI Quotation Extraction (`extract_quotes_from_text`, `QT-AUTO-XX` creation).
     - Inbound Email Poller & Worker (`backend/app/inquiries/email_inbound_worker.py`).
     - Two-way communication timeline & email composer (`Emails` and `WeChat Messages` tabs).
     - Consignment Line-Items Export (Excel `.xlsx` and `.csv`).
     - Smart Hybrid Live-Sync (15s visibility-aware fallback + real-time WebSockets).
     - WeChat/WeCom dispatch and webhook callback integration.
   - **Universal Bulk Import & Deduplication Engine (Suppliers, Buyers, Products, Inquiries, Masters)**:
     - **Buyer Master (`backend/app/buyers/service.py`, `repository.py`)**: Note 66 3-way deduplication across `company_name` (case-insensitive), `contact_calling_number`, and `contact_whatsapp_number` ($\ge 6$ clean digits, cross-checking calling vs whatsapp numbers) plus in-batch collision check (`seen_in_batch`).
     - **Supplier Master (`backend/app/suppliers/service.py`, `validators.py`)**: `company_name` DB and in-file duplicate prevention (`seen_in_batch`), null-safe state code checks (`s.code and s.code.lower() == state_raw.lower()`), 7-15 digit phone/WhatsApp/WeChat format validation, and Country/State/City + Category/Sub-Category relation enforcement.
     - **Product Master (`backend/app/masters/products/service.py`, `validators.py`)**: Dual-uniqueness on `product_name` and `product_code`, in-file duplicate tracking (`seen_names`, `seen_codes`), Category/Sub-Category parent-child validation, and automatic CBM calculation `(L x W x H) / 1,000,000`.
     - **Inquiry Consignment Line Items (`backend/app/inquiries/service.py:import_items`)**: Product code/name resolution against Product Master, UOM inheritance, license requirement copying, positive quantity validation, and rollup recalculation (`_refresh_rollup`).
     - **Master Data Catalogs (All 12 Masters)**: Auto-generation of code slugs (`CAT-XXX`, `BR-XXX`, `BT-XXX`, `UOM-XXX`) from names when code is omitted, and HSN `Refund VAT %` float parsing.
     - **Standard Test Workbooks**: 8 verified test files in `testingimportfile/` for clean import and duplicate rejection verification.
3. **Collision Detection & Resolution**: If incoming remote commits touch or alter any Inquiry files (`service.py`, `routes.py`, `email_inbound_worker.py`, `wechat_service.py`, `Inquiries.tsx`), Buyer files (`buyers/service.py`, `buyers/repository.py`, `Buyers.tsx`), Supplier files (`suppliers/service.py`), Product files (`masters/products/`), or Master Data files, meticulously cross-verify every change. If remote commits accidentally remove, break, or regress the 3-way duplicate detection, null-safe state checks, code auto-generators, or import wizards, immediately preserve and restore our working code.
4. **Build & Regression Verification**: Run `npm run build` in `frontend` and verify backend routes before reporting back to the user.


