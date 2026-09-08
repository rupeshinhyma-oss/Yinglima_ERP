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
2. **Critical Module Protection (Inquiry & Email AI Quotation System)**:
   - The **Inquiry module** is our primary production pipeline and must NEVER be broken or regressed:
     - Automated AI Quotation Extraction (`extract_quotes_from_text`, `QT-AUTO-XX` creation).
     - Inbound Email Poller & Worker (`backend/app/inquiries/email_inbound_worker.py`).
     - Two-way communication timeline & email composer (`Emails` and `WeChat Messages` tabs).
     - Consignment Line-Items Export (Excel `.xlsx` and `.csv`).
     - Smart Hybrid Live-Sync (15s visibility-aware fallback + real-time WebSockets).
     - WeChat/WeCom dispatch and webhook callback integration.
3. **Collision Detection & Resolution**: If incoming remote commits touch or alter any Inquiry files (`service.py`, `routes.py`, `email_inbound_worker.py`, `wechat_service.py`, `Inquiries.tsx`), meticulously cross-verify every change. If the collaborator accidentally broke, removed, or regressed any working Inquiry functionality, immediately preserve and restore our working code.
4. **Build & Regression Verification**: Run `npm run build` in `frontend` and verify backend routes before reporting back to the user.


