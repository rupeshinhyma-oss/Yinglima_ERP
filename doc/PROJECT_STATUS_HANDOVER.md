# Yinglima ERP — Master Project Context & Handover Documentation

**Last Updated:** September 7, 2026 (11:05 IST)  
**Repository:** `https://github.com/rupeshinhyma-oss/Yinglima_ERP.git` (`d:\OM work\ERP_Main_Claude-main`)  
**Target Audience:** Antigravity AI Agent & Human Developers (Comprehensive onboarding & resume document)

---

## 1. Quick Resume Instruction for Antigravity AI
When starting Antigravity on a new machine or starting a new session, simply prompt:
> *"I switched laptops. Read `doc/PROJECT_STATUS_HANDOVER.md`, `doc/SYSTEM_DOCUMENTATION.md`, and `MODULES_AND_FEATURES_TEST_MANUAL.md` to resume our work."*

---

## 2. Executive Overview: What is this ERP?

### A. Business Domain & Purpose
This is a specialized, enterprise-grade **Global Procurement & Supply Chain ERP** built for **Yinglima Import & Export (Wenzhou) Co., Ltd. (盈骊玛进出口（温州）有限公司)** and **Inhyma**.
The platform orchestrates cross-border machinery and industrial packaging manufacturing trade between **Chinese factory suppliers** and **Indian importers/buyers**:
- **Buyers (India):** Request machinery, packaging equipment, conveyors, band sealers, and spare parts.
- **Suppliers (China):** Industrial machinery manufacturers (e.g. Wenzhou Brother Machinery, Hualian Machinery) who quote prices in Chinese Yuan (CNY / RMB).
- **Yinglima China Procurement Team:** Coordinates sourcing, multi-channel RFQs (Email + WeChat), price negotiations, shipment consolidation (CBM/weight planning), and Tally accounting entry.

---

## 3. Core Modules & System Architecture

### 1. Inquiries & Consignment Management (`/inquiries`) — The Heart of the ERP
Organized as a structured **3-Layer Procurement Hierarchy**:
- **Layer 1 — Buyer Selection:** Select or manage the buyer company placing the order.
- **Layer 2 — Consignment Batch:** Sourcing items are grouped into shipment consignments (e.g., `FB1`, `FB2`, `FB3`, `SEA 1`). Tracks total volume in CBM (Cubic Meters), gross weight (kg), and status (`Proposed` vs `Approved`).
- **Layer 3 — Product Line Items & Quotation Matrix:**
  - Individual machinery/parts ordered (e.g., *Band Sealer Conveyor for 10 Kgs*, *FR 900A Band Sealer MSV*).
  - Tracks target quantity, target price, brand preference, specifications, and received quotes count.
  - **Tally Status Toggle:** Clickable badge on each line item to flip between `Pending Tally` and `Tally Posted` (with real-time timestamp and auditor recording).

### 2. Multi-Channel Bulk RFQ Dispatch
- **Email RFQs (Isolated 1-on-1):** Dispatches automated RFQs to multiple suppliers simultaneously. Each supplier receives a strictly isolated email (never revealing competitor emails in `To:` or `Cc:`). Includes a secure public quote portal token link (`/quote/:token`).
- **Tencent WeCom & WeChat RFQs:** Dispatches bilingual (English + Chinese) Markdown RFQ cards directly into Chinese suppliers' WeChat accounts via Tencent WeCom API.

### 3. Automated Inbound AI Quotation Extraction
- **Inbound Email Worker (`backend/app/inquiries/email_inbound_worker.py`):** Runs an asynchronous IMAP inbox listener. Matches replying suppliers, finds the consignment batch (even with spaces like `[SEA 1]`), and invokes OpenAI GPT-4o-mini to extract prices, currency, quantities, payment terms, and delivery dates.
- **WeChat Webhook (`backend/app/inquiries/routes.py: /wechat/callback`):** Receives AES-256-CBC encrypted XML messages from Tencent when suppliers reply on WeChat. Decrypts messages, logs conversation history, and extracts quotes via AI.
- **Strict 1st-Conversation Policy:** AI quotation extraction operates strictly on the **first quotation reply** from a supplier for each item. Once the baseline quotation is recorded, all subsequent messages (counter-offers, chatter, logistics questions) are recorded in the timeline without calling OpenAI (0 token cost, 0 latency, zero risk of overwriting baseline quotes).
- **Quotation Matrix Comparison Modal:** Side-by-side comparison of all supplier quotations per item. Automatically highlights the lowest unit price in green, supports one-click `Approve Quote`, and auto-generates Purchase Orders (PO).

### 4. Master Shipment Planning Grid (`/planning`)
- Interactive spreadsheet workbook for logistics planners.
- Features dynamic column customization, container packing CBM calculations, multi-branch allocation, and container stuffing optimization.

### 5. Master Catalogs (`/masters`)
- **Products:** Complete catalog with specifications, product codes (`#DAR-01563`), UOMs, HSN codes, and Tally mapping names.
- **Suppliers:** Directory with contacts, emails, Chinese phone numbers (`+86`), Indian numbers (`+91`), and WeChat UserIDs.
- **Buyers, Brands, Categories, Subcategories, Currencies, Countries, UOMs.**

### 6. Security, RBAC & Audit Trail
- Multi-role permission system (Super Admin, Procurement Admin, Sales, Logistics).
- Immutable audit log capturing all entity creation, edit, status change, and deletion events.

