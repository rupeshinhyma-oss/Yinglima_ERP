# Enterprise ERP System — Unified Architecture, Feature & Technical Manual

> **System Version:** 1.1.0 (Production)  
> **Last Updated:** September 10, 2026 (Consolidated Collapsible Masters Accordion in Sidebar; Top-level Inquiries, Products, Suppliers & Buyers; Inquiry Lifecycle Tabs & Bulk Actions; zero regression)  
> **Repository:** `https://github.com/rupeshinhyma-oss/Yinglima_ERP.git`  
> **Architectural Pattern:** Modular Async Monolith (FastAPI) + React 18 SPA (Vite) + Real-Time WebSocket Event Bus  
> **Target Audience:** Systems Architects, Software Engineers, DevOps, and Autonomous AI Coding Assistants.  
> **Scope:** Complete end-to-end technical reference containing all system features, data models, API endpoints, background workers, frontend architecture, and developer integration guidelines.

---

## Table of Contents

1. [Executive Architecture & System Topology](#1-executive-architecture--system-topology)
2. [Technology Stack & Dependencies](#2-technology-stack--dependencies)
3. [Directory Layout & File Map](#3-directory-layout--file-map)
4. [Database Architecture & Universal Mixins](#4-database-architecture--universal-mixins)
5. [Complete Data Models & Entity Dictionary](#5-complete-data-models--entity-dictionary)
6. [Security, Authentication & Session Engine](#6-security-authentication--session-engine)
7. [RBAC Engine, Departments & Effective Permissions](#7-rbac-engine-departments--effective-permissions)
8. [Module-by-Module Technical Breakdown](#8-module-by-module-technical-breakdown)
   - 8.1. [Authentication & Active Sessions](#81-authentication--active-sessions)
   - 8.2. [Users & HR Profile Management](#82-users--hr-profile-management)
   - 8.3. [Departments & Department Managers](#83-departments--department-managers)
   - 8.4. [Master Data & Generic Catalogs](#84-master-data--generic-catalogs)
   - 8.5. [Product Catalog & Dynamic Specification Builder](#85-product-catalog--dynamic-specification-builder)
   - 8.6. [Supplier Directory & Tokenized Public Portal](#86-supplier-directory--tokenized-public-portal)
   - 8.7. [Buyer & Client Management](#87-buyer--client-management)
   - 8.8. [Inquiries, RFQs & AI Quotation Extractor](#88-inquiries-rfqs--ai-quotation-extractor)
   - 8.9. [Automated Inbound IMAP Email Worker](#89-automated-inbound-imap-email-worker)
   - 8.10. [Master Shipment Planning Grid & Container Calculations](#810-master-shipment-planning-grid--container-calculations)
   - 8.11. [Audit Trails & JSON Delta Change Diffing](#811-audit-trails--json-delta-change-diffing)
   - 8.12. [Recycle Bin (Universal Soft-Delete & Recovery)](#812-recycle-bin-universal-soft-delete--recovery)
   - 8.13. [Organization & System Profile](#813-organization--system-profile)
   - 8.14. [Employee Directory & Organization Structure](#814-employee-directory--organization-structure-identity--access-management-upgrade)

9. [Real-Time WebSocket & Event Synchronization](#9-real-time-websocket--event-synchronization)
10. [Multi-Tier Caching Engine](#10-multi-tier-caching-engine)
11. [Universal Bulk Import & Export Wizard](#11-universal-bulk-import--export-wizard)
    - 11.1. [Media & File Storage Subsystem (Supabase & Local Disk Fallback)](#111-media--file-storage-subsystem-supabase--local-disk-fallback)
12. [Frontend Architecture & Single-Flight Token Refresh](#12-frontend-architecture--single-flight-token-refresh)
13. [Complete API Route & Endpoint Directory](#13-complete-api-route--endpoint-directory)
14. [Developer & AI Integration Guide (Rules of Engagement)](#14-developer--ai-integration-guide-rules-of-engagement)
15. [Deployment, Environment Variables & Operations](#15-deployment-environment-variables--operations)

---

## 1. Executive Architecture & System Topology

```
+---------------------------------------------------------------------------------------------------+
|                                          CLIENT TIER                                              |
|  React 18 Single Page App  |  IHM Design System (Vanilla CSS)  |  WebSocket Real-Time Listener    |
+-------------------------------------------------+-------------------------------------------------+
                                                  | HTTPS / WSS JSON API
+-------------------------------------------------v-------------------------------------------------+
|                                     FASTAPI APPLICATION TIER                                      |
|                                                                                                   |
|  [Middleware Pipeline: CORS -> Rate Limiting -> Request Logging -> Security Headers -> Context]   |
|                                                                                                   |
|  +---------------------------+  +---------------------------+  +-------------------------------+  |
|  | Authentication & Sessions |  | RBAC & Department Engine  |  | Inquiries & RFQ Lifecycle     |  |
|  | - Argon2id Password Hash  |  | - Hierarchical Roles      |  | - Multi-Vendor RFQ Tracking   |  |
|  | - JWT Access & Refresh    |  | - Dynamic Permissions     |  | - Quotation Matrix Comparison |  |
|  | - Single-Flight Refresh   |  | - User Override Engine    |  | - AI Extraction (GPT-4o/Gemini|  |
|  +---------------------------+  +---------------------------+  +-------------------------------+  |
|  | Master Data & Catalogs    |  | Sourcing & Partners       |  | Master Planning Engine        |  |
|  | - Dynamic Specs Engine    |  | - Suppliers & Contacts    |  | - Dynamic Sheet/Row/Col/Cell  |  |
|  | - Multilevel Categories   |  | - Public Tokenized Portal |  | - Container CBM Optimization  |  |
|  | - Currencies & Geography  |  | - Buyers & Credit Limits  |  | - Cell Status Tagging Engine  |  |
|  +---------------------------+  +---------------------------+  +-------------------------------+  |
|  | Background Workers        |  | Real-Time Event Engine    |  | Governance & Recovery         |  |
|  | - IMAP Email Inbound Poll |  | - WebSocket Manager       |  | - Immutable Audit Logger      |  |
|  | - AI Attachment Extractor |  | - JSON Mutation Broadcast |  | - Universal Soft-Delete / Bin |  |
|  | - Cache Eviction Daemon   |  | - Conflict Prevention     |  | - Field-Level JSON Delta Diff |  |
|  +---------------------------+  +---------------------------+  +-------------------------------+  |
+--------------------------------+----------------------------+-------------------------------------+
                                 |                            |
+--------------------------------v-------+  +-----------------v-------+  +--------------------------+
|            PERSISTENCE TIER            |  |       CACHING TIER      |  |       STORAGE TIER       |
| PostgreSQL / SQLite (SQLAlchemy Async) |  | Redis / InMemoryCache   |  | Local / Cloud Uploads    |
| Alembic Versioned Migrations           |  | Namespace-Based Cache   |  | Quotations, PDFs, Images |
+----------------------------------------+  +-------------------------+  +--------------------------+
```

### 1.1. Core Architectural Pillars
1. **Strict Onion Architecture**: `routes -> services -> repositories -> database`. Routes handle transport and authentication; services orchestrate business validation, audit logging, and caching; repositories build optimized async SQLAlchemy queries.
2. **Unified Response Envelope**: Every HTTP response is structured as `{ "success": true, "data": ..., "meta": ..., "error": null }`. Error responses provide the same uniform contract with a standardized error code and debug message.
3. **Domain Exceptions Hierarchy**: Business logic raises framework-agnostic exceptions (`NotFoundException`, `ConflictException`, `ForbiddenException`, `ValidationException`) translated into standard HTTP envelopes at the middleware boundary.
4. **Optimistic Concurrency**: Records implement integer `version` attributes to prevent dirty overwrites during simultaneous concurrent edits.
5. **Universal Soft-Deletion**: Records inherit `SoftDeleteMixin` (`deleted_at`, `deleted_by`). Deletion operations move data to the Recycle Bin for one-click restoration.

---

## 2. Technology Stack & Dependencies

### Backend Stack
- **Framework**: FastAPI (Python 3.11+) with Uvicorn ASGI server.
- **ORM & Database**: SQLAlchemy 2.0 Async (`asyncpg` for PostgreSQL, `aiosqlite` for local dev) with Alembic migration versioning.
- **Data Validation**: Pydantic v2 schemas for high-throughput serialization.
- **Authentication**: Argon2id password hashing (`argon2-cffi`) and PyJWT (HMAC-SHA256).
- **Caching**: Dual-backend (`InMemoryCacheBackend` with LRU eviction and Redis client).
- **AI Processing**: OpenAI GPT-4o-mini / Google Gemini multimodal APIs for quote extraction from PDF/Excel/image documents.
- **PDF & Office Tooling**: `ReportLab` for PDF datasheets and `openpyxl` / `pypdf` for spreadsheet and document parsing.

### Frontend Stack
- **Core Framework**: React 18 with strict TypeScript typing.
- **Build Engine**: Vite with optimized Rollup code splitting.
- **Styling**: Vanilla CSS (IHM Design System) with custom tokens (glassmorphism, vibrant badges, accessible inputs).
- **Data Utilities**: `SheetJS` (xlsx) and `PapaParse` for client-side spreadsheet import/export.
- **Real-Time Client**: Native WebSocket `LiveClient` with automatic exponential backoff reconnection.

---

## 3. Directory Layout & File Map

```
ERP_Main_Claude/
├── AGENTS.md                  # Mandatory AI and Developer Living Documentation Policy
├── MODULES_AND_FEATURES_TEST_MANUAL.md # Complete UI views, fields, actions & test checklists
├── doc/
│   ├── README.md              # Central documentation index
│   ├── PROJECT_STATUS_HANDOVER.md # Master onboarding, active consignments & server handover
│   └── SYSTEM_DOCUMENTATION.md# Master Unified Architecture & Feature Manual (THIS FILE)
├── backend/
│   ├── app/
│   │   ├── api/v1/router.py   # Versioned API route registration
│   │   ├── audit/             # Immutable audit log models, service, and routes
│   │   ├── auth/              # JWT auth, Argon2id, session tracking, rate limiting
│   │   ├── buyers/            # Buyer directory, contacts, addresses, credit limits
│   │   ├── cache/             # Redis / in-memory cache manager, cleanup worker
│   │   ├── common/            # BaseRepository, BaseService, Pagination, Storage, Importer, Email
│   │   ├── core/              # Config, Responses, Exceptions, Exception Handlers, Logging
│   │   ├── database/          # Async Engine, Session DI, Declarative Base Mixins
│   │   ├── employees/         # Employee (workforce/person) records, optional User Account link
│   │   ├── events/            # WebSocket connection manager and broadcast bus
│   │   ├── inquiries/         # RFQs, AI Extractor, IMAP email poller, WeCom WeChat service
│   │   ├── masters/           # Brands, Categories, Subcategories, Geography, Currencies
│   │   ├── middleware/        # Correlation ID, Logging, Security, Rate Limiter
│   │   ├── organizations/     # Enterprise profile settings
│   │   ├── org_structure/     # Leadership, Positions, Reporting Structure (IAM upgrade)
│   │   ├── planning/          # Dynamic spreadsheet planning grid, container CBM calculator
│   │   ├── rbac/              # Roles, Permissions, User Overrides, Effective Permissions
│   │   ├── suppliers/         # Supplier directory, tokenized public quote portal
│   │   ├── trash/             # Universal Recycle Bin recovery service
│   │   ├── users/             # User accounts, deactivation, force logout, reporting managers
│   │   └── main.py            # Composition root, lifespan lifecycle, middleware wiring
│   ├── alembic/               # Database schema version migrations
│   ├── scripts/               # Migration, seeding, and maintenance tools (setup_neon_databases.py, shift_supabase_to_neon.py, sync_uploads_to_supabase.py)
│   └── requirements.txt       # Python dependencies
└── frontend/
    ├── src/
    │   ├── components/        # AppShell, MasterPage, SearchableDropdown, ImportWizard, UI, icons
    │   ├── lib/               # API client, Auth Context, Navigation registry (nav.ts), WebSockets
    │   ├── pages/             # Inquiries, Planning, Suppliers, Buyers, Users, Rbac, Profile
    │   │   ├── masters/       # Products, Brands, Categories, Currencies, Cities, Countries
    │   │   └── org/           # Positions, Organization Chart (dynamic org hierarchy)
    │   ├── styles/            # IHM Design System stylesheet (style.css, pages.css)
    │   └── types/             # Strict TypeScript domain interfaces
    └── package.json           # Frontend dependencies and build scripts
```

---

## 4. Database Architecture & Universal Mixins

All database models reside in `backend/app/` and inherit from declarative mixins defined in `backend/app/database/base.py`:

```python
class UUIDPrimaryKeyMixin:
    """Provides a RFC 4122 UUID v4 primary key column."""
    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)

class TimestampMixin:
    """Tracks UTC creation and update timestamps."""
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

class SoftDeleteMixin:
    """Provides non-destructive lifecycle management."""
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    deleted_by: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)

class VersionMixin:
    """Provides optimistic concurrency control."""
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
```

### 4.1. Neon Serverless Multi-Database Topology & Driver Engine (`setup_neon_databases.py`, `shift_to_singapore.py`)
- **Three Isolated Logical Databases in Single Project Cluster (`ERP-Cluster`)**:
  - `yinglima_erp`: Dedicated to the China procurement, quotation sourcing, and container shipment planning lifecycle.
  - `inhyma_erp`: Dedicated to the India domestic distribution, multi-branch, and buyer invoicing lifecycle.
  - `erp_main`: Central master repository and golden template for future company deployments.
- **Singapore (ap-southeast-1) Low-Latency Region Deployment**:
  - Successfully migrated from Ohio (`us-east-2`, ~368ms round-trip latency) to Singapore AWS (`ap-southeast-1`, ~170ms round-trip latency, cutting network latency by >50%).
  - Live Singapore Pooled Endpoint: `ep-twilight-base-azwy3ofw-pooler.c-3.ap-southeast-1.aws.neon.tech/yinglima_erp`.
  - Zero data loss: All 49,848 rows across 54 tables and 93 foreign key constraints verified with 100% parity.
- **Optimistic Concurrency & Missing Columns Alignment (`alembic/versions/f9a0b1c2d3e4_ensure_all_version_columns.py`)**:
  - Ensures `version INTEGER NOT NULL DEFAULT 1` exists across all master tables (`hsn_codes`, `units_of_measurement`, `master_companies`, `inquiry_items`, `supplier_types`, `buyer_types`, `consignment_codes`).
  - Ensures `item_description TEXT` exists on `planning_sheets`.
  - Fixes HTTP 500 errors on `/masters/hsn`, `/masters/uom`, and `/planning/sheets`.
- **Connection Pooling & Statement Caching**:
  - Configures `DATABASE_DISABLE_STATEMENT_CACHE=true` in `backend/.env` to avoid prepared statement conflicts with PgBouncer transaction pooling.
- **Driver Parameter Compatibility Matrix**:
  - **`asyncpg` Engine**: Strictly requires `?ssl=require`. Passing `?sslmode=require` causes `TypeError: connect() got an unexpected keyword argument 'sslmode'`.
  - **`psycopg2` Engine / Alembic**: Strictly requires `?sslmode=require`. Passing `?ssl=require` raises an invalid keyword argument error in psycopg2.
  - **Dynamic Resolution (`app.core.config.py`)**: The `sync_database_url` property dynamically inspects query parameters and converts `?ssl=require` to `?sslmode=require` seamlessly across migrations and background sync tools.
- **Switching Databases**:
  - Separate per-database configurations: `backend/.env.yinglima_erp`, `backend/.env.inhyma_erp`, `backend/.env.erp_main`.
  - To activate a company's database, copy its configuration to `backend/.env` (e.g. `copy .env.yinglima_erp .env` or `copy .env.inhyma_erp .env`).
- **Complete Supabase to Neon Migration & 100% Parity (September 2026)**:
  - Total tables in Supabase: **77** | Total tables in Neon: **77** (Zero missing tables, zero missing rows).
  - All 21 Task Management & Notification tables (`notifications`, `tasks`, `task_subtasks`, `task_assignees`, `task_comments`, `task_escalations`, `task_labels`, `task_attachments`, `task_sprints`, etc.) fully migrated with all 426 notifications, 196 tasks, and related attachments.
  - All 184 country ISO2 and ISO3 codes synced.
  - Complete sync of all 20 `inquiry_messages` records.
  - Schema alignment for `products` (`packaging_length`, `packaging_width`, `packaging_height`, `packaging_weight`, `master_box_qty`, `supplier_id`) and `planning_columns.description`.
  - Audited via `backend/scripts/compare_supabase_and_neon.py`.

---

## 5. Complete Data Models & Entity Dictionary

```mermaid
erDiagram
    USERS ||--o{ USER_ROLES : assigned
    ROLES ||--o{ USER_ROLES : holds
    ROLES ||--o{ ROLE_PERMISSIONS : defines
    PERMISSIONS ||--o{ ROLE_PERMISSIONS : grants
    USERS ||--o{ USER_PERMISSIONS : overrides
    PERMISSIONS ||--o{ USER_PERMISSIONS : target
    USERS ||--o{ SESSIONS : registers

    ROLES ||--o{ ROLES : "parent_department (nested)"
    ROLES ||--o{ DEPARTMENT_HIERARCHY : "parent_department (multi)"
    ROLES ||--o{ DEPARTMENT_HIERARCHY : "child_department (multi)"
    USERS ||--o{ EMPLOYEE_POSITION_ASSIGNMENTS : holds
    POSITIONS ||--o{ EMPLOYEE_POSITION_ASSIGNMENTS : filled_by
    ROLES ||--o{ DEPARTMENT_LEADERSHIP_ASSIGNMENTS : led_by
    USERS ||--o{ DEPARTMENT_LEADERSHIP_ASSIGNMENTS : leads
    USERS ||--o{ EMPLOYEE_REPORTING_RELATIONSHIPS : "reports (as person)"
    USERS ||--o{ EMPLOYEE_REPORTING_RELATIONSHIPS : "manages (as manager)"

    BUYERS ||--o{ INQUIRIES : initiates
    INQUIRIES ||--o{ INQUIRY_ITEMS : contains
    INQUIRIES ||--o{ INQUIRY_SUPPLIER_QUOTES : receives
    SUPPLIERS ||--o{ INQUIRY_SUPPLIER_QUOTES : submits
    
    CATEGORIES ||--o{ SUB_CATEGORIES : contains
    SUB_CATEGORIES ||--o{ PRODUCTS : classifies
    BRANDS ||--o{ PRODUCTS : manufactures
    PRODUCTS ||--o{ INQUIRY_ITEMS : references
    
    PLANNING_SHEETS ||--o{ PLANNING_COLUMNS : defines
    PLANNING_SHEETS ||--o{ PLANNING_ROWS : contains
    PLANNING_ROWS ||--o{ PLANNING_CELLS : stores
    PLANNING_COLUMNS ||--o{ PLANNING_CELLS : formats
```

---

## 6. Security, Authentication & Session Engine

### 6.1. Dual-Token JWT & Single-Flight Refresh
- **Access Token**: 15-minute expiration, contains `sub` (User UUID), `username`, `roles`, and base claims.
- **Refresh Token**: 7-day expiration, stored cryptographically in the `refresh_tokens` table. Each refresh token is strictly **single-use** and rotated upon every `/auth/refresh` call.
- **Single-Flight Frontend Guard**: When multiple parallel API calls encounter a `401 Unauthorized`, only a single refresh request is dispatched. All concurrent requests wait on the same promise, preventing race conditions and unexpected logouts.

### 6.2. Argon2id Password Encryption
Passwords are hashed using Argon2id with strict parameters:
- Time cost: 3 iterations
- Memory cost: 65,536 KB
- Parallelism: 4 threads
- Salt length: 16 bytes

### 6.3. Active Session Governance
Every authentication creates a record in the `sessions` table capturing IP address, location, browser user-agent, and device category. Users and administrators can inspect active sessions and revoke compromised devices remotely.

### 6.4. Soft-Deleted Account Authentication Immunity
In accordance with system security standards, soft-deleted user accounts (`deleted_at IS NOT NULL`) are strictly prevented from authenticating:
- **Login Defense**: `UserRepository.get_by_identifier` automatically excludes soft-deleted accounts via `_base_select()`. Attempts to log in with credentials of a soft-deleted user fail immediately with `401 Unauthorized: Invalid username/email/phone number or password.`, mirroring the exact security response of hard-deleted accounts without leaking account existence.
- **Active Token Rejection**: Any in-flight JWT access token presented for a soft-deleted user is rejected during dependency verification (`verify_access_token`) with `401 Unauthorized: User account no longer exists.`.
- **Property Guard**: `User.can_login` evaluates strictly to `False` if `deleted_at` is set.
- **Restoration**: If an administrator restores the user from the Recycle Bin (clearing `deleted_at`), normal authentication capabilities are restored.

---

## 7. RBAC Engine, Departments & Effective Permissions

## 7. RBAC Engine, Departments & Effective Permissions

The platform unifies **Roles** and organizational **Departments** onto the same underlying entity (`roles` table). A Role carries software permission bundles (`role_permissions`) AND real organizational placement (`code` and `parent_department_id` for departmental hierarchy with server-side cycle detection). Assigning a user to a department grants that department's permissions and places the person in the organizational unit. Individual per-user overrides (`user_permissions` ALLOW/DENY) remain available for any user who needs to deviate from department defaults.

### 7.1. Effective Permission Calculation
User capabilities are calculated dynamically at request time:

$$\text{EffectivePermissions} = \left( \bigcup_{r \in \text{UserRoles}} \text{RolePermissions}(r) \cup \text{DirectGrants} \right) \setminus \text{DirectDenies}$$

A user may be assigned any number of Roles simultaneously (`POST /users/{id}/roles` is additive, carrying assignment metadata `assignment_type` [PRIMARY, SECONDARY, TEMPORARY, PROJECT, ACTING], `is_primary`, and effective dates).

*Super Admin Rule:* Users with the `super_admin` role bypass checks and possess all permissions unconditionally.

### 7.2. Department Managers & Leadership
- Department members can be designated as **Department Managers** or leadership assignees (`department_leadership_assignments`).
- Managers display a `MANAGER` badge on the department roster.
- Administrators can configure direct per-user permission overrides (`🔑 Edit permissions`) to give managers elevated operational privileges (e.g. deletion, approval, bulk exports) without altering the base department role.
- Setting a manager automatically updates the `manager_id` reporting hierarchy for department members.

### 7.3. Multi-Parent & Multi-Child Department Hierarchy
- **Entity Model (`department_hierarchy`)**: Supports many-to-many relationships between organizational departments (`parent_department_id` $\leftrightarrow$ `child_department_id`).
- **Bidirectional Relationship**:
  - A parent department can possess **multiple child departments** (sub-departments).
  - A child department can report to or be nested under **multiple parent departments**.
- **DAG Cycle Prevention**: Traversing both `department_hierarchy` and legacy `roles.parent_department_id` via breadth-first search prevents direct or indirect recursive loops across the departmental graph. Attempted cycles fail fast with HTTP `409 Conflict` ("This would create a circular department hierarchy.").
- **Backward Compatibility**: Automatically mirrors and backfills the primary parent to `roles.parent_department_id` for legacy single-parent queries.

---

## 8. Module-by-Module Technical Breakdown

### 8.1. Authentication & Active Sessions
- **Endpoints:** `POST /auth/login`, `POST /auth/refresh`, `POST /auth/logout`, `GET /auth/me`, `GET /auth/sessions`, `DELETE /auth/sessions/{id}`.
- **Features:** Self-service password change, active session listing, device revocation, and forced password reset on first login. Users with `has_login=False` cannot authenticate and are rejected before password hashing.

### 8.2. Users & HR Profile Management (Unified Person & Workforce Directory)
- **Endpoints:** `GET /users`, `GET /users/all`, `GET /users/department-manager/{role_id}`, `POST /users`, `GET /users/{id}`, `PATCH /users/{id}`, `POST /users/{id}/reset-password`, `POST /users/{id}/roles`, `DELETE /users/{id}/roles/{role_id}`.
- **Features:** Unified person directory supporting both ERP login users and workforce members with no system credentials (`has_login=False` -- factory workers, drivers, temporary labor, consultants).
  - **Account Fields:** `username`, `email`, `phone`, `password` (required when `has_login=True`; optional/null when `has_login=False`), and optional initial `position_id`.
  - **HR Attributes:** Employee Code, Contact Numbers, Gender, Date of Birth, Date of Joining, Employment Type, Status, Address, Emergency Contact, and Notes. **Last Name is optional**.
  - **Default "User" Role Assignment:** If an individual is not explicitly assigned any department/role upon creation (or if unassigned), the system automatically assigns the default system **"User"** role. When all roles are removed from a person, the system automatically falls back to assigning the "User" role.
  - **Position Assignment & Editing:** When creating an account, an optional **Position** dropdown (extracted from the active Positions catalog) can be selected to establish an immediate primary position assignment. In the **Edit User Profile & HR Details** drawer, administrators can also view, update, reassign, or unset the user's primary position directly alongside the Reporting Manager selector, with changes synchronized atomically to `employee_position_assignments`.
  - **Department & Manager Auto-Wiring:** When selecting an initial department in the Create User modal, the system calls `/users/department-manager/{role_id}` to automatically detect and pre-fill the department's active manager, with manual override capability.
  - **Positions & Reporting:** Profile Drawer displays held positions (`GET /positions/holders-for-user/{id}`), reporting managers (`GET /reporting/managers/{id}`), and direct reports (`GET /reporting/direct-reports/{id}`).
  - **Multi-Role Assignment:** Assign any number of roles/departments with `assignment_type` (PRIMARY, SECONDARY, TEMPORARY, PROJECT, ACTING), `is_primary`, and effective date ranges.
  - **Account Deactivation Policy & Permanent Retirement of User Deletion:** User deletion is permanently retired and disabled system-wide (`DELETE /users/{id}` returns 400 Bad Request) to preserve audit integrity and historical transaction data. Deactivating a user (`POST /users/{id}/deactivate`) marks their account `INACTIVE` (`is_active=False`), immediately terminates all active sessions, and prevents login or token refresh. Deactivated accounts can be reactivated by administrators (`POST /users/{id}/activate`).
  - **Collective Multi-Select & Bulk Deactivation:** The Users directory supports selecting multiple accounts via row/header checkboxes to execute bulk deactivation with built-in safety guardrails (protecting the administrator's own account, super-admin accounts, and already inactive accounts).
  - **Unified Edit User Profile & HR Details Drawer (Integrated Department Management):** The previous separate "Manage Departments" row action is now consolidated directly into the "Edit Profile" drawer. Administrators can manage basic identity, contact info, HR attributes, reporting manager, positions, and add/remove **Department & Role Assignments** (with assignment types and primary flags) in one unified interface without switching modals.
  - **Immediate Real-Time Force Logout:** "Force Logout" (`POST /users/{id}/force-logout`) provides guaranteed real-time session termination. It revokes device sessions in the database, caches a revocation timestamp (`auth_force_logout:{user_id}`) to instantly reject any in-flight access tokens on subsequent API calls, and pushes a real-time WebSocket disconnect event (`FORCE_LOGOUT`, code `4001`) that immediately clears client storage and redirects the active user to the login screen.

### 8.3. Departments & Permissions (RBAC & Org Structure)
- **Endpoints:** `GET /rbac/roles`, `POST /rbac/roles`, `PATCH /rbac/roles/{id}`, `DELETE /rbac/roles/{id}`, `POST /rbac/roles/{id}/delete-with-reassignment`, `PUT /rbac/users/{id}/permissions/bulk`, `GET /rbac/roles/{id}/hierarchy`, `POST /rbac/roles/{id}/parents`, `DELETE /rbac/roles/{id}/parents/{parent_id}`, `POST /rbac/roles/{id}/children`, `DELETE /rbac/roles/{id}/children/{child_id}`.
- **Features:** Department role definitions with optional short department `code` (e.g. `SALES`), multi-parent department nesting, safe deletion with user reassignment modal, and permission cloning.
  - **Child Departments Card:** Dedicated card directly beneath "Users in this Department" in the left column of `/rbac`, displaying connected sub-departments, member counts, quick view navigation, and inline add/remove child controls.
  - **Multi-Parent Department Management:** Department Details allows assigning multiple parent departments with removable tag badges and immediate unlinking without resaving the entire role.
  - **Real-Time Bidirectional Sync:** Adding a child department in Operations instantly updates the child's parent roster, and vice versa.
  - **Cycle Prevention:** Strict validation prevents assigning an ancestor as a child or vice-versa.

### 8.4. Master Data & Generic Catalogs
- **Modules:** Brands, Categories, Sub-Categories, Countries, States, Cities, Currencies, Units of Measurement (UOM), HSN/SAC Codes, Buyer Types, Supplier Types, and Operating Companies.
- **Features:** Built on the unified `MasterPage.tsx` engine providing uniform search, pagination, validation, modal creation, and cached lookup resolution (`nameResolver.ts`).
- **Universal Template & Validator Alignment**:
  - Full bidirectional alignment between UI sample templates (`sampleTemplate.ts`), import parsers, validators, and backend models across all master modules.
  - Automatic code auto-generation during import when `code` is omitted in the file (Brands: `BR-XXX`, Categories: `CAT-XXX`, Buyer Types: `BT-XXX`, Supplier Types: `ST-XXX`, UOM: derived from name/short name), aligning with UI forms that treat `code` as optional.
  - Multi-alias column resolution supports all UI column labels (`Brand Name`, `Category Name`, `Sub-Category Name`, `Buyer Type Name`, `Supplier Type Name`, `Organization Name`, `Country Name`, `ISO Code`, `Province / Region Name`, `City Name`, `Currency Name`, `Currency Code (ISO 4217)`, `HSN Code`, `Refund VAT %`, `GST %`, `UOM Name`, `Short Name`).
  - Resilient relational resolution: Sub-Categories, States, and Cities resolve linked parents by both code and name with case-insensitive fallback.
  - Name-based deduplication (`dedupe_keys=("name",)`) ensures in-file duplicate prevention reflects the natural business identifier across all masters.

### 8.5. Product Catalog & Dynamic Specification Builder
- **Endpoints:** `GET /masters/products`, `POST /masters/products`, `GET /masters/products/{id}`, `PATCH /masters/products/{id}`, `DELETE /masters/products/{id}`, `POST /masters/products/import`, `GET /masters/products/export`.
- **Features:** Dynamic JSON specification builder allowing arbitrary technical specifications (e.g. Dimensions, Voltage, Speed, Material), multi-image upload, primary supplier auto-detection, and ReportLab PDF datasheet generation.
- **Server-Side Pagination & Subquery Search Engine:** Uses standard 50-item/page server-side pagination with `ProductRepository._apply_search`. Applies case-insensitive subqueries across direct product attributes (`product_code`, `product_name`, `product_name_tally`, `product_name_invoice`, `barcode`, `specification`, `description`, `material`, `color`) and linked masters (`Brand`, `ProductCategory`, `ProductSubCategory`, `HsnCode`, `UnitOfMeasurement`) using PostgreSQL `exists()` clauses. Completely eliminates client-side 10,000-row batch loading and Vite proxy 500 timeout crashes over cloud database connections.

### 8.6. Supplier Directory & Tokenized Public Portal
- **Endpoints:** `GET /suppliers`, `POST /suppliers`, `PATCH /suppliers/{id}`, `POST /suppliers/{id}/contacts`, `POST /suppliers/import`, `GET /suppliers/export`.
- **Features:** Vendor directory with multi-contact management, payment terms, and bank details. Generates secure, tokenized public quote portal links (`/quotes/public/:token`) allowing vendors to submit bids without system accounts.
- **Dynamic Geography & Phone Dialing Code Sync:** When changing Country in the Supplier Profile (e.g., China &rarr; India), Province and City dropdowns reset automatically, and the country dialing code prefixes on Calling Number, WhatsApp Number, and WeChat Number auto-update dynamically (e.g., `+86 7304240120` &rarr; `+91 7304240120`).

### 8.7. Buyer & Client Management
- **Endpoints:** `GET /buyers`, `POST /buyers`, `PATCH /buyers/{id}`, `DELETE /buyers/{id}`, `POST /buyers/import`, `GET /buyers/export`.
- **Features:** Client directory with credit limits, client grades (A, B, C, Premium), multi-address delivery matrix (Billing, Shipping, Warehouse), and bulk import/export.
- **True 3-Way Duplicate Detection (Note 66 in `buyerclient.txt`)**:
  - Independent, multi-factor uniqueness checking across three distinct vectors: **Company Name**, **Calling Number**, and **WhatsApp Number**.
  - **Company Name Uniqueness**: Case-insensitive exact match check is strictly enforced in `BuyerRepository.find_duplicate` and `BuyerService.import_file` even if phone numbers are omitted or different, ensuring company names cannot be duplicated.
  - **Cross-Phone Collision Detection**: Strips non-digit characters and ensures phone numbers ($\ge 6$ digits) cannot collide with another buyer's primary calling number OR WhatsApp number (e.g. using an existing buyer's calling number as a WhatsApp number is immediately flagged and rejected).
  - **Real-Time Client-Side Feedback**: Form inputs display live inline warning alerts (`⚠️ {fieldDuplicates.companyWarning}`, `⚠️ {fieldDuplicates.callingWarning}`, `⚠️ {fieldDuplicates.whatsappWarning}`) as the user types, blocking form submission if any duplicate is detected.
  - **Safe Self-Update**: `exclude_id` ensures editing a buyer's existing profile does not trigger false-positive collisions against its own record.
  - **In-File & Database Deduplication during Import**: Pre-scans batch records and cross-references existing database entries, rejecting intra-file and cross-database duplicates with clear comparative conflict details.

### 8.8. Inquiries, RFQs & AI Quotation Extractor
- **Endpoints:** `GET /inquiries`, `POST /inquiries`, `POST /inquiries/{inquiry_id}/items/import`, `GET /inquiries/sample-template`, `POST /inquiries/{id}/rfq/dispatch`, `POST /inquiries/{id}/send-email-message`, `GET /inquiries/{id}/messages`, `POST /inquiries/{id}/quotes/manual`, `POST /inquiries/{id}/quotes/extract-pdf`, `POST /inquiries/{id}/convert-to-proforma`, `GET /inquiries/{id}/compare-matrix`.
- **Features:**
  - 3-layer RFQ and Quotation management lifecycle: `Buyer Directory` $\rightarrow$ `Consignments` $\rightarrow$ `Line Items & Quotation Matrix`.
  - **Inquiry Lifecycle Tabs & Bulk Actions Engine (Matching Product Master Pattern)**:
    - **Layer 1 (Company Dashboard)**:
      - **Lifecycle Filter Tabs**: `All (N)`, `Pending (N)`, `Ongoing (N)`, `Approved (N)`, `Completed (N)` rendered directly above the table card with blue indicator underline and dynamic badge counters.
      - **Interactive KPI Cards**: The 5 top summary cards (`Pending`, `Approved`, `Ongoing`, `Completed`, `Total Order`) are clickable, interactive filter triggers with active colored borders and elevated shadows that smoothly sync with the Lifecycle Tabs.
      - **Bulk Actions Dropdown (`BulkActionsDropdown`)**: Positioned at the top-right of the table beside `+ ADD NEW`. Provides 1-click **Bulk Delete (Move to Trash)** with confirmation dialog and pending protection across selected buyer companies.
    - **Layer 2 (Consignments Table)**:
      - **Lifecycle Filter Tabs**: `All (N)`, `Proposed (N)`, `Partial Approved (N)`, `Fully Approved (N)` placed above the consignment table alongside the live search input.
      - **Master & Row Multi-Select Checkboxes**: Table header contains a master "Select All" checkbox; rows have individual checkboxes bound to `selectedInquiryIds`.
      - **Bulk Actions Dropdown**: Positioned at the top-right beside `+ Add Inquiry Item`. Enables 1-click **Bulk Delete (Move to Trash)** for selected consignments and child items.
  - **Inquiry Product Bulk Import (Excel .xlsx, .xls & .csv)**:
    - Dedicated full-page import workflow in Layer 3 Consignment Workspace (`ItemsView`) modeled identically on the Supplier Import system.
    - Unified `Imp / Exp ▾` action button: provides *Sample File* download, *Import* (navigates to the dedicated import view), and *Export* (`.xlsx` or `.csv`).
    - Dedicated import interface featuring drag/drop file upload, instant `📥 Download Sample CSV Template` button, format limits (max 5,000 rows, max 8 MB), and clear validation guidelines.
    - **Interactive Column Mapping Wizard (`WizardModal`)**: Pre-parses files in-browser, auto-matches sheet headers to ERP fields using normalized synonyms (`MATCHED` badge), displays a live 5-row preview table, and validates rows before uploading.
    - **Intelligent Product Master Resolution**: Resolves items first by Product Code / SKU (exact match) and falls back to Product Name or Tally Name. Automatically assigns the product's official Unit of Measurement (`uom_id`) and sets `requires_license` flags (highlighted in red) without requiring manual data entry.
    - **Robust Error Handling & Rollup Recomputation**: Validates positive quantities and item statuses (`Proposed` or `Approved`, default `Proposed`). Failed rows are reported with exact spreadsheet row numbers and explanations. On completion, consignment weight, CBM, and status rollups recompute immediately and dispatch real-time WebSocket events (`inquiry.updated`).
  - **Interactive Inline Email Composer (Gmail/Figma-Style)**: Located in the Inquiries -> Emails tab. Allows users to write custom follow-up emails or replies directly to suppliers, auto-selects recipient emails from known suppliers, pre-fills context-aware subject lines, attaches files, and immediately dispatches outbound SMTP emails. Dispatched emails are instantly recorded into the communication timeline.
  - **Dynamic Supplier Resolution & Email Deduplication**: `GET /inquiries/{id}/messages` and the frontend Emails tab automatically resolve unlinked raw recipient/sender emails to official Supplier company names via `supplier_emails`, unifying company names and eliminating raw email duplicates in the communication filter dropdown.
  - **Strict 1-Quote AI Extraction Policy**: The inbound AI parsing worker only extracts quotation terms from initial inbound supplier replies. Subsequent follow-up correspondence and chats between sales personnel and suppliers are logged directly to the email timeline without AI duplication or spurious quotation matrix modifications. Communication badges dynamically reflect whether a quotation record actually exists in the matrix (displaying quote number and price) or whether it represents a discussion thread.
  - All Expected Receiving Date date-pickers enforce `min={today}` to disable selecting past dates.
  - **Resilient Consignment Code Generation**: The Quick Inquiry drawer automatically cross-references both local and global consignment codes. If an entered or suggested code already exists for the selected buyer, it seamlessly links to the existing code ID instead of crashing with HTTP 409 Conflict.
  - **Safe Non-Destructive Consignment Item Updates**: Modifying a consignment via Quick Inquiry updates existing product lines in-place via `PATCH /{inquiry_id}/items/{item_id}` and appends newly added items via `POST /items/bulk`, eliminating destructive full-consignment item wipes and safely preserving existing quotation records, RFQs, and communication histories.
  - **Inline Modal Error Banners**: All inquiry creation drawers and modals render contextual inline error banners directly inside the modal viewport so validation issues are immediately visible without being occluded by full-screen drawer backdrops.
  - **Contextual UOM Indicator**: Item creation modals dynamically resolve and display the selected product's Unit of Measurement (e.g. `PCS`, `SET`, `KG`) directly alongside the Quantity input field.
  - Outbound WeChat RFQ engine automatically resolves supplier 11-digit mobile numbers to WeCom User IDs via Tencent API using `httpx`. Validates Tencent API response codes (`errcode: 0` vs errors like `60020` unwhitelisted IP), only marking dispatches as delivered upon confirmed Tencent ingestion and logging explicit delivery failure diagnostics if rejected.
  - Supabase Cloud Storage integration handles all quotation PDF attachments.
  - Full RFQ status progression: `DRAFT` $\rightarrow$ `SENT_TO_SUPPLIERS` $\rightarrow$ `QUOTES_RECEIVED` $\rightarrow$ `UNDER_EVALUATION` $\rightarrow$ `APPROVED` $\rightarrow$ `ORDER_PLACED` $\rightarrow$ `CLOSED`.
  - Side-by-side vendor quotation comparison matrix with lowest bid and fastest turnaround highlighting.
  - Multimodal AI quote extractor parsing PDFs, Excel sheets, and email text into structured bids (`ExtractedQuotation`).
  - 1-Quote negotiation iteration tracking and turnaround time metrics.

### 8.9. Automated Inbound IMAP Email Worker
- **File:** `backend/app/inquiries/email_inbound_worker.py`
- **Features:** Background daemon running every 60 seconds. Connects via secure IMAP, checks for inquiry reference tokens in email subjects/headers, downloads quote attachments, triggers AI extraction, and logs quotation bids automatically. Avoids duplicate processing via `processed_email_ids.json`.

### 8.10. Master Shipment Planning Grid & Container Calculations
- **Endpoints:** `GET /planning/sheets`, `POST /planning/sheets`, `GET /planning/sheets/{id}/grid`, `GET /planning/sheets/{id}/filter-values`, `GET /planning/organization-search`, `POST /planning/rows`, `POST /planning/columns`, `PATCH /planning/cells`, `POST /planning/container-calc`.
- **Features:**
  - Dynamic grid model (`planning_sheets` $\rightarrow$ `planning_rows` $\rightarrow$ `planning_columns` $\rightarrow$ `planning_cells`).
  - Column data types (`TEXT`, `NUMBER`, `DATE`, `BOOLEAN_YN`) and source types (`MANUAL`, `LINKED_LOOKUP`, `AGGREGATE`, `FORMULA_CALCULATION`).
  - **Organization-Wide Cross-Branch Search Bar**: Top-level search bar dynamically scans across all branches of the currently viewed organization (e.g. Inhyma Mumbai, Inhyma Ahmedabad, Inhyma Indore) via `/planning/organization-search`. Provides instant branch-wise result counts, previews matching items, filters the active grid live, and allows one-click switching to any branch tab.
  - **Full-Dataset Column Filtering & Live Search**: Filter popover dynamically queries distinct values and occurrence counts across all records on the sheet (1384+ items) via `/planning/sheets/{id}/filter-values` with debounced text search, ensuring unrendered and newly created Product Master records are fully searchable.
  - **Automated Product Master Auto-Population**: Automatically syncs and materializes unlinked products for the sheet's organization and branch upon sheet load or filter search.
  - Cell status color tagging (e.g. `status-ordered`, `status-purchased`).
  - Container calculation engine computing total volume in CBM and payload weight across 20FT, 40FT, 40FT HC, and LCL container configurations.
  - Group-wise subcategory & product sorting.

### 8.11. Audit Trails & JSON Delta Change Diffing
- **Endpoints:** `GET /audit`, `GET /audit/{id}`, `GET /audit/export`.
- **Features:** Immutable audit repository capturing actor, IP, timestamp, action type, and field-level before/after JSON delta diffs across all business entities.

### 8.12. Recycle Bin (Universal Soft-Delete & Recovery)
- **Endpoints:** `GET /trash`, `POST /trash/restore`, `POST /trash/permanent-delete`, `POST /trash/empty`.
- **Features:** Centralized Recycle Bin displaying soft-deleted records across all tables. One-click recovery restores records with full relational integrity. Permanent purge is restricted to Super Administrators.
- **Trash Conflict Detection & One-Click Restore Engine (`backend/app/common/trash_conflict.py`, `TrashConflictModal.tsx`):**
  - **Problem Solved:** When a record (e.g. Category `Test 1`) is soft-deleted, it retains its unique database constraints in PostgreSQL. If a user later attempts to create or rename an active record with that same name or code, standard repository queries (which filter `deleted_at IS NULL`) would return `None`, allowing the service to attempt an `INSERT`. This caused PostgreSQL to throw an `IntegrityError` (`UniqueViolationError`), which FastAPI's catch-all handler reported to the user as an unhandled 500 error: *"An unexpected error occurred."*
  - **Application-Level Pre-Check (`check_trash_or_duplicate`):** Service `create()` and `update()` methods across all 12 Master Data catalogs (Categories, Sub-Categories, Brands, UOM, HSN, Countries, States, Cities, Currencies, Supplier Types, Buyer Types, Companies), Products, Buyers, Suppliers, and Inquiries perform an unfiltered table lookup before saving.
  - **Structured Error Details:** If a match is found with `deleted_at IS NOT NULL`, the backend raises `ConflictException` with structured details: `{ "in_trash": True, "trash_id": "<uuid>", "entity_type": "<Entity>", "name": "<Name>", "code": "<Code>" }`. If an active conflict exists, it raises standard 409 Conflict.
  - **Collision-Free Code Generators (`code_exists_anywhere`):** Code slugs (`CAT-XXX`, `BR-XXX`, `ST-XXX`, `CMP-XXX`) check both active and soft-deleted records so auto-increments never collide with soft-deleted slugs.
  - **Interactive Frontend Modal (`TrashConflictModal.tsx`):**
    - Surfaced across all Master pages (`MasterPage.tsx`), Product Master, Buyer Management (`Buyers.tsx`), Supplier Directory (`Suppliers.tsx`), and Quick Inquiry Drawer (`Inquiries.tsx`).
    - **1-Click Restore Action:** Calls `POST /api/v1/trash/restore`, restores the item, invalidates the global dropdown cache via `cache_manager.invalidate_dropdown()`, refreshes the active list, and smoothly closes the modal.
    - **Zero Form Loss Guarantee:** If the user clicks `[ Change Name / Cancel ]`, the conflict modal dismisses while leaving the user's active creation/edit form completely open with all form fields, tags, and item rows preserved.
    - **Inquiry Workflow Integration:** In `QuickInquiryDrawer`, if a consignment code exists in Trash, the modal offers `[ 🔄 Restore & Append My Items ]`, automatically restoring the consignment and appending newly specified line items into it without losing any of the user's inputs.

### 8.13. Organization & System Profile
- **Endpoints:** `GET /organizations/profile`, `PATCH /organizations/profile`.
- **Features:** Enterprise legal identity, tax/VAT/TIN registration, official address, and base operational currency.

### 8.14. Organization Structure, Positions & Reporting Hierarchy
- **Files:** `backend/app/org_structure/`.
- **Architecture:** Unifies workforce identity into `User` (`has_login` boolean) and department management into `Role` (`code`, `parent_department_id`). Complemented by dedicated organizational modules:
- **Positions (`/positions`):** Designations/titles (e.g. "Sales Manager", "Marketing Advisor"). Managed via `Position` and assigned to users via `employee_position_assignments` (supporting PRIMARY, SECONDARY, ACTING, TEMPORARY roles). Holds no permission or reporting logic. Creation and updates support case-insensitive lifecycle status (`ACTIVE`, `INACTIVE`, `ARCHIVED`).
  - **Employee Assignment Count & Deletion Lock:** `GET /positions` and `GET /positions/all` dynamically aggregate active assignment counts (`employee_count`). If any employees currently hold a position (`employee_count > 0`), the position's delete button is completely frozen and locked on the UI with a lock icon, `cursor: not-allowed`, tooltip warning, and an explanatory modal alert preventing deletion. Server-side deletion enforcement (`PositionService.delete`) strictly rejects deletions with HTTP 409 Conflict if active assignments exist.
- **Department Leadership:** `department_leadership_assignments` records who manages/heads a department (`department_id` references `roles.id`, `employee_id` references `users.id`). The same user may lead multiple departments; a department may have multiple leadership assignees.
- **Reporting Structure (`/reporting`):** Person-to-person reporting lines in `employee_reporting_relationships` (`employee_id` and `manager_employee_id` referencing `users.id`). Supports relationship types (`PRIMARY_REPORTING`, `FUNCTIONAL_REPORTING`, `PROJECT_REPORTING`, `DOTTED_LINE`, `TEMPORARY_REPORTING`) and optional department scoping.
  - **Mandatory Server-Side Cycle Prevention:** `ReportingService.would_create_cycle` verifies the reporting graph before any row is saved, immediately rejecting self-reporting (`A -> A`) and circular chains (`A -> B -> C -> A`) with a 409 Conflict.
  - **Direct Reports Reassignment:** `POST /reporting/reassign-direct-reports/{manager_id}` allows reassigning all direct reports before deactivating a manager.
  - **Set / Move Primary Manager (Org Chart):** `POST /reporting/set-manager/{employee_id}` updates an employee's primary reporting manager in a single atomic transaction, validating cycle prevention and returning the updated relationship.
- **Dynamic Org Chart (`GET /reporting/org-chart`):** Renders the multi-level reporting tree in `/org-chart` using active `PRIMARY_REPORTING` relationships resolved dynamically against `UserRepository.list_all()`, including node `relationship_id`.

### 8.15. Inquiries, Consignments & Bidirectional WeChat / Email RFQ Ingestion
- **Endpoints:** `GET /inquiries`, `POST /inquiries`, `GET /inquiries/{id}/items`, `POST /inquiries/{id}/items`, `POST /inquiries/rfq/bulk-dispatch`, `POST /inquiries/{id}/send-email-message`, `POST /inquiries/{id}/send-wechat-message`, `GET /inquiries/{id}/messages`, `GET /inquiries/wechat/callback`, `POST /inquiries/wechat/callback`.
- **Features:** 3-layer consignment management hierarchy (Buyer $\rightarrow$ Consignment $\rightarrow$ Line Items), bulk RFQ dispatch, multi-channel communication (Email IMAP/SMTP and Tencent WeCom/WeChat), and automated AI quotation extraction.
  - **Interactive WeChat Direct Reply Composer:** Inside the **WeChat Messages** tab, salespersons can type and dispatch chat messages directly back to suppliers on WeChat/WeCom via `POST /inquiries/{id}/send-wechat-message`. Automatically pre-fills the recipient contact from the active chat history (e.g. `ChenXianNing` or `13736331731`), offers a quick supplier dropdown for multi-supplier threads, includes 1-click quick negotiation prompts (bulk discount request, delivery lead time confirmation, shipping terms, proforma invoice request), dispatches via Tencent WeCom API (`cgi-bin/message/send` with `msgtype: "text"`), logs outbound messages to the database with the salesperson's name, and broadcasts live WebSocket updates across all connected clients.
  - **Strict 1st-Conversation AI Quotation Extraction Policy:** AI quotation extraction operates strictly on the initial quotation reply from a supplier for each product line item (`inquiry_item_id`, `supplier_id`). Once the initial quotation is recorded in the Quotation Matrix, all subsequent messages between the sales team and the supplier (negotiations, counter-offers, shipping questions, chit-chat) are saved directly into the conversation history without invoking the AI extractor (0 OpenAI tokens consumed, zero latency, and zero risk of overwriting or duplicating baseline quotations).
  - **Body-First Item Matching for Multi-Product RFQs:** Inbound email replies evaluate the email message body first for explicit product codes and product names before checking the subject line. This prevents email threads with multiple products from falsely inheriting the subject line's first product code, ensuring quotes for secondary items (e.g. Ink Roll vs Band Sealer) route to the correct unquoted line item.
  - **WeCom & WeChat Integration (`wechat_service.py`):** Encrypted bidirectional integration using Tencent WeCom API. Generates bilingual Markdown RFQ cards. Smart resolution resolves both Chinese (`+86`) 11-digit numbers and Indian (`+91`) 10-digit numbers, as well as direct WeCom UserIDs. Strict response validation verifies `errcode: 0` before logging success badges.
  - **Automated Inbound Email Worker (`email_inbound_worker.py`):** Listens via IMAP for incoming supplier replies. Prioritizes exact sender email matching against `SupplierEmail` and `SupplierContact` directories before fallback text search (strictly excluding host procurement company names like "Yinglima" to prevent false positive supplier resolution from email signatures). Robust consignment code matching scans all registered database consignment codes against the subject line (supporting multi-word codes with spaces like `[SEA 1]`, prefix brackets, and case variations) and falls back to explicit product code matching (`#FNB-02391`) before supplier historical RFQ lookup. When an unquoted supplier reply arrives, extracts quotation unit prices, quantities, lead times, and terms via OpenAI GPT-4o-mini, automatically inserts `Quotation` records with mandatory `quantity` fields and product-specific line item matching, and broadcasts real-time WebSocket events.
  - **WeChat Callback Ingestion (`routes.py: /wechat/callback`):** Handles incoming supplier replies from WeChat/WeCom. Decrypts XML payloads, stores conversational message history, accurately extracts consignment codes with spaces and brackets, enforces the 1st-conversation extraction policy (skipping AI for subsequent chatter), and creates initial quotation rows with real-time UI notification.
  - **Supplier Thread Resolution:** Dynamic fallback lookup maps unlinked message sender emails to registered suppliers and prevents duplicate vendor dropdown entries.
  - **Inquiry Consignment Line-Items Export (`GET /inquiries/{id}/export`):** Exports all active line items of a consignment to Excel (`.xlsx`) or CSV (`.csv`) via `InquiryService.export_consignment`. Generates clean tabular spreadsheets with columns: `Sr No`, `Consignment Code`, `Buyer Company`, `Product Code`, `Product Name`, `Quantity`, `UOM`, `Brand Preference`, `Product Specs / Remarks`, `License Required`, `Item Status`, `Tally Entry Posted`, `Quotation Count`, `Best Quote Price`, `Best Quote Currency`, `Selected Supplier`, and `Procurement Remarks`. Automatically resolves the lowest or approved quotation bid per line item and logs immutable audit records (`AuditAction.EXPORT`).


---

## 9. Real-Time WebSocket & Event Synchronization

**File:** `backend/app/events/manager.py` & `frontend/src/lib/live/liveClient.ts`

- **Endpoint:** `ws://<host>:<port>/api/v1/events/ws?token=<JWT_ACCESS_TOKEN>`
- **Behavior:** Broadcasts entity mutation events (`RECORD_CREATED`, `RECORD_UPDATED`, `RECORD_DELETED`) to all connected client tabs. Client pages selectively refresh datasets, preventing concurrent edit collisions.

---

## 10. Multi-Tier Caching Engine

**File:** `backend/app/cache/`

- **Dual-Backend:** Supports Redis in distributed environments and `InMemoryCacheBackend` (with LRU eviction) for local development.
- **Namespaces:** `permissions:<user_id>`, `dropdowns:<entity>`, `dashboard:counts`, `records:<entity>:<id>`.
- **Admin API:** `GET /cache/stats`, `GET /cache/keys`, `DELETE /cache/flush`, `DELETE /cache/namespace/{name}`.

---

## 11. Universal Bulk Import & Export Wizard

**Files:** `frontend/src/components/ImportWizard.tsx`, `backend/app/common/importer.py`

- **Workflow:** File Upload (.xlsx / .csv) $\rightarrow$ Header Fuzzy Matching $\rightarrow$ Column Mapping UI $\rightarrow$ Client-Side Validation $\rightarrow$ Transactional Batch Insertion $\rightarrow$ Error Log Report.
- **Duplicate Prevention Subsystem:**
  - **Buyers (`/buyers/import`):** 3-way deduplication across sheet rows and active database records checking `Company Name` (case-insensitive), `Calling Number`, and `WhatsApp Number`.
  - **Suppliers (`/suppliers/import`):** Company Name deduplication against active database records and in-file batches. Null-safe validation for state code comparisons (`s.code and s.code.lower() == state_raw.lower()`).
  - **Products (`/masters/products/import`):** Strict dual-uniqueness on `Product Name` (Tally/Standard) and `Product Code` with automatic CBM calculation from `(L x W x H) / 1,000,000`.
  - **Inquiries (`/inquiries/{id}/items/import`):** Matches line-items by Product Code, Product Name, or Tally Name against Product Master; automatically inherits UOM and license flags; updates consignment total CBM and gross weight rollups.
  - **Master Data (`Categories`, `Brands`, `UOM`, `Buyer Types`, `HSN`):** Auto-generates missing code fields (`CAT-XXX`, `BR-XXX`, `BT-XXX`, `UOM-XXX`) from human-readable names and properly maps `Refund VAT %` on HSN imports.

### 11.2. Verification Test Suite & Excel Test Workbooks (`testingimportfile/`)

A dedicated set of 8 pre-built, styled Excel workbooks (`.xlsx`) is maintained in `testingimportfile/` for end-to-end import testing, duplicate conflict validation, and regression assurance across the 4 core business modules:

| Module | New Data File (Clean Import) | Duplicate Data File (Conflict / Skip Verification) | Validation & Deduplication Rules Tested |
| :--- | :--- | :--- | :--- |
| **Supplier Master** | `supplier_new_data.xlsx` | `supplier_duplicate_data.xlsx` | Tests valid Country/State/City hierarchy, phone formats (7-15 digits), existing DB Company Name deduplication (`ConflictException`), and intra-file batch duplicates. |
| **Buyer (Client) Master** | `buyer_new_data.xlsx` | `buyer_duplicate_data.xlsx` | Tests valid Buyer Types, Country/City mappings, Note 66 3-way deduplication across **Company Name**, **Calling Number**, and **WhatsApp Number** ($\ge 6$ clean digits), plus intra-batch collision rejection. |
| **Product Master** | `product_new_data.xlsx` | `product_duplicate_data.xlsx` | Tests Category/Sub-Category parent-child linkage, valid UOM and HSN codes, required packaging dimensions (Gross Weight > 0, Pack. Qty > 0, CBM > 0), and dual-uniqueness on `Product Name` and `Product Code`. |
| **Inquiry Line Items** | `inquiry_items_new_data.xlsx` | `inquiry_items_duplicate_data.xlsx` | Tests consignment line item import matching active Product Master items by SKU/Code or Name, status assignment (`Approved`/`Proposed`), duplicate item line detection, and invalid quantity/unmatched product error reporting. |

### 11.1. Media & File Storage Subsystem (Neon S3, Supabase & Local Disk Fallback)

**Files:** `backend/app/common/storage.py`, `backend/app/core/config.py`, `backend/app/main.py`

- **Tri-Layer Storage Engine:** Provides unified storage abstractions for product images, supplier factory media, and quotation attachments:
  1. **Neon S3 Object Storage (Primary Cloud Storage):** When `AWS_ENDPOINT_URL_S3`, `AWS_ACCESS_KEY_ID`, and `AWS_SECRET_ACCESS_KEY` are provided in `.env`, uploads files directly to Neon S3-compatible public buckets (`product-images`, `supplier-media`, `quotations`) via `boto3` (using path-style addressing `addressing_style: path`), returning direct high-speed CDN/public URLs (`https://<project-storage-host>/<bucket>/<filename>`).
  2. **Supabase Cloud Storage (Secondary Cloud Fallback):** When `SUPABASE_BASE_URL` and `SUPABASE_AUTH_KEY` / `SUPABASE_SERVICE_KEY` are provided in `.env`, uploads files directly to target public buckets via async HTTP (`httpx`), automatically creating the buckets if not present.
  3. **Local Filesystem Fallback:** When running offline or without cloud bucket credentials, `save_uploaded_file` seamlessly saves uploaded files to local disk under `uploads/<local_subfolder>/` (`uploads/products/`, `uploads/suppliers/`, `uploads/quotations/`).
- **Static Mounting:** FastAPI mounts `uploads/` statically at both `/uploads` and `/static/uploads` via `StaticFiles(directory=uploads_dir)` in `app/main.py`, ensuring instant browser access.
- **Filename Sanitization & MIME Resolution:**
  - `sanitize_filename(filename)`: Strips path traversal characters (`..`, `/`, `\`), collapses repetitive delimiters, enforces safe ASCII tokens, and limits base names to 120 characters prefixed with a unique UUID (`{uuid4}_{clean_name}`).
  - `guess_content_type(filename)`: Resolves standard MIME types (`image/jpeg`, `image/png`, `image/webp`, `video/mp4`, `application/pdf`, `.xlsx`, `.csv`).
- **Database Persistence Model:** Database entities (`products.images`, `suppliers.media_urls`) store URL arrays (e.g. `["https://br-odd-tree-aybmdshz.storage.../product-images/xyz.webp"]` or `["/uploads/products/xyz.webp"]`), providing 100% portability across cloud and local storage backends without requiring database schema alterations.

---

## 12. Frontend Architecture & Single-Flight Token Refresh

**Files:** `frontend/src/lib/api.ts`, `frontend/src/lib/authContext.tsx`, `frontend/src/components/AppShell.tsx`

- **Routing:** React Router v6 with `ProtectedRoute` guards and deep-link redirect preservation.
- **Error Boundaries:** Multi-layer error boundary protection with an application-level root boundary in `main.tsx` and a route-keyed boundary (`ErrorBoundary key={location.pathname}`) in `App.tsx` ensuring crashed page states do not leak across navigation transitions.
- **Component Design System:** Predefined accessible UI tokens in `frontend/src/components/ui.tsx` and `fields.tsx` (including interactive `TextField` with automatic password visibility eye toggle `showPasswordToggle`).
- **Universal Inward Dropdown Chevron Styling:** To prevent browser-native chevron overlap and provide clean visual balance, native selects (`select:not([multiple])`) across all modules utilize custom SVG arrows positioned inward (`right: 14px; padding-right: 34px;`), matched by `SelectField`'s animated SVG chevron with dynamic 180° flip transition upon focus/open.
- **Hooks Architecture:** Custom hooks for asynchronous state management: `useAuth`, `usePendingGuard`, `useToast`, `usePagination`.

---

## 13. Complete API Route & Endpoint Directory

| Module | HTTP Method | Endpoint URI | Description | Permission Gate |
| :--- | :--- | :--- | :--- | :--- |
| **Auth** | `POST` | `/api/v1/auth/login` | Authenticate credentials & issue JWT pair | Public |
| **Auth** | `POST` | `/api/v1/auth/refresh` | Rotate single-use refresh token | Public (Valid Token) |
| **Auth** | `POST` | `/api/v1/auth/logout` | Revoke refresh token & active session | Authenticated |
| **Auth** | `GET` | `/api/v1/auth/me` | Fetch profile & effective permissions | Authenticated |
| **Auth** | `GET` | `/api/v1/auth/sessions` | List active user device sessions | Authenticated |
| **Auth** | `DELETE`| `/api/v1/auth/sessions/{id}` | Revoke specific device session | Authenticated |
| **Users** | `GET` | `/api/v1/users` | List paginated users with search/sort | `user.read` |
| **Users** | `GET` | `/api/v1/users/all` | List all users (unpaginated for manager lookups) | `user.read` |
| **Users** | `GET` | `/api/v1/users/department-manager/{role_id}` | Get active manager for a department/role | `user.read` |
| **Users** | `POST` | `/api/v1/users` | Create person record (login user or workforce member via `has_login`) | `user.create` |
| **Users** | `GET` | `/api/v1/users/{id}` | Inspect user details & roles | `user.read` |
| **Users** | `PATCH` | `/api/v1/users/{id}` | Update user profile / reporting manager | `user.update` |
| **Users** | `POST` | `/api/v1/users/{id}/reset-password` | Generate temporary login password | `user.reset_password` |
| **Users** | `POST` | `/api/v1/users/{id}/roles` | Assign Role/Department (with assignment_type, is_primary, effective dates) | `user.action` |
| **Users** | `POST` | `/api/v1/users/{id}/deactivate` | Deactivate a user, terminate all active sessions, and block login | `user.action` |
| **Users** | `POST` | `/api/v1/users/{id}/activate` | Reactivate an inactive user, restoring login ability | `user.action` |
| **Users** | `POST` | `/api/v1/users/{id}/force-logout` | Revoke active sessions, invalidate tokens & push real-time WebSocket disconnect | `user.action` |
| **Users** | `DELETE`| `/api/v1/users/{id}` | Permanently disabled (returns 400 Bad Request to preserve audit integrity) | `user.action` |
| **RBAC** | `GET` | `/api/v1/rbac/roles` | List all Roles / Departments | `roles_permissions.view` |
| **RBAC** | `POST` | `/api/v1/rbac/roles` | Create new Role / Department (with optional `code` and `parent_department_id`) | `roles_permissions.create` |
| **RBAC** | `PATCH` | `/api/v1/rbac/roles/{id}` | Update Role name/description/code/parent (with cycle detection) | `roles_permissions.action` |
| **RBAC** | `DELETE`| `/api/v1/rbac/roles/{id}` | Delete Role (with impact check) | `roles_permissions.action` |
| **RBAC** | `POST` | `/api/v1/rbac/roles/{id}/delete-with-reassignment` | Safe delete with user reassignment | `roles_permissions.action` |
| **RBAC** | `GET` | `/api/v1/rbac/roles/{id}/hierarchy` | Fetch connected parent and child departments | `roles_permissions.view` |
| **RBAC** | `POST` | `/api/v1/rbac/roles/{id}/parents` | Link an additional parent department (with cycle check) | `roles_permissions.action` |
| **RBAC** | `DELETE`| `/api/v1/rbac/roles/{id}/parents/{parent_id}` | Unlink a parent department | `roles_permissions.action` |
| **RBAC** | `POST` | `/api/v1/rbac/roles/{id}/children` | Link an additional child department (with cycle check) | `roles_permissions.action` |
| **RBAC** | `DELETE`| `/api/v1/rbac/roles/{id}/children/{child_id}` | Unlink a child department | `roles_permissions.action` |
| **RBAC** | `GET` | `/api/v1/rbac/permissions` | List all system permission codes | `roles_permissions.view` |
| **RBAC** | `PUT` | `/api/v1/rbac/users/{id}/permissions/bulk` | Save per-user direct permission overrides | `roles_permissions.action` |
| **RBAC** | `GET` | `/api/v1/rbac/users/{id}/effective-permissions` | Compute effective user permissions | `roles_permissions.view` |
| **Positions** | `GET/POST`| `/api/v1/positions` | Manage positions/designations | `position.*` |
| **Positions** | `GET` | `/api/v1/positions/holders-for-user/{user_id}` | List position assignments held by a user | `position.view` |
| **Positions** | `POST/DELETE`| `/api/v1/positions/assignments[/{id}]` | Assign/remove an employee's position assignment | `position.update` |
| **Reporting** | `POST` | `/api/v1/reporting` | Create a reporting relationship (rejects self/circular reporting, 409) | `reporting.manage` |
| **Reporting** | `GET` | `/api/v1/reporting/managers/{user_id}` | List managers for a user | `reporting.view` |
| **Reporting** | `GET` | `/api/v1/reporting/direct-reports/{user_id}` | List direct reports for a user | `reporting.view` |
| **Reporting** | `DELETE`| `/api/v1/reporting/{id}` | Remove a reporting relationship | `reporting.manage` |
| **Reporting** | `POST` | `/api/v1/reporting/reassign-direct-reports/{manager_id}` | Move a manager's active direct reports to someone else | `reporting.manage` |
| **Reporting** | `POST` | `/api/v1/reporting/set-manager/{employee_id}` | Set or move an employee's primary manager (drag-and-drop org chart) | `reporting.manage` |
| **Reporting** | `GET` | `/api/v1/reporting/org-chart` | Dynamic organization chart data (active PRIMARY_REPORTING edges) | `reporting.view` |
| **Masters** | `GET/POST`| `/api/v1/masters/brands` | Manage product brands | `brand.*` |
| **Masters** | `GET/POST`| `/api/v1/masters/categories` | Manage product categories | `category.*` |
| **Masters** | `GET/POST`| `/api/v1/masters/subcategories` | Manage product sub-categories | `subcategory.*` |
| **Masters** | `GET/POST`| `/api/v1/masters/countries` | Manage country records | `country.*` |
| **Masters** | `GET/POST`| `/api/v1/masters/states` | Manage state/province records | `state.*` |
| **Masters** | `GET/POST`| `/api/v1/masters/cities` | Manage city records | `city.*` |
| **Masters** | `GET/POST`| `/api/v1/masters/currencies` | Manage currencies & conversion rates | `currency.*` |
| **Masters** | `GET/POST`| `/api/v1/masters/uom` | Manage units of measurement | `uom.*` |
| **Masters** | `GET/POST`| `/api/v1/masters/hsn` | Manage HSN/SAC customs codes | `hsn.*` |
| **Masters** | `GET/POST`| `/api/v1/masters/company-list` | Manage enterprise company/branch entities | `organizationlist.*` |
| **Masters** | `GET/POST`| `/api/v1/masters/supplier-types` | Manage supplier classification types | `suppliertype.*` |
| **Masters** | `GET/POST`| `/api/v1/masters/buyer-types` | Manage buyer client classification types | `buyertype.*` |
| **Search**  | `GET` | `/api/v1/search` | Universal global topbar search across all modules | Authenticated |
| **Products**| `GET` | `/api/v1/products` | Paginated product catalog | `product.read` |
| **Products**| `POST` | `/api/v1/products` | Create product record | `product.create` |
| **Products**| `PATCH` | `/api/v1/products/{id}` | Update product & technical specs | `product.update` |
| **Products**| `GET` | `/api/v1/products/{id}/datasheet-pdf` | Generate ReportLab PDF datasheet | `product.read` |
| **Suppliers**| `GET` | `/api/v1/suppliers` | List suppliers with multi-column sort | `supplier.read` |
| **Suppliers**| `POST` | `/api/v1/suppliers` | Create supplier record | `supplier.create` |
| **Suppliers**| `PATCH` | `/api/v1/suppliers/{id}` | Update supplier profile & bank details | `supplier.update` |
| **Suppliers**| `POST` | `/api/v1/suppliers/{id}/contacts` | Add contact to supplier directory | `supplier.update` |
| **Suppliers**| `POST` | `/api/v1/suppliers/import` | Bulk import suppliers from spreadsheet | `supplier.import` |
| **Suppliers**| `GET` | `/api/v1/suppliers/export` | Export supplier database | `supplier.export` |
| **Buyers** | `GET` | `/api/v1/buyers` | List buyer clients with status filters | `buyer.read` |
| **Buyers** | `POST` | `/api/v1/buyers` | Create buyer profile | `buyer.create` |
| **Buyers** | `PATCH` | `/api/v1/buyers/{id}` | Update buyer profile & credit limit | `buyer.update` |
| **Buyers** | `POST` | `/api/v1/buyers/{id}/addresses` | Add billing/shipping address | `buyer.update` |
| **Inquiries**| `GET` | `/api/v1/inquiries` | List RFQs with status filtering & financials | `inquiry.read` |
| **Inquiries**| `POST` | `/api/v1/inquiries` | Create new inquiry consignment | `inquiry.create` |
| **Inquiries**| `PATCH` | `/api/v1/inquiries/{id}` | Update inquiry header & status | `inquiry.update` |
| **Inquiries**| `POST` | `/api/v1/inquiries/{id}/items` | Add line item to inquiry | `inquiry.update` |
| **Inquiries**| `POST` | `/api/v1/inquiries/{id}/items/bulk` | Bulk add items to inquiry | `inquiry.update` |
| **Inquiries**| `POST` | `/api/v1/inquiries/{id}/bulk-rfqs` | Dispatch multi-item RFQ emails/WeChat to suppliers | `inquiry.action` |
| **Inquiries**| `POST` | `/api/v1/inquiries/rfq/bulk-dispatch` | Multi-item isolated 1-on-1 email & WeChat RFQ dispatch | `inquiry.action` |
| **Inquiries**| `POST` | `/api/v1/inquiries/messages/send-direct-email` | Direct inline email composer to supplier via SMTP | `inquiry.action` |
| **Inquiries**| `GET`  | `/api/v1/inquiries/{id}/messages` | Fetch chronological two-way communication feed | `inquiry.read` |
| **Inquiries**| `GET`  | `/api/v1/inquiries/wechat/callback` | Tencent WeCom handshake verification | Public (Signature Verified) |
| **Inquiries**| `POST` | `/api/v1/inquiries/wechat/callback` | WeCom webhook handler with AI quotation ingestion | Public (AES Decrypted) |
| **Inquiries**| `POST` | `/api/v1/inquiries/items/{item_id}/rfqs` | Dispatch single-item RFQ email & portal link | `inquiry.action` |
| **Inquiries**| `POST` | `/api/v1/inquiries/items/{item_id}/quotations` | Manually record supplier quotation | `inquiry.update` |
| **Inquiries**| `PATCH` | `/api/v1/inquiries/quotations/{id}` | Edit quotation details (qty, price, currency, terms) | `inquiry.update` |
| **Inquiries**| `PATCH` | `/api/v1/inquiries/quotations/{id}/status` | Approve or reject quotation | `inquiry.approve` |
| **Inquiries**| `DELETE` | `/api/v1/inquiries/quotations/{id}` | Soft-delete quotation & resync KPIs | `inquiry.delete` |
| **Inquiries**| `POST` | `/api/v1/inquiries/inbound-webhook` | Inbound webhook for WeChat/Email auto-ingestion | Public (API / Webhook) |
| **Inquiries**| `GET` | `/api/v1/inquiries/items/{item_id}/quotations` | List quotations with turnaround & lead times | `inquiry.read` |
| **Inquiries**| `GET` | `/api/v1/inquiries/quotations/documents` | Fetch all quotation sheets for Gallery | `inquiry.read` |
| **Inquiries**| `GET` | `/api/v1/inquiries/{id}/export` | Export consignment line items to Excel/CSV | `inquiry.read` |
| **Inquiries**| `POST` | `/api/v1/inquiries/bulk-tally-post` | Bulk mark items as Tally Entry Posted | `inquiry.update` |
| **Public** | `GET` | `/api/v1/public/quotes/{token}` | Fetch RFQ specifications for vendor | Public (Token Validated) |
| **Public** | `POST` | `/api/v1/public/quotes/{token}` | Submit vendor quote bids & lead times | Public (Token Validated) |
| **Public** | `POST` | `/api/v1/public/quotes/{token}/upload` | Upload quotation PDF / datasheet | Public (Token Validated) |
| **Planning**| `GET` | `/api/v1/planning/sheets` | List planning sheets / branches | `planning.read` |
| **Planning**| `POST` | `/api/v1/planning/sheets` | Create planning sheet | `planning.sheet.manage` |
| **Planning**| `GET` | `/api/v1/planning/sheets/{id}/grid` | Fetch dynamic planning matrix | `planning.read` |
| **Planning**| `GET` | `/api/v1/planning/sheets/{id}/filter-values` | Query distinct column filter values & counts | `planning.read` |
| **Planning**| `GET` | `/api/v1/planning/organization-search` | Search items across all branch sheets of an organization | `planning.read` |
| **Planning**| `POST` | `/api/v1/planning/rows` | Add item row to planning sheet | `planning.row.manage` |
| **Planning**| `POST` | `/api/v1/planning/columns` | Add dynamic column to sheet | `planning.column.manage` |
| **Planning**| `PATCH` | `/api/v1/planning/cells` | Update cell value & status color | `planning.cell.edit` |
| **Planning**| `POST` | `/api/v1/planning/container-calc` | Compute container CBM & load capacity | `planning.read` |
| **Audit** | `GET` | `/api/v1/audit` | Query immutable audit change logs | `audit.view` |
| **Trash** | `GET` | `/api/v1/trash` | List soft-deleted records | `trash.view` |
| **Trash** | `POST` | `/api/v1/trash/{entity}/{id}/restore` | One-click restore deleted record | `trash.restore` |
| **Trash** | `DELETE`| `/api/v1/trash/{entity}/{id}/purge` | Permanently purge record | `trash.purge` (Super Admin) |
| **Cache** | `GET` | `/api/v1/cache/stats` | Inspect cache metrics & hit rate | `settings.manage` |
| **Cache** | `DELETE`| `/api/v1/cache/flush` | Flush entire cache | `settings.manage` |
| **Organizations** | `GET/PATCH` | `/api/v1/organizations/profile` | Manage enterprise company profile & logo | `organization.view/manage` |
| **Events** | `WS` | `/api/v1/events/ws` | Real-time WebSocket connection bus | Authenticated |

---

## 14. Developer & AI Integration Guide (Rules of Engagement)

When building new features, modifying endpoints, or merging external components into this ERP:

### 14.1. Adding a New Business Module
1. **Model**: Create `backend/app/<module>/models.py`. Inherit from `Base`, `UUIDPrimaryKeyMixin`, `TimestampMixin`, `SoftDeleteMixin`, and `VersionMixin`.
2. **Schemas**: Define `Create`, `Update`, `Read` schemas in `backend/app/<module>/schemas.py`.
3. **Repository**: Inherit from `BaseRepository[Model]` in `backend/app/<module>/repository.py`.
4. **Service**: Implement business rules and audit recording in `backend/app/<module>/service.py`.
5. **Routes**: Wire endpoints with `Depends(require_permission("<module>.<action>"))` in `backend/app/<module>/routes.py`.
6. **Register Router**: Include the router in `backend/app/api/v1/router.py`.
7. **Migration**: Generate migration via `alembic revision --autogenerate -m "add <module> table"`.
8. **Frontend**: Create `frontend/src/pages/<Module>.tsx` and register route in `frontend/src/lib/nav.ts`.
9. **Living Documentation**: Update `doc/SYSTEM_DOCUMENTATION.md` immediately per [`AGENTS.md`](file:///c:/Users/Inhyma%20Solutions/Downloads/ERP_Main_Claude-main/AGENTS.md).

### 14.2. Antipatterns & Critical Rules
- ❌ **NEVER execute physical deletion (`session.delete(row)`) in standard flows**: Always use soft-delete (`row.deleted_at = utcnow()`).
- ❌ **NEVER bypass permission dependencies**: Every private endpoint must specify `Depends(require_permission(...))`.
- ❌ **NEVER alter database tables manually**: Keep all migrations version-controlled in `backend/alembic/versions/`.
- ❌ **NEVER modify user permissions without invalidating cache**: Always call `cache_manager.invalidate_user_permissions(user_id)`.

### 14.3. Git Pull & Remote Merge Invariant: Universal Bulk Import & Deduplication Engine

Whenever pulling from remote branches or merging collaborative Git branches, the following **Universal Bulk Import & Deduplication Engine** rules represent verified, production-grade logic that must **NEVER** be regressed, deleted, or overwritten:

1. **Buyer (Client) Master Deduplication (`backend/app/buyers/service.py`, `repository.py`)**:
   - **Note 66 3-Way Deduplication**: Incoming rows are checked across `company_name` (case-insensitive trim), `contact_calling_number`, and `contact_whatsapp_number`.
   - **Cross-Phone Protection**: Strips non-digit characters (`re.sub(r"\D", "", phone)`); if length $\ge 6$ digits, checks that a new calling number does not collide with ANY existing calling or WhatsApp number, and vice versa.
   - **Batch Collision Guard**: Tracks `seen_in_batch` set; duplicate company names within the same upload are rejected with `ConflictException`.
   - **Master Links**: Strict validation of `Buyer Type` (mapped to valid enum/master values), `Country`, and `Product Categories`.

2. **Supplier Master Deduplication & Hierarchy Validation (`backend/app/suppliers/service.py`, `validators.py`)**:
   - **Company Uniqueness**: Checks `company_name` against database (`existing_map`) and in-file batch duplicates.
   - **Null-Safe State Resolution**: Validates state by country ID and matches name or code safely: `s.name.lower() == state_raw.lower() or (s.code and s.code.lower() == state_raw.lower())` (prevents `AttributeError` on `None` state codes).
   - **Phone Digits Rule**: Calling, WhatsApp, and WeChat numbers must contain between 7 and 15 digits (including international country code prefix).
   - **City / Province / Country & Category Hierarchy**: Every supplier row must resolve to an existing Country, State, and City in geography masters, and valid Category / Sub-Category links.

3. **Product Master Dual-Uniqueness & Automated Dimensions (`backend/app/masters/products/service.py`, `validators.py`)**:
   - **Dual Uniqueness**: Both `product_name` / `product_name_tally` and `product_code` are strictly unique across active products (`seen_names` and `seen_codes`).
   - **Parent-Child Category Verification**: Sub-category is verified to belong to the chosen category (e.g. `Band sealing Machine` under `Machines`).
   - **Packaging Computations**: Enforces `Pack. Qty > 0`, `Pack. Gross Weight > 0`, and automatically calculates `Pack. Unit CBM = (Length x Width x Height) / 1,000,000` if Length, Width, Height are supplied.

4. **Inquiry Consignment Line Items Import (`backend/app/inquiries/service.py:import_items`)**:
   - **Flexible Product Resolution**: Matches line items by `Product Code`, `Product Name`, or `product_name_tally` against Product Master.
   - **Auto-Inheritance**: Automatically copies `uom_id` and `requires_license` flags from the resolved product; validates positive integer/float quantity.
   - **Rollup Synchronization**: Calling `import_items` automatically invokes `_refresh_rollup` to recalculate total CBM, gross weight, item count, and proposed/approved totals.

5. **Master Data ("Etc" General Masters) Code Auto-Generation**:
   - Across all 12 master modules (Brands, Categories, Sub-Categories, UOM, Buyer Types, Supplier Types, Cities, Countries, States, HSN, Currencies, Company List), if the `Code` column is omitted from import sheets, a unique code slug (`CAT-XXX`, `BR-XXX`, `BT-XXX`, `UOM-XXX`) is automatically synthesized from the title/name.
   - HSN Code validator strips percent signs/commas and correctly casts `Refund VAT %` to `float`.

6. **Standard Verification Workbooks (`testingimportfile/`)**:
   - Maintain the 8 reference Excel files in `testingimportfile/` (`*_new_data.xlsx` and `*_duplicate_data.xlsx`) as the definitive regression test suite. Any code merge touching import files must pass these 8 files with zero regressions.

---

## 15. Deployment, Environment Variables & Operations

### Backend Environment Variables (`backend/.env`)
```env
# Application Settings
APP_NAME=Enterprise ERP
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-super-secret-key-32-chars-minimum
API_V1_PREFIX=/api/v1

# Database Configuration (Neon Serverless PostgreSQL)
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_7HTzR5qPbvmx@ep-old-fire-axzu5kp9-pooler.c-4.us-east-2.aws.neon.tech/yinglima_erp?ssl=require
DATABASE_DISABLE_STATEMENT_CACHE=true

# Database Environment Profiles (Switch via: copy .env.<db_name> .env)
# 1. Yinglima (China):  .env.yinglima_erp -> DATABASE_URL=.../yinglima_erp?ssl=require
# 2. Inhyma (India):    .env.inhyma_erp   -> DATABASE_URL=.../inhyma_erp?ssl=require
# 3. Master / Golden:   .env.erp_main     -> DATABASE_URL=.../erp_main?ssl=require

# CORS Allowed Origins
BACKEND_CORS_ORIGINS=["http://localhost:5173","https://erp.yourdomain.com"]

# JWT Configuration
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Caching Configuration
REDIS_URL=redis://localhost:6379/0

# AI Quotation Extractor API Keys
OPENAI_API_KEY=your-openai-api-key
GEMINI_API_KEY=your-gemini-api-key

# Inbound Email Worker (IMAP)
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
IMAP_USERNAME=quotes@yourdomain.com
IMAP_PASSWORD=your-app-password
# Supabase Storage & Cloud Asset Persistence
SUPABASE_PROJECT_ID=mpvzjzunkiqchhhvxrza
SUPABASE_SERVICE_KEY=your-supabase-service-role-secret-key
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_URL=https://mpvzjzunkiqchhhvxrza.supabase.co
```

### Frontend Environment Variables (`frontend/.env`)
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_BASE_URL=ws://localhost:8000/api/v1/events/ws
```

### Supabase Storage & Media Asset Persistence Architecture
- **Central Storage Engine (`app.common.storage`)**: All file and media uploads (Product Photos, Supplier Visit Photos/Videos, and Inbound Supplier Quotation Sheets/PDFs) utilize a unified async storage engine.
- **Dedicated Public Buckets**:
  - `product-images`: Multi-photo product catalogs and cover images.
  - `supplier-media`: Factory visit photos, videos, and supplier profile attachments.
  - `quotations`: PDF quote sheets and specification attachments extracted from supplier reply emails.
- **Automatic Bucket Provisioning**: The service role secret key automatically provisions public buckets (`public: true`, 50MB per-file ceiling) upon initial upload.
- **Resilient Fallback**: If Supabase credentials are not supplied or the remote service is temporarily unreachable, files safely persist to the backend's local `uploads/` directory with detailed structured warning logs.
- **Sync & Maintenance Utility (`scripts/sync_uploads_to_supabase.py`)**: One-command synchronization tool that scans local disk directories (`uploads/products`, `uploads/suppliers`, `uploads/quotations`), uploads them to Supabase Storage, and updates all existing PostgreSQL database references with global public URLs.

### Inbound & Outbound Email Architecture (Zero Wasted API Costs)
- **Bidirectional Mailbox Polling**: Poller inspects both `INBOX` and `[Gmail]/Sent Mail` to capture supplier replies and salesperson outbound negotiations sent directly via email clients (e.g. Gmail web, Outlook, mobile).
- **Isolated 1-on-1 RFQ Dispatch per Supplier**: When dispatching bulk RFQs ("RFQ for all" or selected items), the system partitions emails per supplier so each vendor receives an isolated, 1-on-1 email with their own company greeting (`Dear [Contact] ([Company])`). Competitor emails are never bundled or exposed in `To:`.
- **Explicit `Reply-To` Routing Header**: All outbound SMTP emails (both single and bulk RFQ) enforce `Reply-To: Yinglima Procurement Team <om1inhyma@gmail.com>`. When vendors click "Reply", responses are guaranteed to route directly to the procurement inbox for automated AI ingestion.
- **Per-Supplier Outbound Timeline Logging**: Individual `InquiryMessage` entries are created per supplier (`supplier_id=sup.id`) rather than bundled flat strings, ensuring accurate supplier-filtered timeline tracking in the Emails tab.
- **Outbound Multi-Recipient Parsing**: Outbound emails parse all addresses from `To` and `Cc` to guarantee matching against all recipient suppliers.
- **Outbound Company Emails**: Emails sent by Yinglima (`om1inhyma@gmail.com`) are strictly tagged as `direction="outbound"`. They are logged into the `Emails` tab timeline with **0 OpenAI API calls** and never create quotation rows.
- **First Valid Supplier Reply & AI Resilience**: The first valid reply from a supplier to our RFQ triggers OpenAI GPT extraction **exactly ONCE**, creating `QT-AUTO-XX`, uploading any quote attachment directly to Supabase Storage, and logging the email in the `Emails` tab. OpenAI API calls incorporate automatic 3-attempt exponential backoff retry for transient network disconnects, and `Message-ID` deduplication caching is deferred until successful processing so dropped requests are cleanly recovered.
- **Missing Quote Self-Healing**: If an inbound message was logged to the Emails timeline but quotation rows were interrupted or pending, the poller identifies that items remain unquoted for that supplier and automatically proceeds with AI extraction rather than discarding the message.
- **Subsequent Follow-ups & Negotiations**: Once `QT-AUTO-XX` exists for `(inquiry_item_id, supplier_id)`, all subsequent negotiation emails, price discussions, and delivery conversations bypass AI extraction (**0 OpenAI API calls**) and are appended directly to the `Emails` timeline.
- **Thread-Aware Item Inheritance**: Short follow-up emails without explicit SKU numbers automatically inherit the product item (`inquiry_item_id`) from the active thread history with that supplier.
- **Smart Hybrid Real-Time & Fallback Sync**: The Inquiries module leverages primary real-time WebSocket push updates (`useLiveModule("inquiries")`) for sub-second zero-latency display of incoming WeChat and parsed email quotes, backed by a gentle 15-second visibility-aware fallback poll that automatically pauses when the browser tab is hidden and instantly refreshes upon window focus to eliminate network congestion and CPU overhead.
### Universal Search & Deep-Linking Architecture (`GET /search?q=`)
- **Global Search Endpoint (`app.search.service`)**: Searches asynchronously across Organization, Users, Suppliers, Buyers, Products, Product Categories & Sub-Categories, Brands, HSN Codes, Geography Masters (Countries, States, Cities), Currencies & UOM, **Inquiries & Consignments** (`ConsignmentCode`, `InquiryItem`), and **Trash** (soft-deleted records across all models via `MODEL_MAP`).
- **Client-Side Deep-Linking (`UniversalSearch.tsx`)**: Clicking a search result carries the matched record's UUID via query parameter (e.g. `/suppliers?id=8973e972-...`, `/buyers?id=...`, `/masters/products?id=...`, `/users?id=...`, `/inquiries?buyerId=...&inquiryId=...`, `/trash?q=...`).
- **Automatic Drawer & Modal Invocation**: Destination pages (`Suppliers.tsx`, `Buyers.tsx`, `Users.tsx`, `masters/Products.tsx`, `Inquiries.tsx`, `Trash.tsx`, and `MasterPage.tsx` for shared masters) detect parameters on mount or route transition and open corresponding views/drawers automatically.

### Collapsible Masters Navigation Sub-Menu Architecture (`lib/nav.ts`, `components/AppShell.tsx`)
- **Top-Level Clean Workspace**: Consolidates 12 lookup and catalog configuration masters (`Cities`, `Provinces/States`, `Countries`, `Currencies`, `UOM`, `HSN Codes`, `Categories`, `Sub Categories`, `Brands`, `Supplier Types`, `Buyer Types`, and `Organization List`) into an expandable/collapsible **`Masters ▾`** accordion menu under `SETTINGS`.
- **Protected Primary Business Modules**: Primary daily operational tools remain directly accessible as top-level sidebar items:
  - `Inquiries` under `SALE`
  - `Product Master` and `Product Gallery` under `INVENTORY`
  - `Suppliers` and `Buyers` under `CONTACT`
- **Smart Auto-Expansion**: The sidebar inspects the active route on mount and navigation; if the user accesses any master page, the `Masters` group automatically expands and highlights the active sub-item.
- **Responsive Collapse Mode**: Fully compatible with the 72px icon-collapsed sidebar state (`sidebarCollapsed`). Clicking the group icon expands the sidebar and group seamlessly.

---
*Maintained and verified for Inhyma Solutions Enterprise ERP. Last updated: September 10, 2026 (Consolidated Collapsible Masters Accordion in Sidebar; Top-level Inquiries, Products, Suppliers & Buyers; Inquiry Lifecycle Tabs & Bulk Actions; zero regression).*