---

## 4. Technology Stack & Infrastructure

| Layer | Technologies Used |
| :--- | :--- |
| **Frontend** | React 18, TypeScript, Vite, Vanilla CSS / Tailwind, Lucide Icons |
| **Backend API** | FastAPI, Python 3.11/3.12, SQLAlchemy 2.0 (Async), Pydantic v2, Alembic |
| **Database** | **Remote Cloud Supabase PostgreSQL** (`aws-0-ap-south-1.pooler.supabase.com`) |
| **Real-time Comms** | WebSocket Live Client (`/api/v1/events/ws`), EventDispatcher |
| **AI Quotation Engine** | OpenAI GPT-4o-mini with 3-attempt automated retry and exponential backoff |
| **WeChat Integration** | Tencent WeCom API, WXBizMsgCrypt AES-256-CBC encryption |
| **Email Service** | Python `aiosmtplib` (SMTP outbound), `imaplib` (IMAP inbound listener) |

---

## 5. Server Hosts, Endpoints & Credentials Overview

### A. Database (Cloud Supabase PostgreSQL)
- **Host / Pooler:** `aws-0-ap-south-1.pooler.supabase.com`
- **Port:** `6543` (Transaction Pooler) / `5432` (Direct Session)
- **Database Name:** `postgres`
- *Note: All persistent business data is in the cloud; local laptops only connect via credentials in `backend/.env`.*

### B. Tencent WeCom (企业微信) Configuration
- **Corp ID (`CorpId`):** `ww0aafdc97cca27e0a`
- **Agent ID (`AgentId`):** `1000002` (*Yinglima ERP Bot*)
- **Secret:** `8kzaUnGu34Q6aelEYTaVyB9xOH7EX7MSR6tsLpiL9B8`
- **Token:** `Nr8CIsNe`
- **EncodingAESKey:** `yoIVWBBr2iRASH0rIyu2H5VjsSVl1LcWAzXgwyAajLc`
- **API Endpoint:** `https://qyapi.weixin.qq.com`
- **Callback Inbound Path:** `/api/v1/inquiries/wechat/callback`
- **Whitelisted Enterprise IPs (Cloudflare Egress):**
  `104.28.232.96;104.28.232.97;104.28.200.92;104.28.200.96;104.28.200.97`
- **Admin Group:** `ERP Admins` (Paws / `paws` / `+91 8108294930` configured with full management rights).

### C. Mail Servers
- **SMTP Host:** `smtp.gmail.com` (Port `587`, TLS)
- **IMAP Host:** `imap.gmail.com` (Port `993`, SSL)

---

## 6. Current Test Consignments & Verified Status

### Consignment `FB2` (Multi-Supplier Email Test)
- **Items:**
  1. *Band Sealer Conveyor for 10 Kgs (#INH-00209)*:
     - `QT-AUTO-01`: Wenzhou Brother Machinery (¥1,250 CNY)
     - `QT-AUTO-02`: Hualian Machinery Group (¥12,700 CNY)
  2. *FR 900A Band Sealer MSV (#DAR-01563)*:
     - `QT-AUTO-01`: Wenzhou Brother Machinery (¥1,680 CNY)
     - `QT-AUTO-02`: Hualian Machinery Group (¥7,000 CNY)
- **Verification:** Both suppliers' email replies successfully parsed and displayed in matrix under separate products.

### Consignment `FB3` (WeChat End-to-End Test)
- **Item:** *FR 900A Band Sealer MSV* (Qty: 89)
- **WeChat Outbound:** Dispatched to `paws` (`+91 8108294930`) with `errcode: 0, errmsg: 'ok'`.
- **WeChat Inbound Reply:** Simulated reply received and decrypted.
- **Quote Generated:** `QT-AUTO-01` (Unit price: ¥1,550 CNY, FOB Ningbo, 30% advance, 10 days delivery).

---

## 7. Mandatory AI & Developer Policies
1. **Living Documentation Policy (`AGENTS.md`):**
   - Whenever any API endpoint, schema, UI view, button, or logic changes, immediately update `doc/SYSTEM_DOCUMENTATION.md` and `MODULES_AND_FEATURES_TEST_MANUAL.md`.
2. **Zero Feature Loss & Zero Inaccuracies:**
   - Never break or strip existing cataloged features or UI layouts during development.
3. **Local Development Safety:**
   - **NO `git push`** without explicit user permission.

---

## 8. Laptop Migration & Setup Checklist

1. **Backup from Current Laptop:**
   - Copy the entire folder `d:\OM work\ERP_Main_Claude-main` to a USB drive or cloud zip.
   - **MANDATORY:** Ensure `backend/.env` is included in the copy (it is git-ignored and contains DB/API secrets).
2. **Setup on New Laptop:**
   - Prerequisites: Python 3.11/3.12, Node.js 18+, Antigravity IDE.
   - Paste the project directory.
   - In terminal 1 (Backend):
     ```bash
     cd backend
     python -m pip install -r requirements.txt
     python server.py --skip-migrate
     ```
   - In terminal 2 (Frontend):
     ```bash
     cd frontend
     npm install
     npm run dev
     ```
   - Open Antigravity IDE and log into your Google account.
   - Open folder `ERP_Main_Claude-main`.
   - Prompt Antigravity: *"I switched laptops. Read `doc/PROJECT_STATUS_HANDOVER.md` and resume our work."*
