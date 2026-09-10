# Enterprise ERP — Complete Modules, Features & Testing Specification Manual

> **Document Type:** Master Regression Testing Specification & Feature Catalog  
> **Location:** Root Workspace (`/MODULES_AND_FEATURES_TEST_MANUAL.md`)  
> **Purpose:** Exhaustive reference catalog detailing every single module, page layout, table column, action button, modal window, drawer, form tab, and form field across the entire ERP. Designed for developers, QA testers, and autonomous AI agents to execute manual and automated regression tests before and after code changes.  
> **Strict Policy:** When developing or modifying features, no existing module, form, or field listed in this document may be removed, broken, or regressed.

---

## Table of Contents

1. [Executive Testing Principles & Rules of Engagement](#1-executive-testing-principles--rules-of-engagement)
2. [Master Navigation Sitemap](#2-master-navigation-sitemap)
3. [DASHBOARD Module](#3-dashboard-module)
4. [CONTACT: Suppliers Module](#4-contact-suppliers-module)
5. [CONTACT: Buyers Module](#5-contact-buyers-module)
6. [INVENTORY: Product Master Module](#6-inventory-product-master-module)
7. [INVENTORY: Product Gallery Module](#7-inventory-product-gallery-module)
7.1. [INVENTORY: Product Price Directory Module](#71-inventory-product-price-directory-module)
8. [INVENTORY: Categories Master Module](#8-inventory-categories-master-module)
9. [INVENTORY: Sub Categories Master Module](#9-inventory-sub-categories-master-module)
10. [INVENTORY: Brands Master Module](#10-inventory-brands-master-module)
11. [INVENTORY: Supplier Types Master Module](#11-inventory-supplier-types-master-module)
12. [INVENTORY: Buyer Types Master Module](#12-inventory-buyer-types-master-module)
13. [SALE: Inquiries & Proforma Workflow Module](#13-sale-inquiries--proforma-workflow-module)
14. [PLANNING: Master Shipment Planning Grid Module](#14-planning-master-shipment-planning-grid-module)
15. [USER MANAGEMENT: Users Module](#15-user-management-users-module)
16. [USER MANAGEMENT: Departments & Permissions (RBAC) Module](#16-user-management-departments--permissions-rbac-module)
17. [CONFIGURATIONS: HSN Codes Master Module](#17-configurations-hsn-codes-master-module)
18. [CONFIGURATIONS: Geography Masters (Countries, Provinces, Cities)](#18-configurations-geography-masters-countries-provinces-cities)
19. [CONFIGURATIONS: Currencies Master Module](#19-configurations-currencies-master-module)
20. [CONFIGURATIONS: Units of Measurement (UOM) Master Module](#20-configurations-units-of-measurement-uom-master-module)
21. [CONFIGURATIONS: Organization Settings & Company List](#21-configurations-organization-settings--company-list)
22. [GOVERNANCE: Audit Log Module](#22-governance-audit-log-module)
23. [GOVERNANCE: Trash & Recovery (Recycle Bin) Module](#23-governance-trash--recovery-recycle-bin-module)
24. [USER ACCOUNT: Profile, Security & Active Sessions](#24-user-account-profile-security--active-sessions)
25. [AUTHENTICATION: Login & Session Recovery](#25-authentication-login--session-recovery)
26. [EXTERNAL PORTAL: Public Supplier Quotation Submission Portal](#26-external-portal-public-supplier-quotation-submission-portal)
27. [TOPBAR: Universal Search & Record Deep-Linking](#27-topbar-universal-search--record-deep-linking)
28. [USER MANAGEMENT: Unified Person & Workforce Architecture (Employee-to-User Merge)](#28-user-management-unified-person--workforce-architecture-employee-to-user-merge)
29. [USER MANAGEMENT: Unified Departments & Organizational Units (Department-to-Role Merge)](#29-user-management-unified-departments--organizational-units-department-to-role-merge)
30. [USER MANAGEMENT: Positions Module](#30-user-management-positions-module)
31. [USER MANAGEMENT: Organization Chart Module](#31-user-management-organization-chart-module)
32. [AI Subagent Autonomous Testing Prompt Template](#32-ai-subagent-autonomous-testing-prompt-template)

---

## 1. Executive Testing Principles & Rules of Engagement

1. **Zero Feature Loss Guarantee**: Whenever AI or human engineers add or edit code, this checklist must be tested to ensure existing buttons, fields, validation rules, popovers, and drawers continue to render and function.
2. **Form Completeness**: Every form must retain all specified fields, dropdown data loaders, maskings (e.g. phone country codes), and conditional locks (e.g. 1-way status lock from `New` $\rightarrow$ `Existing`).
3. **Data Integrity**: Soft-deletion must always move records to Trash (`/trash`) and never physically purge rows from active tables.
4. **Optimistic Locking & Concurrency**: Modifying entities must send and check `version` increments to avoid dirty concurrent overwrites.

---

## 2. Master Navigation Sitemap

| Sidebar Section | Navigation Label | Sub-Menu / Type | Route Path | Active Key | Icon Key | Required Permission |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **DASHBOARD** | Dashboard | Direct | `/dashboard` | `dashboard` | `dashboard` | Public Authenticated |
| **CONTACT** | Suppliers | Direct | `/suppliers` | `suppliers` | `factory` | `supplier.view` |
| **CONTACT** | Buyers | Direct | `/buyers` | `buyers` | `shoppingBag` | `buyer.view` |
| **INVENTORY** | Product Master | Direct | `/masters/products` | `masters-products` | `box` | `product.view` |
| **INVENTORY** | Product Prices | Direct | `/inventory/product-prices` | `product-prices` | `coins` | `product.view` |
| **INVENTORY** | Product Gallery | Direct | `/product-gallery` | `product-gallery` | `image` | `productgallery.view` |
| **SALE** | Inquiries | Direct | `/inquiries` | `inquiries` | `fileText` | Public Authenticated / `inquiry.view` |
| **PLANNING** | Shipment Planning | Direct | `/planning` | `planning` | `truck` | `planning.view` |
| **USER MANAGEMENT** | Users | Direct | `/users` | `users` | `user` | `user.view` |
| **USER MANAGEMENT** | Positions | Direct | `/positions` | `positions` | `briefcase` | `position.view` |
| **USER MANAGEMENT** | Departments & Permissions | Direct | `/rbac` | `rbac` | `shield` | `roles_permissions.view` |
| **SETTINGS** | **Masters ▾** | **Accordion Parent** | *(Collapsible)* | `masters-group` | `masters` | Dynamic based on children |
| *SETTINGS / Masters* | Cities | Sub-Item | `/masters/cities` | `masters-cities` | — | `city.view` |
| *SETTINGS / Masters* | Provinces | Sub-Item | `/masters/states` | `masters-states` | — | `state.view` |
| *SETTINGS / Masters* | Countries | Sub-Item | `/masters/countries` | `masters-countries` | — | `country.view` |
| *SETTINGS / Masters* | Currencies | Sub-Item | `/masters/currencies` | `masters-currencies` | — | `currency.view` |
| *SETTINGS / Masters* | Units of Measurement | Sub-Item | `/masters/uom` | `masters-uom` | — | `uom.view` |
| *SETTINGS / Masters* | HSN Codes | Sub-Item | `/masters/hsn` | `masters-hsn` | — | `hsn.view` |
| *SETTINGS / Masters* | Categories | Sub-Item | `/masters/categories` | `masters-categories` | — | `category.view` |
| *SETTINGS / Masters* | Sub Categories | Sub-Item | `/masters/subcategories` | `masters-subcategories` | — | `subcategory.view` |
| *SETTINGS / Masters* | Brands | Sub-Item | `/masters/brands` | `masters-brands` | — | `brand.view` |
| *SETTINGS / Masters* | Supplier Types | Sub-Item | `/masters/supplier-types` | `masters-supplier-types` | — | `suppliertype.view` |
| *SETTINGS / Masters* | Buyer Types | Sub-Item | `/masters/buyer-types` | `masters-buyer-types` | — | `buyertype.view` |
| *SETTINGS / Masters* | Organization List | Sub-Item | `/masters/company-list` | `masters-company-list` | — | `organizationlist.view` |
| **SETTINGS** | Organization Settings | Direct | `/organization` | `organization` | `settings` | `organization.manage` |
| **SETTINGS** | Audit Log | Direct | `/audit` | `audit` | `clock` | `audit.view` |
| **SETTINGS** | Trash | Direct | `/trash` | `trash` | `trash` | `trash.view` |

### Sidebar Accordion Navigation Test Checklist
- [ ] Verify `Masters ▾` renders in the `SETTINGS` group with a right-chevron `>` and person-plus icon.
- [ ] Verify clicking `Masters` smoothly expands all 12 nested master links, rotating chevron to `∨`.
- [ ] Verify clicking on any master sub-item (e.g., `Cities`) routes correctly and renders that master page.
- [ ] Verify active master sub-item displays highlighted background (`#e0edff`) and bold `#0061f2` text.
- [ ] Verify the parent `Masters` item retains `.active-parent` blue styling while any child is active.
- [ ] Verify reloading the page or deep-linking to any master page (e.g., `/masters/hsn`) automatically keeps `Masters` expanded on load.
- [ ] Verify collapsing the entire sidebar via `≡` hides sub-items cleanly and uncollapses when `Masters` icon is clicked.
- [ ] Verify `Product Master`, `Product Gallery`, `Suppliers`, `Buyers`, and `Inquiries` remain directly visible as primary top-level menu items.


---

## 3. DASHBOARD Module

- **Route:** `/dashboard`
- **Purpose:** Primary landing screen upon successful login.

### Visual Elements & Layout
1. **Top Greeting:** `Welcome To {User Full Name / Username}` (e.g. `Welcome To Rupesh Malla` or `Welcome To Admin`).
2. **Top Navigation Bar:**
   - Universal Global Search Input: `Search entire ERP (e.g. company, users, products...)`
   - Notification Bell Icon (`🔔`)
   - User Profile Badge with initials (e.g. `AD Admin ⌵`) displaying dropdown with:
     - 👤 **My Profile** (`/profile`)
     - ⚙️ **Organization Settings** (`/organization`)
     - 🚪 **Logout** (`POST /api/v1/auth/logout` $\rightarrow$ redirects to `/login`)

### Test Cases
- [ ] Verify logging in redirects directly to `/dashboard`.
- [ ] Verify the user's name is dynamically extracted from `authContext` and displayed in the heading.
- [ ] Verify clicking the profile menu and selecting "My Profile" navigates to `/profile`.
- [ ] Verify clicking "Logout" clears session tokens and redirects to `/login`.

---

## 4. CONTACT: Suppliers Module

- **Route:** `/suppliers`
- **Purpose:** Comprehensive vendor directory, sourcing management, factory visit logs, and public quote token dispatching.

### 4.1. Screen Layout & Header Actions
1. **Breadcrumb:** `Dashboard / Supplier Profiles`
2. **Page Title & Subtitle:** `Supplier Profiles — Supplier directory, contacts, product categories, and sourcing status.`
3. **Top Action Buttons:**
   - 🔍 **Filter Button (Funnel Icon):** Toggles advanced filter drawer.
   - ⚡ **`+ QUICK ADD` Button:** Opens lightweight creation modal.
   - ➕ **`+ ADD NEW` Button:** Opens full multi-tab supplier profile creation modal.
   - 📥 **`Imp / Exp ⌵` Dropdown:**
     - `Import Excel / CSV` (opens Import Wizard)
     - `Download Sample Template` (downloads `suppliers_sample.csv`)
     - `Export Filtered Data` (downloads `.csv` of current query)
   - ⚡ **`Bulk Actions ⌵` Dropdown:**
     - `Activate Selected`
     - `Deactivate Selected`
     - `Delete Selected` (soft-deletes selected rows with confirmation prompt)
4. **Tabs:**
   - **Active Tab:** Displays active vendors (`is_active = true`).
   - **Inactive Tab:** Displays deactivated vendors (`is_active = false`).
5. **Toolbar Row:**
   - **Items/Page Dropdown:** `10`, `25`, `50`, `100`, `250`.
   - **📌 Freeze Columns Button:** Opens column pin popover menu (Left / Right / Unpin).
   - **Search Input:** `Search company, country, contact, city, phone...` (live debounced search with `✕` clear button, and numeric Sr. No. jump support).

### 4.2. Suppliers Table Columns
1. **Checkbox Column:** Select all / select individual rows.
2. **SR. NO.:** Sequential row index with sorting indicator.
3. **COMPANY NAME:** Clickable company title opening the Detail Side Drawer.
4. **PRODUCT CATEGORY:** Category badge with `+N` expander popover.
5. **KEY STRENGTH SUB-CATEGORY:** Sub-category badges with popover.
6. **PRODUCTS SUPPLIED:** Linked product names with popover.
7. **SECONDARY PRODUCTS:** Truncated text cell with view popover.
8. **COUNTRY:** Country name.
9. **STATE / PROVINCE:** Province / State name.
10. **CITY:** City name.
11. **SUPPLIER TYPE:** Manufacturer, Trader, Wholesaler, Agent badge.
12. **CURRENT STATUS:** `New` / `Existing` status badge (inline editable if permitted).
13. **SUPPLIER GRADE:** `A` / `B` / `C` / `Premium` (inline editable dropdown).
14. **POTENTIAL:** `Yes` / `No` / `High` / `Medium` (inline editable dropdown).
15. **ACTIONS:**
    - 👁️ **View / Detail Drawer**
    - ✏️ **Edit Supplier**
    - 🔗 **Copy Public Quote Portal Link**
    - 🗑️ **Delete Supplier** (Soft-delete protected if Status is `Existing` or Potential is `Yes`)

---

### 4.3. Suppliers "+ QUICK ADD" Modal
Opens a focused single-screen modal for rapid vendor entry.

#### Fields in Quick Add Form:
| Field Label | Field Name | Type | Options / Source | Mandatory | Default / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Company Name** | `company_name` | Text | — | **YES** | Auto Title-cased; checks real-time duplicate suggestions |
| **Product Category** | `category_ids` | Multi-Select Dropdown | `/masters/product-categories` | No | Searchable multi-panel with checkboxes |
| **Key Strength Sub-Category** | `sub_category_ids` | Multi-Select Dropdown | `/masters/product-sub-categories` | No | Dynamically filtered by chosen Category |
| **Country** | `country_id` | Select Dropdown | `/masters/countries` | **YES** | Defaults to **China** (`+86`) |
| **State / Province** | `state_id` | Select Dropdown | `/masters/states` | **YES** | Scoped to Country; supports custom text typing |
| **City** | `city_id` | Select Dropdown | `/masters/cities` | **YES** | Scoped to State; supports custom text typing |
| **Contact Person Name** | `contact_full_name` | Text | — | No | Primary representative |
| **Designation** | `contact_designation` | Text | — | No | e.g. Sales Manager, CEO |
| **Calling Number** | `contact_calling_number`| Phone with Country Code | Auto country prefix | No | Validates 7–15 digits |
| **WhatsApp Number** | `contact_whatsapp_number`| Phone with Country Code| "Same as Calling" checkbox | No | Auto-copies from Calling Number |
| **WeChat Number** | `contact_wechat_number` | Text | "Same as Calling" checkbox | No | WeChat ID / phone |
| **Email(s)** | `emails` | Tag / Multi-Email Input | — | No | Enter email + press Enter or comma |
| **Supplier Type** | `supplier_type` | Select Dropdown | `/masters/supplier-types` | No | Manufacturer / Trader / etc. |
| **Current Status** | `current_status` | Select Dropdown | `New`, `Existing` | No | Defaults to `New` |

- **Actions:** `Cancel`, `Save Supplier`, `Save & Open Full Profile`.

---

### 4.4. Suppliers "+ ADD NEW" / Full Edit Modal
Multi-tab comprehensive modal for vendor master lifecycle.

#### Tab 1: 👤 First Data Form (Basic Profile)
- **Company Name** (*Required*): Auto title-case + 3-way duplicate detection (Company + Phone + WhatsApp).
- **Brand / Factory Description**: Text Area for capabilities, factory size, machinery.
- **Supplier Type**: Dropdown from Supplier Types Master.
- **Geography Selection**:
  - **Country** (*Required*): Dropdown (loads country dial code).
  - **State / Province** (*Required*): Scoped dropdown + custom input toggle.
  - **City** (*Required*): Scoped dropdown + custom input toggle.
  - **Town / Industrial Zone**: Specific industrial area or town name.
  - **Address**: Detailed factory / office street address.
- **Websites**:
  - **Primary Website**: Validated URL field.
  - **Secondary Website / Alibaba Store**: Validated URL field.
- **Tax Identification**:
  - **Tax ID / GST / Unified Social Credit Code**: Vendor business registration code.
- **Sourcing & Pipeline Metrics**:
  - **Current Status**: `New` vs `Existing` (1-way lock: cannot revert from `Existing` to `New`).
  - **Supplier Grade**: `Grade A`, `Grade B`, `Grade C`, `Premium`.
  - **Potential**: `Yes` vs `No`.
  - **Potential Reason**: Explanatory text area if Potential is selected.
- **Factory / Office Visit Record**:
  - **Visited Factory / Office**: Radio/Select `Yes` / `No`.
  - **Visit Remarks**: Notes from physical plant inspection.
  - **Visit Photos / Media Upload**: Multi-file uploader supporting **Neon S3 Object Storage** (`supplier-media` bucket) with transparent Supabase and local disk fallback (`uploads/suppliers/`) served statically by FastAPI (`/uploads/suppliers/`), complete with preview thumbnails and delete action.
  - **Visit Video URL**: Link to factory inspection video (YouTube, Youku, Cloud Storage).
- **Overall Remarks**: General procurement notes.

#### Tab 2: 📇 Contacts Sub-Panel
Manage complete vendor team directory:
- **`+ Add Contact` Button**: Opens contact sub-form with:
  - **Salutation**: `Mr.`, `Ms.`, `Mrs.`, `Dr.`
  - **Person Name** (*Required*): Full name.
  - **Designation**: Role / title.
  - **Handling Territory**: e.g., North America, India, Europe.
  - **Calling Number**: Phone input with country dial code prefix.
  - **WhatsApp Number**: With "Same as Calling" checkbox.
  - **WeChat ID / Number**: With "Same as Calling" checkbox.
  - **Email Address**: Direct email.
- **Contacts Table**: Lists all contacts with `Primary Contact` badge, `Edit` button, and `Delete` button.

#### Tab 3: 📦 Products & Categories
- **Product Categories**: Multi-select panel.
- **Key Strength Sub-Categories**: Multi-select panel scoped to categories.
- **Products Supplied**: Multi-select product picker.
- **Secondary Products Description**: Text area for custom/ancillary items.

### 4.5. Supplier Detail Side Drawer
- **Header:** Company name, status badge, grade badge, potential badge, and public quote share link.
- **Sections:** Identity, Geography, Contact Persons Grid, Sourcing Status, Factory Visit Photos Gallery, Notes.

### Test Cases
- [ ] Open `/suppliers` and confirm active list loads.
- [ ] Click `+ QUICK ADD`, fill Company Name, Country, State, City and save. Verify record appears in table.
- [ ] Click `+ ADD NEW`, navigate all 3 tabs, upload factory visit photo, add contact person, and save.
- [ ] Test Country Dial Code Auto-Update: Change Country (e.g. China -> India) and verify Calling Number, WhatsApp Number, and WeChat Number dialing codes automatically update (e.g. `+86` -> `+91`) while resetting Province/City dropdowns.
- [ ] Test 1-Way Status Lock: Change status to `Existing`, save, edit again and verify `New` cannot be chosen.
- [ ] Verify soft-delete moves vendor to `/trash`.

---

## 5. CONTACT: Buyers Module

- **Route:** `/buyers`
- **Purpose:** Client/buyer directory, multi-contact management, credit limits, addresses, and inquiry linkage.

### 5.1. Screen Layout & Header Actions
1. **Breadcrumb:** `Dashboard / Buyer (Client) Profiles`
2. **Header Actions:**
   - 🔍 **Filter Button (Funnel Icon):** Advanced filter drawer.
   - ➕ **`+ ADD BUYER` Button:** Opens buyer creation modal.
   - 📥 **`Imp / Exp ⌵` Dropdown:** Import CSV/XLSX, Download Sample Template, Export Filtered CSV.
   - ⚡ **`Bulk Actions ⌵` Dropdown:** Bulk Activate, Bulk Deactivate, Bulk Delete.
3. **Tabs:** `Active` vs `Inactive`.
4. **Toolbar:** Items/Page (`10`, `25`, `50`, `100`, `250`), 📌 Freeze Columns popover, Live Search Input.

### 5.2. Buyers Table Columns
1. **Checkbox:** Select row.
2. **SR. NO.:** Row counter with sort.
3. **COMPANY NAME:** Clickable title opening Buyer Detail Side Drawer.
4. **BUYER TYPE:** Dynamic type badge from Buyer Types master (e.g. End User, Trader, Distributor).
5. **PRODUCT CATEGORIES:** Category badge with `+N` expander popover.
6. **PRODUCT SUB CATEGORIES:** Sub-category badges with popover.
7. **COUNTRY:** Country name.
8. **CITY:** City name.
9. **CURRENT STATUS:** `New` / `Existing` (1-way status lock).
10. **BUYER GRADE:** `A`, `B`, `C`, `Premium`.
11. **POTENTIAL:** `Yes` / `No`.
12. **PRIMARY CONTACT:** Name & Phone.
13. **ACTIONS:** View Drawer (`👁️`), Edit (`✏️`), Delete (`🗑️`).

### 5.3. Buyers "+ ADD BUYER" / Edit Modal
#### Tab 1: 👤 Profile (Basic Info & Pipeline)
- **Company Name** (*Required*): Auto title-cased + duplicate alert checking.
- **Buyer Type**: Dropdown from `/masters/buyer-types`.
- **Product Range & Interest**:
  - **Product Categories**: Searchable multi-select panel.
  - **Product Sub Categories**: Searchable multi-select panel.
  - **Product Range Description**: Text Area for specific machinery or commodity needs.
  - **Currently Buying From**: Competing supplier or region description.
- **Location Details**:
  - **Country** (*Required*): Dropdown selector.
  - **City**: City text/selector.
  - **Address**: Registered billing address.
- **Primary Contact Person**:
  - **Salutation**: `Mr.`, `Ms.`, `Mrs.`, `Dr.`
  - **Contact Person Name**: Full name.
  - **Designation**: Title.
  - **Calling Number**: Phone with country dial code.
  - **WhatsApp Number**: With "Same as Calling" toggle.
  - **Email(s)**: Multi-email tag input.
- **Commercial & Sourcing Attributes**:
  - **Tax ID / GST Number**: Tax registration ID.
  - **Website**: Validated URL.
  - **Current Status**: `New` vs `Existing` (1-way status lock).
  - **Buyer Grade**: `Grade A`, `Grade B`, `Grade C`, `Premium`.
  - **Potential**: `Yes` vs `No`.
  - **Potential Reason**: Explanatory remarks if Potential is active.
  - **Overall Remarks**: General business comments.

#### Tab 2: 📇 Contacts Management
- Multi-contact person manager with full CRUD: Name, Salutation, Designation, Calling Number, WhatsApp Number, Email. Auto-synced with Primary Contact.

### 5.4. Buyers Bulk Import Workspace & 3-Way Duplicate Detection
- **Import View:** Dedicated full-page import workflow modeled on Supplier Import via `Imp / Exp ⌵` -> `Import`.
- **Upload Support:** Drag-and-drop or file selector for `.xlsx`, `.xls`, and `.csv` files (up to 5,000 rows, 8 MB).
- **Template Download:** Instant `📥 Download Sample CSV Template` button generating sample with all 23 business fields matching `doc/buyerclient.txt`.
- **Wizard Modal:** 4-step wizard with auto-matched column headers, fuzzy synonyms, live preview, and chunked uploads.
- **True 3-Way Duplicate Prevention (Note 66 in `buyerclient.txt`):**
  - **In-File Duplicate Check:** Prevents duplicate company names in the same import file.
  - **Company Name Uniqueness:** Strictly enforces case-insensitive uniqueness on `Company Name` against the database even when phone numbers are empty or different.
  - **Phone Collision Detection:** Cross-checks `Calling Number` and `WhatsApp Number` against both phone fields of all existing buyers ($\ge 6$ digits, stripping non-digit characters).
  - **Real-Time Client Warnings:** Inline field warning badges display live while typing in the Add/Edit form, blocking save if any of the three vectors collides.
  - **Safe Self-Update:** `exclude_id` ensures updating an existing buyer does not trigger self-collision.

### Test Cases
- [ ] Create Buyer with Company Name, Country, Calling Number, and save.
- [ ] Attempt to create a second buyer with the same Company Name (even with different or empty phone numbers) and verify duplicate conflict is raised.
- [ ] Attempt to create a buyer with a different Company Name but the same Calling Number or WhatsApp Number as an existing buyer, and verify duplicate conflict is raised with the conflicting buyer's name.
- [ ] Attempt to use an existing buyer's Calling Number as a new buyer's WhatsApp Number, and verify cross-phone duplicate detection blocks it.
- [ ] Edit an existing buyer without changing phone/name, save, and verify `exclude_id` allows save without self-duplicate conflict.
- [ ] Verify deleting a buyer with status `Existing` or potential `Yes` is blocked by protection dialog.
- [ ] Click `Imp / Exp ⌵` -> `Import` to open the dedicated Buyer Import workspace.
- [ ] Download Sample CSV template and verify all 23 headers match `doc/buyerclient.txt`.
- [ ] Upload sample file and verify 3-way duplicate check prevents duplicate company names or phone numbers.
- [ ] Master Data Imports: Download sample CSV from each master module (Brands, Categories, Sub-Categories, Buyer Types, Supplier Types, UOM, HSN, Countries, States, Cities, Currencies, Company List), upload directly, and verify all rows import with 100% success and no header/code mismatches.

---

## 6. INVENTORY: Product Master Module

- **Route:** `/masters/products`
- **Purpose:** Centralized product catalog, dynamic specifications builder, CBM packaging calculations, photo gallery uploader, and ReportLab PDF datasheet generation.

### 6.1. Product Master Table Columns
1. **Checkbox:** Row selector.
2. **SR. NO.:** Sequential number.
3. **IMAGE:** Thumbnail preview with click-to-expand lightbox.
4. **PRODUCT CODE:** Unique SKU / Item code.
5. **PRODUCT NAME (TALLY):** Official internal accounting name.
6. **INVOICE NAME:** Commercial description used on billing documents.
7. **CATEGORY / SUB-CATEGORY:** Hierarchy badges.
8. **BRAND:** Manufacturer brand name.
9. **HSN / SAC:** Customs code with VAT Refund rate indicator.
10. **PRIMARY UOM:** Base unit (e.g. PCS, SET, KG).
11. **PACKAGING CBM:** Calculated volume ($L \times W \times H / 1,000,000$).
12. **STATUS:** `Active` / `Inactive` badge.
13. **ACTIONS:** View Detail Drawer, Edit Product, Download PDF Datasheet, Delete.

### 6.3. Add / Edit Product Form Fields
- **Basic Details:**
  - **Product Code**: Auto-generated or manual SKU.
  - **Product Name (Tally / Internal)** (*Required*): Primary product title.
  - **Product Name (Invoice / Export)**: Commercial description.
  - **Barcode / EAN / UPC**: Barcode number.
- **Classification & Taxonomy:**
  - **Category** (*Required*): Dropdown from `/masters/product-categories`.
  - **Sub-Category**: Dynamically filtered by chosen Category.
  - **Brand**: Dropdown from `/masters/brands`.
  - **HSN Code**: Dropdown from `/masters/hsn` (auto-fills Refund VAT %).
- **Units & Conversions:**
  - **Primary Unit of Measurement (UOM)** (*Required*): Base unit.
  - **Secondary UOM**: Alternative packaging unit.
  - **Conversion Factor**: e.g., $1 \text{ BOX} = 24 \text{ PCS}$.
- **Packaging & Dimensions (CBM Engine):**
  - **Packaging Quantity**: Items per master carton.
  - **Net Weight (kg)** & **Gross Weight (kg)**.
  - **Length (cm)**, **Width (cm)**, **Height (cm)**.
  - **Packaging Unit CBM**: Auto-computed live read-only display ($L \times W \times H / 1,000,000$).
- **Commercial & Regulatory:**
  - **Color** & **Material**.
  - **Standard Purchase Cost** & **Standard Selling Price**.
  - **Minimum Order Quantity (MOQ)** & **Reorder Level**.
  - **Refund VAT %**: Auto-filled from HSN or custom override.
  - **License / Certificate Required**: Checkbox & description for regulatory certifications (e.g. CE, ISO, BIS).
  - **Is Purchasable** (`true`/`false`) & **Is Sellable** (`true`/`false`).
- **Dynamic Technical Specifications Builder:**
  - Key-Value attribute table (e.g. `Voltage: 380V`, `Power: 4.5kW`, `Speed: 120 pcs/min`).
- **Cloud Media & Photo Upload:**
  - Multi-image uploader supporting **Neon S3 Object Storage** (`product-images` bucket) with automatic Supabase and local filesystem fallback (`uploads/products/`) served statically by FastAPI (`/uploads/products/`), ensuring zero broken images even in air-gapped deployments.

### Test Cases
- [ ] Create a product, enter Length: `100`, Width: `50`, Height: `40`. Verify CBM calculates to `0.200000`.
- [ ] Select HSN code with 13% Refund VAT and confirm Refund VAT % field auto-populates with `13`.
- [ ] Click "Download PDF Datasheet" (`GET /api/v1/products/{id}/datasheet-pdf`) and verify ReportLab PDF generates.
- [ ] Open `/masters/products` and verify the table loads under 3 seconds with standard pagination (`Showing 1-50 of 3556`, `Page 1 of 72`) and zero 500 error banners.
- [ ] Navigate through pages (`Next`, `Page 2`, `Page 3`) and verify 50 products render reliably per page.
- [ ] Filter by Category, Sub-Category, or Brand using the toolbar dropdowns; confirm the table updates immediately with matching filtered count.
- [ ] Test Comprehensive Server Search: Search by Product Code (`DAR-01849`), Product Name (`Ink Cup`), Brand Name (`Supreme`), or Category; confirm matching items display instantly without proxy timeout.

---

## 7. INVENTORY: Product Gallery Module

- **Route:** `/product-gallery`
- **Purpose:** Visual media center for browsing all product photos and supplier factory inspection photos/videos.

### Visual Elements & Actions
1. **View Tabs:**
   - 📦 **Product Catalog Media Tab:** Visual card grid of all products with image galleries.
   - 🏭 **Supplier Factory Media Tab:** Visual card grid of vendor factory inspection photos & videos.
2. **Filters & Search:** Category, Sub-Category, Supplier, Country, Status, and Keyword search.
3. **Product Media Card:**
   - Cover Photo thumbnail with total photo count badge (e.g. `🖼️ 6 Photos`).
   - Product Name, SKU code, Category badge, and Primary Supplier name.
   - Action: Click opens **Lightbox Carousel**.
4. **Lightbox Carousel Modal:**
   - High-resolution image preview with Next (`❯`) / Previous (`❮`) navigation.
   - Zoom in / Zoom out controls.
   - 💾 **Download Current Photo** button.
   - 📦 **Download All Media (ZIP / Batch)** button.
   - ✏️ **Quick Edit Product** button (opens side drawer).

---

## 7.1. INVENTORY: Product Price Directory Module

- **Route:** `/inventory/product-prices` (Aliases: `/product-prices`, `/masters/product-prices`)
- **Active Key:** `product-prices`
- **Icon:** `coins`
- **Required Permissions:** `product.view` (read), `product.update` (assign / inline edit), `product.export` (export), `product.import` (import)
- **Purpose:** Procurement and sales pricing catalog showing lowest supplier quote per product, inline price updating, expandable vendor price comparisons, and universal bulk Excel import/export.

### Visual Elements & Actions
1. **Header & Summary:**
   - Heading: `Product Price Directory`
   - Total Counter Badge: `N Products`
   - Action Buttons: `📊 Export Excel`, `📄 Export CSV`, `📥 Bulk Import Prices`, `🔄 Refresh`
2. **Filters & Search Bar:**
   - **Search Catalog Input:** Debounced (300ms) multi-attribute search matching product code, product name, Tally alias, barcode, or vendor company name.
   - **Category Filter Dropdown:** All Categories or specific category filter.
   - **Sub-Category Filter Dropdown:** Dynamic scoping to selected Category.
   - **Brand Filter Dropdown:** All Brands or specific brand filter.
   - **Pricing Status Dropdown:** `All Items`, `Priced Items Only`, `Unpriced Items Only`.
3. **Main Table Columns:**
   - **Sr. No.:** Global 1-indexed running number across pages `((page - 1) * pageSize + idx + 1)`.
   - **Product Name & Code:**
     - Product photo thumbnail.
     - Product Name: Clickable link opening `Product Detail SideDrawer`.
     - Product Code Badge (e.g. `DAR-01758`).
     - Barcode (if present).
   - **Category & Brand:** Category name, Brand name, and UOM code.
   - **Best Price (Quote):**
     - Formatted currency badge (e.g. `¥ 125.00` or `$ 16.50`).
     - **Inline Editing:** Clicking/double-clicking turns badge into an inline number input. Pressing `Enter` or clicking `✓` automatically commits changes via `PATCH /api/v1/inventory/product-prices/{link_id}` with optimistic UI update. `Esc` cancels.
     - Unpriced state: Amber button `+ Add Price` opening the Assign Quote modal.
   - **Primary Supplier:**
     - Lowest-price vendor name.
     - Expandable Accordion Badge: `[ N Suppliers ▾ ]` toggling the comparison sub-table.
     - Unpriced state: `—` with `+ Assign` button.
   - **Actions:**
     - `+ Quote` button (opens quick modal to link another supplier to this product).
     - `Compare ▾` / `Close ▴` toggle button.
4. **Option 1 Expandable Sub-Table Comparison (Accordion & 0ms Hover Pre-Fetching):**
   - **Hover Pre-Fetching Engine:** Moving the cursor over any product table row (`<tr>`), supplier count badge `[ N Suppliers ▾ ]`, `+ Assign`, `+ Quote`, or `Compare ▾` button automatically triggers background pre-fetching (`prefetchProductSuppliers`) 200–300ms before click, caching quote data in React state.
   - **0ms Instant Accordion Toggle:** Clicking `Compare ▾` or `[ N Suppliers ▾ ]` opens immediately (0ms) without waiting for server network latency or showing a loading spinner. If `supplier_count === 0`, it opens in 0ms with zero backend network requests.
   - Sub-table columns:
     - `Supplier Name`: Vendor company name, primary calling number (`📞`), WeChat ID (`💬`), and `BEST` green badge on lowest bidder.
     - `Location`: City, Province, Country.
     - `Quoted Price`: Formatted price, inline editable with click and auto-save!
     - `Currency`: CNY, USD, EUR, INR.
     - `MOQ`: Minimum Order Quantity (e.g. `50 pcs`).
     - `Notes / Terms`: Procurement remarks.
     - `Updated`: Formatted quotation date.
     - `Actions`: `🗑️` Delete quote button with confirmation prompt (optimistically removes row and recalculates best price in 0ms).
   - **Inline Quick-Add Row (`+ Add Another Supplier Quote:`):**
     - Supplier select dropdown + Unit Price input + Currency dropdown + MOQ input + `Save Quote` button.
     - **0ms Optimistic Sub-Table Injection:** Instantly appends the new quote to the sub-table, sorts ASC, updates the main row's best price badge and supplier count in 0ms, clears inputs immediately, and synchronizes with server in the background.
5. **Modal: Assign Supplier & Price Quote (0ms Optimistic UI):**
   - Form fields: Product Info summary banner, **Select Supplier Combobox** (Searchable autocomplete dropdown with instant type-to-filter, circular `✕` quick-clear button to wipe typed text/selection without manual backspacing, keyboard navigation, and auto-label resolution; *Required*), Unit Price (*Required*), Currency, MOQ, Notes/Remarks.
   - **Instant 0ms Optimistic Save:** Submitting valid form immediately closes the modal (0ms), renders a green success toast, updates the main product row (new best price, currency, primary vendor, and incremented supplier count), updates open sub-table quotes in memory, and performs background server sync with graceful rollback on error.
6. **Modal: Bulk Import Product Prices:**
   - Sample template link: `📥 Download Sample Price Template (.xlsx)`.
   - Drag & drop or click-to-browse `.xlsx` file upload.
   - Live import summary box: `✅ Created: N`, `🔄 Updated: N`, `❌ Failed: N`, with detailed error list and row numbers for invalid entries.
7. **Product Detail SideDrawer:**
   - Slides in from right upon clicking product name or code.
   - High-resolution photo, Tally Name, Brand, Category, Sub-Category, HSN Code, UOM, Packaging Quantity, Refund VAT %, Packaging Net/Gross Weight, Dimensions (L x W x H cm), auto-computed Packaging Unit CBM, License Warning banner, and Technical Specifications.

### Test Checklist for Quality Assurance
- [ ] **Table Render**: Verify all 3,500+ products load smoothly under 1.5s with Sr. No., Product Name & Code, Category & Brand, Best Price, Primary Supplier, and Actions.
- [ ] **Search Filter**: Type a product code (e.g. `DAR-01758`) or partial product name &rarr; verify table filters instantly.
- [ ] **Category & Brand Filters**: Select a Category &rarr; verify Sub-Category dropdown auto-scopes &rarr; select a Brand &rarr; verify rows reflect selection.
- [ ] **Pricing Status Filter**: Filter by `Priced Items Only` &rarr; verify only rows with quotes display; filter by `Unpriced Items Only` &rarr; verify rows show `+ Add Price`.
- [ ] **Product Detail Drawer**: Click any product name or code &rarr; verify `SideDrawer` opens with full specs, dimensions, weights, CBM, and photo.
- [ ] **Assign Modal 0ms Optimistic Save**: Click `+ Add Price` or `+ Quote` &rarr; select vendor, enter `125.00`, click Save &rarr; verify modal closes immediately (0ms), price badge and supplier update instantly on the main row without waiting for full catalog reload.
- [ ] **Assign Modal Quick-Clear `✕`**: In the supplier search combobox, type any query or non-existent supplier &rarr; verify `✕` cross button appears inside the input &rarr; click `✕` &rarr; verify text and selection clear instantly, input stays focused, and full supplier list is restored.
- [ ] **Inline Edit Main Row (0ms)**: Click on the price badge `¥ 125.00` &rarr; enter `130.00`, press `Enter` &rarr; verify price badge and sub-table quote update immediately with success banner.
- [ ] **Hover Pre-fetching & Instant Compare**: Hover cursor over a product row or `Compare ▾` button for 200ms &rarr; click `Compare ▾` &rarr; verify sub-table opens in 0ms with zero loading delay or spinner.
- [ ] **Zero Supplier 0ms Open**: Click `Compare ▾` on an unpriced item with 0 suppliers &rarr; verify sub-table opens immediately with empty quotes table and quick-add row with zero backend network requests.
- [ ] **Sub-Table Inline Quick-Add (0ms)**: Select a 2nd supplier, enter `110.00`, click `Save Quote` &rarr; verify sub-table immediately injects the new quote with `BEST` badge, supplier count increases to `2 Suppliers`, and main row best price drops to `¥ 110.00` without waiting for network roundtrip.
- [ ] **Sub-Table Delete Quote (0ms)**: Click `🗑️` on a quote &rarr; confirm prompt &rarr; verify quote removed immediately and best price recalculates in 0ms.
- [ ] **Excel & CSV Export**: Click `📊 Export Excel` and `📄 Export CSV` &rarr; verify downloaded files contain all columns and valid data.
- [ ] **Bulk Import & Template**: Open `Bulk Import Prices` modal &rarr; click `Download Sample Price Template` &rarr; verify `.xlsx` template downloads with headers and examples &rarr; upload file &rarr; verify import summary.

---

## 8. INVENTORY: Categories Master Module

- **Route:** `/masters/categories`
- **Table Columns:** SR. NO., Category Name, Category Code, Description, Status, Actions (Edit, Delete).
- **Add / Edit Form Fields:**
  - **Category Name** (*Required*): Title-cased name.
  - **Category Code**: Unique uppercase code (e.g. `MACH`, `PKG`).
  - **Description**: Text area.
  - **Status**: `Active` / `Inactive`.

---

## 9. INVENTORY: Sub Categories Master Module

- **Route:** `/masters/subcategories`
- **Table Columns:** SR. NO., Sub Category Name, Parent Category Name, Code, Description, Status, Actions.
- **Add / Edit Form Fields:**
  - **Parent Category** (*Required*): Dropdown from Categories Master.
  - **Sub Category Name** (*Required*): Title-cased name.
  - **Sub Category Code**: Unique code.
  - **Description**: Text area.
  - **Status**: `Active` / `Inactive`.

---

## 10. INVENTORY: Brands Master Module

- **Route:** `/masters/brands`
- **Add / Edit Form Fields:** Brand Name (*Required*), Brand Code, Manufacturer / Country Description, Status (`Active`/`Inactive`).

---

## 11. INVENTORY: Supplier Types Master Module

- **Route:** `/masters/supplier-types`
- **Add / Edit Form Fields:** Supplier Type Name (*Required*, e.g. Manufacturer, Trader, OEM, Authorized Distributor), Code, Description, Status.

---

## 12. INVENTORY: Buyer Types Master Module

- **Route:** `/masters/buyer-types`
- **Add / Edit Form Fields:** Buyer Type Name (*Required*, e.g. Wholesaler, Retailer, Direct Importer, Institutional Client), Code, Description, Status.

---

## 13. SALE: Inquiries & Proforma Workflow Module

- **Route:** `/inquiries`
- **Purpose:** End-to-end 3-layer RFQ and Quotation management lifecycle:
  $$\text{Layer 1: Buyer Summary Directory} \longrightarrow \text{Layer 2: Buyer Consignments (FB1, FB2...)} \longrightarrow \text{Layer 3: Inquiry Line Items, RFQs \& Quotation Matrix}$$

### 13.1. Layer 1: Buyer Inquiries Directory
- **Summary Cards / Top KPIs (Interactive Filters):**
  - **Pending RFQs:** Count of items awaiting supplier quotes. Clickable &rarr; sets tab to `Pending`.
  - **Approved Quotes:** Count of line items with approved supplier pricing. Clickable &rarr; sets tab to `Approved`.
  - **Ongoing Inquiries:** Active buyer consignments currently in negotiation. Clickable &rarr; sets tab to `Ongoing`.
  - **Completed Consignments:** Successfully ordered / fulfilled consignments. Clickable &rarr; sets tab to `Completed`.
  - **Total Order Value:** Sum of all active consignment line items. Clickable &rarr; sets tab to `All`.
- **Lifecycle Filter Tabs (Matching Product Master Pattern):**
  - Positioned directly above the company table: `All (N)`, `Pending (N)`, `Ongoing (N)`, `Approved (N)`, `Completed (N)`.
  - Active tab highlighted with blue underline (`2.5px solid #0061f2`) and active text color.
- **Top Actions & Bulk Operations:**
  - 🟢 **`Bulk Actions (N) ▾` Button & Dropdown Menu:**
    - Positioned in the top-right header alongside `+ ADD NEW`.
    - Shows `Select 1 or more items from list first` tooltip if 0 selected.
    - Turns vibrant green (`#10b981`) with active count `(N)` when $\ge 1$ company is selected via checkboxes.
    - **`🗑️ Bulk Delete ({N})`**: Deletes all consignments across selected buyer companies safely into Trash with confirmation prompt.
  - ➕ **`+ ADD NEW` Button:** Opens the `QuickInquiryDrawer`.
- **Buyer Directory Table Columns:**
  1. **Checkbox:** Master select all in header; individual checkboxes per buyer row.
  2. **BUYER COMPANY NAME:** Clickable buyer title drilling down to Layer 2 Consignments.
  3. **CONSIGNMENT CODES:** Tag pills of consignment codes (e.g. `📦 FB1`, `📦 FB2`).
  4. **STATUS BADGE:** `Pending`, `Partial Approved`, `Fully Approved`.
  5. **TOTAL CBM:** Sum of CBM for this company's consignments.
  6. **TOTAL WEIGHT:** Total kilograms.
  7. **UPDATED DATE:** Timestamp of latest update.
  8. **ACTIONS:** `👁️ View`, `✏️ Edit`, `🗑️ Delete`.
- **Top Actions Details:**
  - ⚡ **`+ Quick Add Inquiry` Drawer:**
    - **Buyer Company** (*Required*): Searchable dropdown from `/buyers`.
    - **Consignment Code** (*Required*): Dropdown of existing codes or type new (e.g. `FB1`). Automatically cross-references existing codes to reuse matching IDs and prevent `HTTP 409 Conflict` errors.
    - **Inline Error Alert Banner**: Displays red contextual alert banner inside the drawer for immediate feedback on validation failures or conflict warnings.
    - **Non-Destructive Item Editing**: When modifying an existing consignment, updates existing items in-place via `PATCH /{inquiry_id}/items/{item_id}` and appends new rows via `POST /items/bulk`, safely preserving existing quotation records, RFQs, and WeChat/Email chat histories.
    - **Product Item** (*Required*): Type-ahead search with Product Code + Name + Category from Product Master.
    - **Quantity** (*Required*): Number input.
    - **Target Price**: Buyer's budgeted price.
    - **Brand Preference**: Preferred manufacturer/brand.
    - **Product Specs Remarks**: Custom technical or packaging requirements.
    - **Action Buttons:** `Cancel`, `Save Item`, `Save & Add Another Item`.
  - ➕ **`+ Add Item` Modal:**
    - **Buyer Company**: Scoped to current buyer context.
    - **Consignment Code** (*Required*): Scoped strictly to the selected buyer.
    - **Product Name** (*Required*): Auto-resolves and displays dynamic Unit of Measurement (e.g. `PCS`, `SET`, `KG`, `METER`) next to the Quantity input label.
    - **Quantity** (*Required*): Number input (> 0).
    - **Brand Preference & Remarks**: Optional text fields.
    - **Status**: `Proposed` or `Approved`.
  - ➕ **`+ New Consignment` Modal:**
    - **Buyer Company** (*Required*): Select buyer.
    - **Consignment Code** (*Required*): e.g. `FB1`, `FB2`, `MUM-2026-AUG`.
    - **Target Delivery Date**: Date picker.
    - **Consignment Remarks / Notes**: Text area.

---

### 13.2. Layer 2: Consignments View (Inside a Buyer)
- **Top Header & Navigation:**
  - `← All Companies` breadcrumb back button.
  - Heading: `{Buyer Company Name} — Consignments`.
  - 🟢 **`Bulk Actions (N) ▾` Button:** Top-right action bar beside `+ Add Inquiry Item`.
    - Active when $\ge 1$ consignment checkbox is selected.
    - **`🗑️ Bulk Delete ({N})`**: Deletes selected consignments and child items safely into Trash with confirmation prompt.
  - ➕ **`+ Add Inquiry Item` Button:** Opens `AddItemModal`.
- **Lifecycle Filter Tabs & Search Bar:**
  - Tabs: `All (N)`, `Proposed (N)`, `Partial Approved (N)`, `Fully Approved (N)`.
  - Live search input: `Search consignment code…`.
- **Consignments Table Columns:**
  1. **Checkbox:** Master select-all checkbox in `th`; row checkbox in each `td`.
  2. **CONSIGNMENT CODE:** Clickable title (e.g. `FB1`, `FB2`) drilling down to Layer 3 Line Items.
  3. **STATUS:** `badge-gray` (Proposed), `badge-yellow` (Partial Approved), `badge-green` (Fully Approved).
  4. **TOTAL CBM:** Sum of CBM.
  5. **TOTAL WEIGHT:** Sum of weight (kg).
  6. **UPDATED:** Date of latest update.
  7. **ACTION:** `View` (drills into Layer 3), `Delete` (moves to Trash).

---

### 13.3. Layer 3: Inquiry Line Items, RFQs & Quotation Matrix
- **Top Navigation:**
  - `← Back to Consignments` button.
  - Breadcrumb: `Inquiries / {Buyer Name} / {Consignment Code}`.
- **Toolbar Actions:**
  - ➕ **`+ Add Line Item` Button & Modal:**
    - Product picker (loads SKU, image, category), Quantity, Primary UOM, Target Price, Brand Preference, Remarks.
  - ➕ **`+ Add Line Item` Button & Modal:**
    - Product picker (loads SKU, image, category), Quantity, Primary UOM, Target Price, Brand Preference, Remarks.
  - 🔄 **`Imp / Exp ▾` Button & Dropdown Menu (Unified Import/Export):**
    - **UI Placement**: Top-right action bar in Layer 3 beside `← Back` and `+ Add Item`.
    - **Dropdown Options**:
      - 📄 **SAMPLE FILE**: Downloads standardized sample CSV (`Sample_Inquiry_Items_Template.csv`) pre-populated with realistic machine/spare part data.
      - 📥 **IMPORT**: Navigates to the dedicated `Import Inquiry Products` full-page interface.
      - 📤 **EXPORT**: Exports all consignment line items to Excel (`.xlsx`) with enriched quotation metrics, UOM, and statuses.
  - 📥 **`Import Inquiry Products` Dedicated Page & Column Mapping Wizard:**
    - **Page Layout**:
      - Breadcrumb: `Inquiries > {Buyer Name} > #{Consignment Code} > Import Products`.
      - Header with `← BACK` navigation button.
      - Drag-and-drop file selector supporting `.csv`, `.xlsx`, and `.xls` (Max 8 MB, up to 5,000 rows).
      - `📥 Download Sample CSV Template` button.
      - **Validation Guidelines & Notes Card**: Explains mandatory fields (`Product Name` or `Product Code`, `Quantity`), positive quantity requirement, auto-assigned UOM from Product Master, automated license flagging in red, and status defaulting to `Proposed`.
      - Action buttons: `Cancel` and `Import`.
    - **Interactive Column Mapping Modal (`WizardModal`)**:
      - Client-side pre-parsing via SheetJS / PapaParse.
      - Dynamic synonyms matching (e.g. `Item Name` $\rightarrow$ `Product Name`, `Qty` $\rightarrow$ `Quantity`, `SKU` $\rightarrow$ `Product Code`) with green `MATCHED` badges.
      - First 5 rows live preview table for visual verification.
      - Progressive chunked upload to `POST /api/v1/inquiries/{inquiry_id}/items/import`.
    - **Results Summary Panel**:
      - Displays total rows, created count, failed count, and row-by-row error diagnostics with exact spreadsheet row numbers.
      - Automatically recomputes consignment rollups (Total CBM, Weight, Status) and updates the workspace in real-time.
  - ⚡ **`+ Bulk Add Items` Button & Modal:**
    - Multi-row product picker from Product Master with live search. Check multiple products and enter quantities simultaneously.
  - 📤 **`Dispatch Bulk RFQs` Button & Modal:**
    - **Select Suppliers**: Multi-select supplier picker filtered by relevant product categories or all suppliers.
    - **Isolated 1-on-1 Supplier Dispatch**: The backend partitions recipients per supplier so each vendor receives an isolated, private email. Competitor email addresses are never bundled or exposed in `To:`.
    - **Guaranteed `Reply-To` Header**: Enforces `Reply-To: Yinglima Procurement Team <om1inhyma@gmail.com>` on all outbound emails, ensuring supplier replies route cleanly back to the automated AI ingestion inbox.
    - **Per-Supplier Timeline Logging**: Logs separate outbound `InquiryMessage` timeline entries for each recipient supplier (`supplier_id = sup.id`).
    - **Dispatch Channels**: Select `Email (IMAP/SMTP)` and/or `Tencent WeCom / WeChat`.
    - **RFQ Custom Subject & Message**: Pre-filled template with line item details and specifications.
    - **Expected Due Date**: Quotation submission deadline.
    - **Auto Token Generator**: Generates unique public quote tokens (`/quote/:token`) for each supplier.
  - 📊 **`Quotation Matrix Comparison` Button & Modal:**
    - Displays all received supplier quotes side-by-side per line item.
    - **Columns**: Supplier Name, Unit Price, Currency, Lead Time (Days), MOQ, Payment Terms, Incoterms (FOB/CIF/EXW), Total Calculated Cost.
    - **Highlights**: 🟢 **Lowest Unit Price** (green badge), 🟡 **Fastest Lead Time** (yellow badge).
    - **Decision Actions**:
      - `✔ Approve Quote`: Marks quote as `Approved`, sets line item status to `Approved`, updates consignment KPI.
      - `✖ Reject Quote`: Marks quote as `Rejected`.
  - ➕ **`+ Add Manual Quote` Button & Modal:**
    - Supplier picker, Unit Price, Currency (`USD`, `CNY`, `INR`, `EUR`), Lead Time (Days), MOQ, Incoterms, Payment Terms, Quotation Sheet Upload to **Supabase Storage**.
  - 🖼️ **`Quote Documents Gallery` Side Drawer:**
    - Displays all vendor PDF quotation sheets, Excel specs, and technical drawings.
    - In-drawer preview, zoom, and direct download links.
  - 💬 **`Two-Way Communication Timeline & Interactive Email Composer` (Emails Tab):**
    - Chronological feed of all inbound/outbound emails and WeChat messages for this consignment / product.
    - **Supplier Thread Filter & Company Resolution**: Dropdown automatically maps recipient/sender email addresses to their official supplier company names (e.g. mapping `om2inhyma@gmail.com` -> `Yinglima Packaging Machinery Co., Ltd.`), deduplicates suppliers so company names and emails are never split, and cleanly isolates communication threads per vendor.
    - **Accurate AI Auto-Extraction & Discussion Badges**:
      - **Initial Quotation Reply**: On the first incoming quotation message from a supplier for an item, AI extracts commercial pricing and terms, creating `QT-AUTO-XX` in the Quotation Matrix. Displays: `✨ Auto-Parsed with AI & Recorded in Quotation Matrix (QT-AUTO-XX • $Price)`.
      - **Subsequent Sales / Negotiation Chatter**: Once the initial quote exists, subsequent conversations between the sales team and supplier (discounts, delivery questions, terms) bypass AI extraction completely (0 OpenAI tokens). Displays: `💬 Inbound Discussion / Negotiation Thread` (or `💬 Supplier WeChat Discussion`).
      - **Multi-Product RFQ Routing**: When an RFQ contains multiple products (e.g. Band Sealer & Ink Roll), the inbound worker checks message bodies first to ensure quotes for secondary items route to their respective line items without colliding or being blocked by the first item's quote.
      - **Multi-Supplier & Cross-Consignment Isolation**: Supplier A, B, and C replies remain strictly isolated side-by-side in the Quotation Matrix, and quotes for identical products in different consignments (e.g. FB1 vs INH1) never cross-leak.
      - **WeCom / WeChat Intelligent Inbound Matching**:
        - **Consignment Code Detection**: Auto-detects tagged tags like `[#YG7]`, `#YG7`, or `YG7` in message text.
        - **Product Code Auto-Resolution**: When a supplier replies without quoting the consignment tag, the webhook auto-matches line items via product codes present in the reply (e.g. `#DAR-01849` -> automatically matches the inquiry containing that item).
        - **Outbound Recipient Correlation**: If neither code is explicitly typed, matches the reply to the most recent outbound RFQ sent to the supplier's WeCom UserID / mobile number.
        - **Supplier Signature Matching**: Auto-maps the supplier entity if the company name appears in the message signature (e.g. *Wenzhou Brother Machinery Co., Ltd.*).
        - **Instant AI Quotation Parsing**: Automatically generates `QT-AUTO-XX` with unit price, currency, quantity, and payment/delivery terms, and logs the discussion in the WeChat Messages timeline.
    - **Interactive Inline Email Composer (Gmail/Figma-Style)**:
      - Embedded directly at the bottom of the Email timeline.
      - **"To:" Recipient Field**: Quick dropdown of suppliers or free-text comma-separated email entry.
      - **"Subject:" Field**: Auto-prefilled with context tag `Re: [#ConsignmentCode] ProductName (#SKU) - Inquiry Follow-up`.
      - **"Message Body" Textarea**: Clean, spacious multiline composer for typing replies/messages.
      - **"📎 Attach File"**: Supabase Storage file/PDF uploader.
      - **Action Toolbar**: Primary blue **`✈️ Send Email`** button with async SMTP dispatch + Discard button.
    - **Smart Hybrid Real-Time & Fallback Sync**: Primary live updates arrive instantly via WebSocket (sub-second zero-latency display), backed by a gentle 15-second visibility-aware fallback poll that automatically pauses when the browser tab is hidden and refreshes immediately upon window focus to eliminate network congestion and CPU overhead.
  - 📋 **`Bulk Tally Entry Post` Button:** Select multiple line items and mark them as `Tally Entry Posted` in one batch operation.
- **Line Items Table Columns:**
  1. **Checkbox:** Select row for bulk RFQ dispatch or bulk Tally posting.
  2. **SR. NO.:** Sequential item index.
  3. **PRODUCT DETAILS:** Thumbnail photo + SKU code + Product Title + Category badge.
  4. **QUANTITY & UOM:** e.g. `500 PCS`, `24 SETS`.
  5. **TARGET PRICE:** Buyer's budget.
  6. **BRAND PREFERENCE:** Preferred brand name.
  7. **SPECIFICATIONS / REMARKS:** Popover with full technical notes.
  8. **RECEIVED QUOTES BADGE:** e.g. `3 Quotes` (Click opens Quotation Matrix modal directly).
  9. **TALLY STATUS:** Clickable toggle badge (`Tally Posted` in green vs `Pending Tally` in gray).
  10. **ACTIONS:** `Edit Item`, `Delete Item`, `Dispatch Single RFQ`, `Add Manual Quote`.

### Test Cases for Inquiries Module
- [ ] In Layer 1, click `+ Quick Add Inquiry`, select Buyer, enter Consignment `FB1`, pick Product, enter Quantity `100`, save. Verify item is created.
- [ ] Drill down to Layer 2 and Layer 3, click `Dispatch Bulk RFQs`, select 2 suppliers, dispatch. Verify RFQ records are generated with public tokens, verify each supplier receives an isolated 1-on-1 email without competitor emails in `To:`, and verify distinct `InquiryMessage` entries are created per supplier.
- [ ] In the RFQ dispatch drawer, when selecting the WeChat channel, verify the backend validates Tencent's response code (`errcode: 0` vs rejection). Verify the service resolves both Chinese (`+86`) and Indian (`+91`) mobile numbers, as well as direct WeCom UserIDs.
- [ ] Send an RFQ to a supplier, simulate/receive an email reply containing a unit price with spaces in the consignment code (e.g. `[SEA 1]`) and product codes (e.g. `#FNB-02391`), and verify that `email_inbound_worker` accurately maps to the matching consignment line item, extracts the quote via OpenAI, populates `quantity`, and generates a quotation row in the Quotations tab.
- [ ] Simulate or receive an incoming WeChat reply from a supplier; verify `/api/v1/inquiries/wechat/callback` parses the reply, extracts unit price and terms via AI, and automatically creates or updates the quotation row with real-time WebSocket broadcast.
- [ ] Switch to the **Emails** tab in Layer 3, verify the timeline displays historical RFQs and replies.
- [ ] In the **Inline Email Composer** at the bottom of the Emails tab, select a supplier from the dropdown, type a message body, and click `✈️ Send Email`. Verify the email is dispatched via SMTP and instantly appears in the conversation thread with the `Outbound Email ↗` badge.
- [ ] Switch to the **WeChat Messages** tab in Layer 3, verify the timeline displays all incoming and outgoing WeChat messages with timestamps and badges (`WeChat Inbound ↙` vs `Outbound WeChat ↗`).
- [ ] In the **WeChat Direct Reply Composer** at the bottom of the WeChat tab, verify the `To:` field auto-populates with the supplier's WeChat contact (e.g. `ChenXianNing` or `13736331731`), or select a supplier from the dropdown.
- [ ] Click a quick negotiation prompt pill (e.g. `+ Can you offer a discount for bulk quantity?`), type any additional instructions in the text area, and click `Send to WeChat 💬`. Verify the message is dispatched live to the supplier's WeCom/WeChat mobile app via Tencent API, a green success alert displays, and the reply immediately appears in the timeline with the `Outbound WeChat ↗` badge and the salesperson's name.
- [ ] Open Public Quote Portal (`/quote/:token`) for a supplier, submit unit price `¥4500` with PDF quote sheet upload.
- [ ] Return to Layer 3 Items view, verify Received Quotes badge updates to `1 Quote`.
- [ ] Open Quotation Matrix Comparison modal, verify Lowest Price is highlighted in green, click `Approve Quote`, verify status turns to `Approved`.
- [ ] Click Tally Status toggle badge on a line item, verify it toggles between `Pending Tally` and `Tally Posted` instantly.
- [ ] In Layer 3 Items view, click the **Export** button on the top-right toolbar. Select **Excel Spreadsheet (XLSX)** from the dropdown. Verify browser downloads `Inquiry_{Code}_{Date}.xlsx`. Open the file and verify columns (`Sr No`, `Product Code`, `Product Name`, `Quantity`, `UOM`, `Best Quote Price`, `Selected Supplier`, etc.) match active items.
- [ ] In Layer 3 Items view, click the **Export** button and select **CSV Delimited (CSV)**. Verify browser downloads `Inquiry_{Code}_{Date}.csv` and file opens cleanly in Excel without character encoding issues.
- [ ] Open a consignment with 0 items. Verify the **Export** button is disabled with tooltip `"No items to export"`.

---

## 14. PLANNING: Master Shipment Planning Grid Module

- **Route:** `/planning`
- **Purpose:** Interactive spreadsheet-like shipment planning workbook for branch logistics, dynamic column configuration, container CBM optimization, and audit logging.

### 14.1. Workbook Features & Sheet Architecture
1. **Branch Sheet Tabs:**
   - Multi-tab navigation across enterprise branches (e.g. `Mum Branch`, `MP Branch`, `GJ Branch`, `CN Central`).
   - ➕ **`+ Add New Sheet` Button & Modal:**
     - **Sheet Name** (*Required*): e.g. `TN Branch`.
     - **Associated Branch / Organization**: Dropdown selector.
     - **Group Label Prefix** (*Required*): e.g. `Mum`, `TN`, `CN` (customizes all column group numbering and headers for this sheet).
   - **Sheet Actions Menu:** `Rename Sheet`, `Duplicate Sheet`, `Delete Sheet`.

2. **Top Grid Toolbar Actions:**
   - 🔍 **Organization-Wide Cross-Branch Search Bar:** Dynamic top search bar with animated SVG search icon, live branch scan across all sheets of the active organization (e.g. `Inhyma Mumbai`, `Inhyma Ahmedabad`, `Inhyma Indore`), match count pills, item previews, and instant one-click branch switching.
   - 🔍 **Grid Search Input:** Live cell search highlighting matching cells across all rows and columns.
   - 🎚️ **Density Toggle:** `Compact` (high-density ERP spreadsheet) vs `Comfortable`.
   - ➕ **`+ Add Row` Button & Modal:**
     - Select Product from Product Master (auto-fills Category, Sub-Category, UOM, and CBM specs).
     - Enter Initial Target Quantity.
   - ➕ **`+ Add Column` Button & Modal:**
     - **Column Header Title** (*Required*): e.g. `Mum 1`, `Mum 1 Remarks`, `Supplier Name`, `Inspection Date`.
     - **Data Type**: `TEXT`, `NUMBER`, `DATE`, `BOOLEAN_YN` (Yes/No toggle).
     - **Source Type**:
       - `MANUAL`: Free data input by planning officers.
       - `LINKED_LOOKUP`: Pulls dynamic attributes from Product Master, Supplier Master, or Buyer Master.
       - `AGGREGATE`: Live calculation (`SUM`, `AVG`, `MIN`, `MAX`, `COUNT`) of selected column ranges.
       - `FORMULA_CALCULATION`: Custom mathematical formula (e.g. `[Qty] * [Unit CBM]`).
     - **Default Width (px)**: Resizable width stored server-side.
   - 📌 **`Freeze & Hide Columns` Manager Drawer:**
     - List of all sheet columns with visibility checkboxes.
     - Left-pin, Right-pin, and Unpin controls with persistent localStorage caching.
   - 📜 **`Audit History & Change Log` Side Drawer:**
     - Immutable trail recording every single cell edit, column creation/deletion, and row mutation with Timestamp, User Initials, Old Value, and New Value.
   - 📦 **`Container Optimization & CBM Calculator` Button & Modal:**
     - Opens container load calculation panel.
   - 📥 **`Import / Export Workbook`:**
     - `Export to Excel (.xlsx)` with complete cell styling and formulas.
     - `Import from Excel (.xlsx)` with column mapping.

3. **Dynamic Spreadsheet Grid Layout:**
   - **Row Grouping:** Automatically groups line items by Product Sub-Category with collapsible group summary rows showing sub-total quantities and total volume.
   - **Column Drag-and-Drop Resizing:** Grab column border to resize; persisted to database via `PlanningColumn.width_px`.
   - **Column Groups & Cascading Logic:**
     - Group-numbered series (e.g. `Mum 1`, `Mum 1 Remarks`, `NO. OF PKG MUM1`, `TOTAL WEIGHT MUM1`, `TOTAL CBM MUM1`).
     - Deleting or hiding a group column cascades cleanly to all related package, weight, and remark group columns.
   - **Special `Approval Date` Column:**
      - Interactive eye icon (`👁️`) on each cell displaying full chronological history of who approved the date and when.
    - **Excel-Style Column Header Filtering & Live Server Search:**
      - Filter funnel icon (`Y`) on every column header (including `ITEM`, `TEST(Y/N)`, `APPROVAL DATE`, and dynamic columns).
      - **Live Filter Popover**: Queries `/api/v1/planning/sheets/{id}/filter-values` across the entire sheet dataset (1384+ items) rather than only the currently loaded browser page.
      - **Instant Search Box**: Real-time debounced text search inside the popover dynamically matches and returns items from the whole database, even for unrendered or newly added Product Master items.
      - **Checkbox Selection**: Multi-select checkboxes with `(Select All)` and `Clear` controls, exact item frequency counts `(N)`, and full name tooltips.
      - **Server-Side Application**: Applying filters queries the database with server-side ILIKE and IN matching, updating the grid pagination and footer count (`Showing 1-N of Total`).
    - **Inline Cell Editing & CRM Status Swatch:**
      - Single-click or double-click to edit cell values inline.
      - Hover over any cell to display the **Status Swatch Picker**:
        - 🔴 **Red Swatch:** Requirement Raised
        - 🔵 **Blue Swatch:** Ordered to Manufacturer
        - 🟢 **Green Swatch:** Purchased / In Transit
        - 🎨 **Custom Color Swatches:** Admin-defined operational status tags.
      - Real-time WebSocket broadcasting sends cell updates to all connected users, preventing concurrent edit overwrites.

4. **Container CBM Optimization Engine:**
    - Computes total loaded volume in cubic meters ($m^3$) and gross weight ($kg$) live across all planned item rows:
      $$\text{Total CBM} = \sum (\text{Row Quantity} \times \text{Product Packaging Unit CBM})$$
      $$\text{Total Weight} = \sum (\text{Row Quantity} \times \text{Product Packaging Gross Weight})$$
    - **Container Preset Specifications:**
      - **20FT Standard Container:** Max $28.00 \text{ CBM} / 21,500 \text{ kg}$
      - **40FT Standard Container:** Max $58.00 \text{ CBM} / 26,000 \text{ kg}$
      - **40FT High Cube (HC) Container:** Max $68.00 \text{ CBM} / 26,000 \text{ kg}$
      - **LCL (Less than Container Load)**
    - **Visual Load Meter:**
      - Percentage filled gauge: 🟢 Optimal ($< 95\%$), 🟡 Near Capacity ($95–100\%$), 🔴 Overloaded ($> 100\%$).
      - Multi-container distribution recommendations (e.g. `Requires 2 x 40FT HC + 1 x 20FT Container`).

### Test Cases for Shipment Planning Module
- [ ] Open `/planning`, switch between branch sheet tabs, verify active sheet grid renders with default Inhyma organization.
- [ ] Type an item query (e.g. `FR900` or `DKX4540`) into the top **Organization-Wide Search Bar**. Verify it live-filters the active branch sheet (`Inhyma Mumbai`) and opens the cross-branch results dropdown.
- [ ] In the search dropdown, verify it displays match counts across all branches of the active organization (e.g. `Inhyma Mumbai`, `Inhyma Ahmedabad`, `Inhyma Indore`).
- [ ] Click `Switch to Branch →` or click an item under another branch (e.g. `Inhyma Ahmedabad`). Verify active tab switches to `Inhyma Ahmedabad` with the filter applied immediately.
- [ ] Click the clear icon (`✕`) in the top search bar. Verify active sheet filter clears and the full sheet is restored.
- [ ] Click filter funnel on `ITEM` column, verify filter popover opens with distinct items across all rows in the workbook.
- [ ] Paste a product name (e.g. `GF1000FD Granular Filler` or unrendered item) into `Search items...` in filter popover. Verify matching item appears in the list with count.
- [ ] Select matching item, click `Apply`. Verify the grid updates and displays only the matching product with accurate footer count.
- [ ] Click filter funnel again, click `Reset` or `Clear All Filters`. Verify all 1384+ items render again.
- [ ] Click `+ Add Column`, create column `Test Number` with type `NUMBER` and source `MANUAL`. Verify column appears in grid.
- [ ] Edit a cell in the grid, change value, click off, verify cell value persists on reload.
- [ ] Hover over a cell, click the status swatch, select Green (`Purchased`). Verify cell displays green status tag.
- [ ] Click the `Approval Date` column eye icon, verify approval history drawer/popover opens.
- [ ] Click `Container Optimization Calculator`, verify total CBM and weight compute accurately against 20FT / 40FT / 40FT HC container capacity limits.
- [ ] Open `History & Change Log` drawer, verify the cell edits and column additions are logged with timestamps and user names.

---

## 15. USER MANAGEMENT: Users Module

- **Route:** `/users` (also aliased from `/employees`)
- **Purpose:** Complete enterprise person directory for both login-enabled staff and workforce personnel without system access, HR profiles, positions held, reporting hierarchy, and password governance.

### 15.1. Users Table Columns
1. **Checkbox:** Row selector.
2. **SR. NO.:** Index.
3. **EMPLOYEE NAME & AVATAR:** Initials circle + Full Name.
4. **USERNAME:** System login ID (or placeholder for workforce members with `has_login=False`).
5. **EMAIL:** Official corporate email (null for `has_login=False`).
6. **DEPARTMENT / ROLE:** Assigned role/department badges (e.g. `Sales`, `Procurement`, `Admin`).
7. **REPORTING MANAGER:** Manager's full name.
8. **STATUS:** `ACTIVE`, `INACTIVE`, `SUSPENDED`, `LOCKED`, `PASSWORD_CHANGE_REQUIRED`.
9. **ACTIONS:**
   - 👁️ **View Profile Drawer:**
     - HR Profile details (contact, gender, DOB, joining date, address, emergency contact, notes)
     - **Section 6.5: Positions & Reporting Structure:**
       - **Positions:** Badges of all held positions (e.g. `Sales Manager (Primary)`, loaded dynamically via `/positions/holders-for-user/{id}`)
       - **Reports To:** Listing of all managers by relationship type (e.g. `PRIMARY REPORTING: manager id ...`)
       - **Direct Reports:** Listing of direct subordinate personnel (e.g. `PRIMARY REPORTING: employee id ...`)
     - **Section 7: Active Login Sessions:** Lists active device sessions with remote revocation (for accounts with `has_login=True`).
   - ✏️ **Edit Profile:** Opens unified profile drawer, now integrating basic identity details, contact information, employment profile, position assignments, and **Department & Role Assignments** (consolidating the previously separate "Manage Departments" action into one unified interface).
   - 🔑 Reset Password (generates temporary password for login-enabled users)
   - 🔑 Direct Permission Overrides (`🔑 Edit permissions`)
   - ⏸️ **Deactivate User:** Immediately deactivates the user account (`status=INACTIVE`, `is_active=False`), revokes all active device sessions, and prevents login or access token usage. Available for all accounts that are not already inactive (including Active, Password Change Required, Pending, and Locked).
   - ▶️ **Activate User:** Restores an inactive account to `ACTIVE` (`is_active=True`), immediately restoring the ability to log in.
   - ⚡ **Unsuspend Account:** Restores a suspended user back to active status.
   - 🔓 **Unlock Account:** Clears temporary failed-login lockout.
   - 🚪 **Force Logout:** Immediately and forcibly logs out the user across all devices in real time. Sets a revocation timestamp, disconnects live WebSockets, terminates active sessions, and immediately invalidates in-flight access tokens so any ongoing user activity instantly triggers session expiry and redirects them to the login page.
   - 🚫 **Permanent Removal of User Deletion:** User deletion is completely removed from the UI and disabled backend-wide (`DELETE /users/{id}` returns 400 Bad Request) to maintain transactional integrity, foreign key relations, and audit history.

### 15.1.1. Multi-Select & Collective Bulk Deactivation
- **Select All Checkbox (Header):** Selects or deselects all visible user accounts across the current page.
- **Row Checkboxes:** Click to select individual user accounts for collective action.
- **Collective Action Bar & Buttons:**
  - Whenever 1 or more user accounts are selected:
    - **Header Collective Deactivate:** An amber `Deactivate Selected (N)` button appears in the page header actions alongside `+ Create User Account`.
    - **Toolbar Selection Bar:** Renders count pill `N users selected` + `⏸️ Deactivate (N)` amber button + `Deselect all` link.
  - **Account Safety & Protection Guards:**
    - Automatically guards the administrator's currently authenticated account: attempting to collective-deactivate self is excluded with notification.
    - Automatically guards `super_admin` accounts: attempting to collective-deactivate Super Administrators is excluded.
    - Automatically skips accounts that are already inactive.
    - Displays confirmation dialog indicating total accounts to be deactivated and any skipped accounts.
    - Executes batch deactivation via `POST /users/{id}/deactivate` using `Promise.allSettled`, immediately setting account status to `Inactive`, terminating sessions, and clearing selection.

### 15.2. Add / Edit User Form Fields
- **Login Credentials Toggle:**
  - **Give this person ERP login access (`has_login`)** (*Checkbox, default checked*).
  - Uncheck for workforce records with no login (e.g. factory worker, driver, temporary labor, consultant) -- Username, Email, Phone, and Password become optional/disabled.
- **Account Identity (when `has_login=True`):**
  - **First Name** (*Required*), **Middle Name**, **Last Name** (*Optional*).
  - **Display Name** (*Required*): Shown throughout the system in place of raw username.
  - **Position** (*Optional, not red-marked*): Dropdown placed alongside Display Name, dynamically extracted from active positions in the Positions catalog (`/positions/all`). When selected, establishes an initial primary position assignment for the user.
  - **Username** (*Optional*): If left blank, derived automatically from email.
  - **Work Email** (*Required if has_login=True*).
  - **Mobile Number** (*Required if has_login=True*): Phone number with country dial code.
  - **Password** (*Required if has_login=True*): Initial temporary password field equipped with an integrated **Eye toggle button** (`👁️` / `👁️‍🗨️`) allowing the administrator to preview or conceal the plaintext password before submitting.
- **HR & Employment Profile:**
  - **Employee Code**: Unique staff ID (e.g. `EMP-1042`).
  - **Gender**: `Male`, `Female`, `Other`.
  - **Date of Birth** & **Date of Joining**: Date pickers.
  - **Employment Type**: `Full Time`, `Part Time`, `Contract`, `Intern`.
  - **Employment Status**: `Active`, `Inactive`, `On Leave`, `Terminated`, `Resigned`.
  - **Assign Initial Department**: Dropdown of available department roles (defaults to `-- Default: User (System) --`).
    - **Default "User" Assignment:** If left unselected or if no department is specified, the system automatically assigns the individual to the default system **"User"** role (both for login users and workforce records).
    - Selecting a department triggers automatic detection of that department's manager.
  - **Assign Reporting Manager**: Dropdown placed directly beneath "Assign Initial Department".
    - **Automatic Manager Auto-Wiring:** When an initial department is selected, the system immediately queries `/api/v1/users/department-manager/{role_id}` and automatically pre-fills that department's designated manager with a helpful blue confirmation badge.
    - **Manual Override:** The administrator can change or clear the manager to any other user or `-- None (No Manager) --` as needed.
  - **Drawer Usability & Scroll Bar:** The Create User Account modal features a responsive vertical scroll container with a styled scrollbar and sticky bottom footer (`Cancel` and `Create User Account` action buttons), ensuring all inputs remain comfortably accessible on viewports of all heights.

### 15.3. One-Time Temporary Password Modal
- When creating a user or resetting a password, the system generates a secure temporary password.
- Displays password in a highlighted box with a **`📋 Copy Password`** button.

### 15.4. Edit User Profile & HR Details Drawer
- **Drawer Layout & Usability:** Side-drawer overlay with full viewport height (`calc(100vh - 60px)`), smooth vertical scroll container (`flex: 1`, `overflowY: auto`), and a pinned sticky footer (`.form-actions`).
- **Footer Action Buttons:** `Cancel` (secondary outline button) and `Save Changes` (primary blue button) pinned neatly at the bottom with fixed height (38px), aligned horizontally to the right without vertical distortion.
- **Sections Included:**
  - **Basic & Identity Details:** First Name, Middle Name, Last Name, Username (*Required*), Display Name, Employee Code.
  - **Contact Information:** Work Email (*Required*), Mobile / Phone Number (*Required*), Emergency Contact.
  - **Employment & HR Profile:**
    - **Reporting Manager & Position:** Side-by-side dropdown selectors. The **Position** dropdown is dynamically populated from active positions in `/positions/all` and automatically pre-selected with the employee's current primary position assignment. Selecting a new position or `-- None (No Position) --` updates the assignment atomically upon clicking `Save Changes`.
    - **Gender & Employment Type:** `Gender` (`Male`, `Female`, `Other`, `Prefer Not to Say`) and `Employment Type` (`Full Time`, `Part Time`, `Contract`, `Intern`, `Temporary`).
    - **Employment Status & Dates:** `Employment Status` (`Active`, `Inactive`, `On Leave`, `Terminated`, `Resigned`), `Date of Joining`, and `Date of Birth`.
  - **Address & Location Details:** Street Address, City, State / Province, Country, Postal / PIN Code.
  - **Internal Administrator Notes:** Free-form text area for administrative annotations.
  - **Department & Role Assignments (Integrated):**
    - Displays active department/role memberships with badges, primary indicator (`PRIMARY`), assignment types (`PRIMARY`, `SECONDARY`, `TEMPORARY`, `PROJECT`, `ACTING`), and remove action (`×`).
    - Inline selector to add new departments with role dropdown, assignment type, and effective dates.
    - Synchronizes changes immediately upon addition or removal without closing the drawer, eliminating the need for a separate modal.

### 15.5. Test Cases for Users Module
- [ ] Open `/users`, verify User Accounts & Passwords table loads with search bar, status dropdown filter, and `+ Create User Account` button.
- [ ] Verify each row has a checkbox and the table header has a `select-all-checkbox`.
- [ ] Check multiple user checkboxes. Verify:
  - Header actions render an amber **`Deactivate Selected (N)`** button.
  - Toolbar renders a selection indicator: `N users selected` with a **`⏸️ Deactivate (N)`** button and a **`Deselect all`** link.
- [ ] Click `Deselect all`. Verify all checkboxes are cleared and the bulk deactivate buttons disappear.
- [ ] Check a selection that includes your own authenticated account or a `super_admin`. Click `Deactivate Selected`. Verify:
  - Confirmation modal pops up warning that own account and Super Admin accounts cannot be deactivated and will be skipped.
  - Remaining eligible accounts are deactivated (`status=Inactive`, `is_active=False`) and active sessions terminated in real-time.
- [ ] **Deactivation Login Block**: Verify that any deactivated user cannot log in at `/login`, receiving an immediate `403 Forbidden: Account is inactive or locked.` and cannot authenticate.
- [ ] **Real-Time Force Logout**: Click `🚪 Force Logout` on an active user account. Verify:
  - User's active session is terminated in the database.
  - User's active browser tabs receive a real-time WebSocket disconnect (`code 4001`) and are immediately redirected to `/login`.
  - In-flight access tokens are invalidated via cache timestamp check (`auth_force_logout:{user_id}`).
- [ ] Click `✏️ Edit Profile` on a user row. Verify:
  - Drawer opens with identity, HR attributes, and dynamically populated **Position** dropdown.
  - **Department & Role Assignments** section is displayed directly inside the drawer.
  - Adding or removing departments updates the user's role assignments immediately with live table sync.

---

## 16. USER MANAGEMENT: Departments & Permissions (RBAC) Module

- **Route:** `/rbac`
- **Purpose:** Department role definitions, organizational hierarchy nesting, department managers, permission matrices, and user reassignment.

### 16.1. Departments Table
- **Columns:** Checkbox, Sr. No., Department Name, Created Date, Actions.
- **Header Actions:** `+ ADD NEW DEPARTMENT`, `Bulk Delete`.

### 16.2. Department View / Edit Modal
- **Department Name** (*Required*): Title (reserved system roles like `super_admin` are protected).
- **Department Code**: Optional short organizational code (e.g. `SALES`). Purely organizational labeling.
- **Parent Departments Section (in Department Details):**
  - Displays all currently assigned parent departments as removable badge tags (`🏢 Department Name (CODE) [×]`).
  - Dropdown selector (`-- Add another parent department --`) with eligible roles (excluding self, active children, active parents, and system admin) + `+ Add Parent` button.
  - Immediately unlinks or adds parents with live real-time sync. Supports **multiple parent departments** per department.
- **Description**: Text area.
- **Department Managers Section:**
  - Select user to designate as **Department Manager**.
  - Roster displays manager with `⭐ MANAGER` badge.
  - **`🔑 Edit permissions` Button:** Opens per-user direct permission override drawer to grant manager extra elevated privileges without altering base role.
  - Setting a manager automatically updates reporting hierarchy for department members.
- **Department Members Section ("Users in this Department"):**
  - Add / remove employees assigned to this department with real-time membership counts.
- **Child Departments Card (directly beneath "Users in this Department"):**
  - Dedicated card in the left column displaying all sub-departments that report to or are nested under the active department.
  - **Header Badge:** Displays active count of connected sub-departments (e.g. `2 sub-departments`).
  - **Add Child Selector:** Dropdown `Select child department to add...` + `+ Add` button.
  - **Child Department Row:**
    - Green initial icon + Department Name + Code badge.
    - Member count badge (`👤 X members`).
    - `View` button: Directly navigates to and opens that child department.
    - `Remove` button: Unlinks the child department from this parent.
    - Clean empty state when no child departments are connected.
- **Bidirectional Live Auto-Sync:** Connecting a child department under a parent (e.g. Sales under Operations) immediately updates both departments' rosters so Operations lists Sales as a child, and Sales lists Operations as a parent.
- **DAG Cycle Detection:** Server-side validation prevents circular hierarchies (e.g. A -> B -> A or A -> B -> C -> A) and returns HTTP 409 Conflict with an alert.
- **Permission Matrix Grid:**
  - Grouped by module cards: `Dashboard`, `Contact`, `Inventory`, `Sale`, `Planning`, `User Management`, `Configurations`, `Audit`, `Trash`.
  - `Select All` / `Deselect All` toggles per module.
  - Checkboxes for granular permissions (`.view`, `.create`, `.update`, `.delete`, `.export`, `.import`, `.bulk_action`, etc.).
- **Clone Department Button:** Creates a copy of the department with all permissions pre-checked.
- **Safe Delete with Reassignment Modal:** If users exist in a department scheduled for deletion, prompts administrator to select a replacement department to reassign those employees before deletion proceeds.

### 16.3. Test Cases for Departments & Permissions Module
- [ ] Open `/rbac`, click on a department (e.g. `Operations`), verify Left Column renders:
  1. Department Details (Name, Description, Code, Parent Departments)
  2. Managers in this Department
  3. Users in this Department
  4. **Child Departments** (directly beneath Users in this Department)
- [ ] In **Child Departments** card, select another department (e.g. `Sales`) from the dropdown and click `+ Add`. Verify `Sales` appears in the list with member count and `View` / `Remove` buttons.
- [ ] Click `Back to Departments` and open `Sales`. Verify `Operations` is displayed under **Parent Departments** as a removable badge tag (`🏢 Operations [×]`).
- [ ] In `Sales`, select another parent department (e.g. `Executive Management`) and click `+ Add Parent`. Verify `Sales` now lists multiple parents (`Operations` and `Executive Management`).
- [ ] Attempt to add `Operations` as a child department of `Sales`. Verify cycle detection triggers and rejects the circular connection with the error: *"This would create a circular department hierarchy."*
- [ ] In `Operations` -> Child Departments, click `Remove` next to `Sales`. Verify `Sales` is unlinked and no longer appears under Child Departments or as Sales's parent.

---

## 17. CONFIGURATIONS: HSN Codes Master Module

- **Route:** `/masters/hsn`
- **Table Columns:** SR. NO., HSN / SAC Code, Description, GST/VAT Rate (%), Refund VAT Rate (%), Status, Actions.
- **Add / Edit Form Fields:**
  - **HSN / SAC Code** (*Required*): 6 to 8 digit customs tariff code.
  - **Description**: Trade description.
  - **GST / VAT Rate (%)**: Standard domestic rate.
  - **Refund VAT Rate (%)**: Export tax rebate percentage.
  - **Status**: `Active` / `Inactive`.

---

## 18. CONFIGURATIONS: Geography Masters (Countries, Provinces, Cities)

### 18.1. Countries (`/masters/countries`)
- **Fields:** Country Name (*Required*), ISO Code 2 (e.g. `CN`, `IN`, `US`), ISO Code 3, International Phone Dial Code (e.g. `+86`, `+91`), Currency Code, Status.

### 18.2. Provinces / States (`/masters/states`)
- **Fields:** Country (*Required dropdown*), State / Province Name (*Required*), State Code, Status.

### 18.3. Cities (`/masters/cities`)
- **Fields:** Country (*Required*), State / Province (*Required, scoped to Country*), City Name (*Required*), City Code, Status.

---

## 19. CONFIGURATIONS: Currencies Master Module

- **Route:** `/masters/currencies`
- **Fields:** Currency Code (*Required*, e.g. `USD`, `CNY`, `INR`, `EUR`), Currency Name, Currency Symbol (e.g. `$`, `¥`, `₹`, `€`), Exchange Rate to Base Currency, Is Base Currency (`true`/`false`), Status.

---

## 20. CONFIGURATIONS: Units of Measurement (UOM) Master Module

- **Route:** `/masters/uom`
- **Fields:** UOM Name (*Required*, e.g. Pieces, Sets, Kilograms, Meters, Rolls, Boxes), UOM Code (e.g. `PCS`, `SET`, `KG`), Symbol, Unit Category, Status.

---

## 21. CONFIGURATIONS: Organization Settings & Company List

### 21.1. Organization Settings (`/organization`)
- **Single-Tenant Corporate Profile Fields:**
  - Company Legal Name, Trade Name, Official Email, Phone, Website.
  - Tax Registration Number (GST / PAN / VAT / TIN).
  - Operating Timezone, Base Currency, Business Hours.
  - Registered Head Office Address, City, State, Country, Postal Code.
- **Actions:** `Edit Organization`, `Save Changes`, `Cancel`. Automatically updates brand name across sidebar.

### 21.2. Organization List (`/masters/company-list`)
- Multi-company entity catalog for group enterprises.
- **Fields:** Company Name, Legal Entity Type, Registration Number, Base Currency, Status.

---

## 22. GOVERNANCE: Audit Log Module

- **Route:** `/audit`
- **Purpose:** Immutable compliance trail capturing all entity mutations across the ERP.
- **Table Columns:** Timestamp (UTC & Local), Actor (User Name & ID), Action Type (`CREATE`, `UPDATE`, `DELETE`, `LOGIN`, `PASSWORD_RESET`, `BULK_ACTION`), Target Entity (`Supplier`, `Product`, `Inquiry`, `User`), Entity ID, IP Address, HTTP Status Code.
- **JSON Delta Viewer Modal:** Click row opens side-by-side before-and-after JSON diff highlighting altered fields.
- **Filters:** Action type dropdown, Entity type, User picker, Date range.

---

## 23. GOVERNANCE: Trash & Recovery (Recycle Bin) Module

- **Route:** `/trash`
- **Purpose:** Universal soft-delete registry allowing one-click data restoration.
- **Table Columns:** Checkbox, Entity Type (e.g. `Supplier`, `Buyer`, `Product`, `Inquiry`), Record Name / Title, Deleted At Timestamp, Deleted By User, Actions.
- **Header Actions:** Module Filter dropdown (`ALL`, `Suppliers`, `Buyers`, `Products`, etc.), Search query.
- **Row Actions:**
  - 🔄 **`Restore` Button:** Restores deleted record back to its active table with relational integrity preserved.
  - ❌ **`Purge` Button:** Permanently deletes record from database (restricted to Super Administrator).
- **Bulk Actions:** `Restore Selected`, `Empty Trash`.

### Trash Conflict Detection & One-Click Restore Modal (`TrashConflictModal.tsx`)
- **Applies To:** All 12 Master Data catalogs (Categories, Sub Categories, Brands, UOM, HSN, Countries, States, Cities, Currencies, Supplier Types, Buyer Types, Companies), Product Master, Buyer Management, Supplier Directory, and Quick Inquiry Drawer.
- **Test Checklist:**
  1. **Category Soft-Delete & Re-creation Conflict:**
     - Navigate to `/masters/categories`.
     - Create category `"Alpha Test 1"`.
     - Soft-delete `"Alpha Test 1"` (record moves to Trash).
     - Click `+ Add Category` and enter name `"Alpha Test 1"`.
     - Click `Save`.
     - **Expected Outcome:** Instead of a 500 error or unexpected crash, an interactive `TrashConflictModal` dialog immediately appears stating: *"Category Already Exists in Trash"*, displaying the matching Name and Code.
  2. **One-Click Restore Action:**
     - In the conflict popup, click `[ 🔄 Restore Alpha Test 1 from Trash ]`.
     - **Expected Outcome:** The modal shows *"Restoring..."* briefly, closes, the categories table refreshes showing `"Alpha Test 1"` active again, and global dropdown caches are invalidated.
  3. **Preserve Form Inputs on Cancel:**
     - Open the create drawer for any entity (e.g. Buyer or Product).
     - Enter detailed information across multiple fields (e.g. 5 contact fields, website, categories).
     - Use a company name that exists in Trash. Click `Save`.
     - When `TrashConflictModal` appears, click `[ Change Name / Cancel ]`.
     - **Expected Outcome:** The popup closes, but the create drawer remains completely OPEN with all entered values, phone numbers, and categories 100% preserved so the user can easily adjust the name without re-entering anything.
  4. **Open Trash Shortcut:**
     - In `TrashConflictModal`, click `[ Open Trash ↗ ]`.
     - **Expected Outcome:** Opens `/trash` in a new browser tab without losing the current page context.
  5. **Inquiry Consignment Code Re-use & Multi-Item Append:**
     - Open `QuickInquiryDrawer` on `/inquiries`.
     - Add 3 product line items with quantities, brands, and remarks.
     - Specify a consignment code that exists in Trash.
     - Click `Save as Proposed`.
     - **Expected Outcome:** The conflict modal opens with primary action `[ 🔄 Restore & Append My Items ]`. Clicking it restores the consignment and immediately appends all 3 line items into it with zero manual re-entry.

---

## 24. USER ACCOUNT: Profile, Security & Active Sessions

- **Route:** `/profile`
- **Section 1: Personal Details:** First Name, Last Name, Email, Contact Number, `Save Profile` button.
- **Section 2: Security & Password:** Current Password, New Password, Confirm Password, show/hide eye icons, `Update Password` button.
- **Section 3: Active Device Sessions:** List of active browser sessions (Browser, OS, IP Address, Device Category, Last Active). Action: `Revoke Session` button.

---

## 25. AUTHENTICATION: Login & Session Recovery

- **Route:** `/login`
- **Form Fields:** Username or Corporate Email (*Required*), Password (*Required*), "Remember Me" checkbox, `Sign In` button.
- **Security Logic:** Rate-limiting protection on failed attempts; automated single-flight token refresh upon access token expiration (`/auth/refresh`).
- **Deactivated Account Immunity & Permanent Deletion Retirement:** User deletion is completely disabled across the system. Deactivated accounts (`is_active=False`, `status=INACTIVE`) cannot log in under any circumstances. Submitting credentials for a deactivated user fails immediately with `403 Forbidden: Account is inactive or locked.`, preventing authentication. Any existing active JWT access tokens are immediately rejected on API calls, and clicking `Force Logout` instantly expels active sessions via real-time WebSocket termination and token invalidation.

---

## 26. EXTERNAL PORTAL: Public Supplier Quotation Submission Portal

- **Route:** `/quote/:token` (Public, No Login Required)
- **Purpose:** Secure tokenized web portal sent to vendors via RFQ emails/WeChat.
- **Display Data:** Inquiry Item Code, Product Name, Technical Specifications, Target Delivery Date, Buyer RFQ Remarks.
- **Supplier Bid Submission Form:**
  - **Unit Price** (*Required*): Number input.
  - **Currency** (*Required*): Dropdown (`CNY`, `USD`, `INR`, `EUR`).
  - **Lead Time (Days)**: Delivery turnaround time.
  - **Commercial Terms & Conditions**: Payment terms, validity period.
  - **Quotation Sheet / PDF Upload**: Direct upload of vendor price quotation to Supabase Cloud Storage.
  - **`Submit Quotation` Button:** Posts bid to backend, updates inquiry status to `QUOTES_RECEIVED`, and notifies procurement officers.

---

## 27. TOPBAR: Universal Search & Record Deep-Linking

- **Component:** `UniversalSearch.tsx` (Top Navigation Bar)
- **Keyboard Shortcuts:** `ArrowUp`, `ArrowDown`, `Enter` (Navigate results), `Escape` (Close dropdown).
- **Backend Search Service:** `GET /search?q=<term>` (`app.search.service`) querying Organizations, Users, Suppliers, Buyers, Products, Product Categories, Sub-Categories, Brands, HSN Codes, Countries, States, Cities, Currencies, and UOM.
- **Deep-Linking Test Cases:**
  1. **Supplier Deep-Link:** Search for a supplier (e.g. `Darsh Impex`), click result $\rightarrow$ Lands on `/suppliers?id=<uuid>`, automatically loads supplier profile and opens `SideDrawer` displaying all details, contacts, categories, and remarks.
  2. **Buyer Deep-Link:** Search for a buyer, click result $\rightarrow$ Lands on `/buyers?id=<uuid>`, automatically loads buyer details and opens `SideDrawer`.
  3. **Product Deep-Link:** Search for a product, click result $\rightarrow$ Lands on `/masters/products?id=<uuid>`, automatically loads product details and opens `SideDrawer`.
  4. **User Deep-Link:** Search for a user member, click result $\rightarrow$ Lands on `/users?id=<uuid>`, automatically loads profile and opens View User Modal.
  5. **Master Data Deep-Link:** Search for Categories, Brands, HSN, Countries, Currencies, etc., click result $\rightarrow$ Opens corresponding master record drawer via `MasterPage.tsx`.
  6. **Drawer Close / URL Cleanup:** Closing the drawer or modal cleanly removes `?id=` from the URL and supports back-button navigation.

---

## 28. USER MANAGEMENT: Unified Person & Workforce Architecture (Employee-to-User Merge)

- **Route:** `/users` (with `/employees` as a route alias)
- **Architecture & Merge Rationale:** Workforce personnel records and user login accounts are unified on the `User` entity (`users` table). Rather than splitting people into two separate screens (`/users` and `/employees`) requiring linking steps, the system uses a single boolean attribute: **`has_login: bool`**.
  - **Login-Enabled Users (`has_login=True`):** Full system accounts with `username`, `email`, `phone`, and `password_hash`. Subject to session management, rate limits, lockouts, and authentication dependencies.
  - **Workforce Members (`has_login=False`):** Offline or field workforce members (e.g. factory floor workers, drivers, warehouse temporary labor, consultants). Created without username, email, phone, or password credentials. Authentication is rejected before password hashing; account status is `INACTIVE` for login but active for organizational assignments.

---

## 29. USER MANAGEMENT: Unified Departments & Organizational Units (Department-to-Role Merge)

- **Route:** `/rbac` (Departments & Permissions)
- **Architecture & Merge Rationale:** Organizational departments and software permission bundles are unified onto the `Role` entity (`roles` table). This eliminates the confusion of having two separate "Departments" screens.
  - **Organizational Structure:** Roles carry `code` (e.g. `SALES`) and multi-parent / multi-child relationships via `department_hierarchy` and `roles.parent_department_id` (supporting many-to-many parent and child departments with server-side circular dependency validation via `would_create_cycle`).
  - **Software Permissions:** Roles bundle fine-grained permission codes (`role_permissions`).
  - **User Role Assignments:** Modeled in `user_roles` with `assignment_type` (`PRIMARY`, `SECONDARY`, `TEMPORARY`, `PROJECT`, `ACTING`), `is_primary`, and effective date ranges.

---

## 30. USER MANAGEMENT: Positions Module

- **Route:** `/positions` (Sidebar Icon: `briefcase`)
- **Purpose:** Professional designations and job titles (e.g. "Sales Manager", "Marketing Advisor", "Senior Engineer") that employees hold.
- **Independence:** Holds no reporting-hierarchy or software-permission logic -- designations do not dictate who reports to whom or software access privileges.
- **Table Columns:** SR. NO., NAME, CODE, EMPLOYEES, STATUS, ACTION (standard master CRUD).
  - **Employees Column:** Displays a dynamic badge (e.g. `👤 1`) showing how many employees currently hold the position.
- **Add / Edit Form Fields:** Position Name (*Required*), Code, Description, Status (supports case-insensitive ACTIVE / INACTIVE / ARCHIVED).
- **Safety & Deletion Freeze Rules:**
  - **Locked/Frozen Delete Button:** If any employees are assigned to a position (`employee_count > 0`), the delete button is completely frozen and locked with a lock icon, disabled appearance, `cursor: not-allowed`, and a hover tooltip explaining that deletion is locked due to active assignments.
  - **Warning Alert Modal:** If the user attempts to click the locked delete button, an immediate modal alert dialog appears explaining that the position cannot be deleted because employees are currently attached to it.
  - **Bulk Delete Protection:** If multiple items are selected for bulk deletion, any positions with active employees are automatically protected and skipped, with an alert notifying the administrator.
  - **Server-Side Conflict Enforcement:** Deletion requests (`DELETE /positions/{id}`) are rejected server-side with HTTP 409 Conflict if active assignments exist.
- **User Profile Display:** Active positions held by a user are displayed in Section 6.5 of the User Profile Drawer via `GET /positions/holders-for-user/{user_id}`.

---

## 31. USER MANAGEMENT: Organization Chart Module

- **Route:** `/org-chart` (Sidebar Icon: `orgChart`)
- **Purpose:** Dynamic, real-time visual hierarchy of company reporting lines, built entirely from active `PRIMARY_REPORTING` relationships (`GET /reporting/org-chart`).
- **Display & Rendering:**
  - Multi-level hierarchical tree diagram with interactive node expansion and collapse.
  - Node resolution dynamically loads person names via `UserRepository.list_all()`.
  - Enforces mandatory server-side cycle detection (`ReportingService.would_create_cycle`) preventing any self-reporting (`A -> A`) or circular reporting (`A -> B -> C -> A`).
  - **Drag-and-Drop Manager Assignment:** Dragging and dropping an employee's card onto a new manager calls `POST /api/v1/reporting/set-manager/{employee_id}` with `manager_employee_id`, updating the primary relationship atomically with cycle validation.
  - Updates dynamically whenever reporting lines are reassigned or updated.

---

## 32. AI Subagent Autonomous Testing Prompt Template

When instructing an autonomous AI agent to verify the ERP after code modifications, copy and run the following prompt:

```markdown
You are acting as an Autonomous QA Tester for the Enterprise ERP.
Your task is to verify that all modules and features described in MODULES_AND_FEATURES_TEST_MANUAL.md exist and function without regressions.

Checklist to execute:
1. Compile backend: Run `python -m compileall backend/app` -> must return 0 errors.
2. Build frontend: Run `npm run typecheck` and `npm run build` in /frontend -> must compile cleanly.
3. Verify module routes in frontend/src/App.tsx and frontend/src/lib/nav.ts match the sitemap in Section 2, and all 26 nav items possess distinct, non-duplicated icons.
4. Verify all form fields, modals, and actions documented for Suppliers, Buyers, Products, Inquiries, Planning, and Users remain intact.
5. Verify the unified User Architecture:
   - Creating a user with `has_login=True` requires email, phone, and password.
   - Creating a user with `has_login=False` permits saving without email, phone, or password.
   - Profile drawer displays Section 6.5 (Positions & Reporting Structure).
   - Positions (/positions, icon: briefcase) and Organization Chart (/org-chart, icon: orgChart) render and function.
   - Departments (/rbac) support optional short code and parent department nesting.
6. Report any missing fields, broken endpoints, or regressions.
```

---

## 33. Universal Import & Deduplication Test Suite (`testingimportfile/`)

A standardized suite of 8 production-grade Excel (`.xlsx`) files is maintained directly in `testingimportfile/` to allow developers and QA engineers to execute end-to-end import and duplicate-detection testing across the 4 core business modules:

### 33.1. Supplier Master (`/suppliers`)
- **Folder:** `testingimportfile/`
- **File 1 (Clean Data):** `supplier_new_data.xlsx`
  - **Rows:** 2 new supplier companies ("Hangzhou Precision Pack Machinery Co., Ltd.", "Apex Automation Systems Pvt. Ltd.")
  - **Headers:** `Company Name`, `Product Categories`, `Key Strength Sub-Categories`, `Products Supplied`, `Secondary Products`, `Country`, `State / Province`, `City`, `Brand Description`, `Supplier Type`, `Current Status`, `Supplier Grade`, `Potential`, `Potential Reason`, `Contact Person`, `Designation`, `Calling Number`, `WhatsApp Number`, `WeChat Number`, `Emails`, `Tax ID / GST Number`, `Address`, `Town`, `Primary Website`, `Secondary Website`, `Visited Factory/Office`, `Visit Remarks`, `Overall Remarks`, `Status`.
  - **Expected Result:** `created: 2, failed: 0`. Both suppliers created successfully and linked to their respective City/State/Country and Category/Sub-Category masters.
- **File 2 (Duplicate / Conflict Data):** `supplier_duplicate_data.xlsx`
  - **Rows:** 4 rows:
    - Row 2: Existing Supplier "Yinglima Packaging Machinery Co., Ltd." (in Wenzhou, China).
    - Row 3: Existing Supplier "Darsh Impex" (in Mumbai, India).
    - Row 4: New company "Newtech Sealing Solutions Co., Ltd." (First entry in batch).
    - Row 5: Same company "Newtech Sealing Solutions Co., Ltd." (Second entry in same batch).
  - **Expected Result:** Rows 2 and 3 skipped/flagged as existing DB duplicates (`ConflictException`). Row 5 flagged as an in-file batch duplicate.

### 33.2. Buyer (Client) Master (`/buyers`)
- **Folder:** `testingimportfile/`
- **File 1 (Clean Data):** `buyer_new_data.xlsx`
  - **Rows:** 2 new buyers ("Zenith Food & Beverage Processing Ltd.", "Global Agro Industries Ltd.")
  - **Headers:** `Company Name`, `Buyer Type`, `Product Categories`, `Product Sub Categories`, `Country`, `City`, `Address`, `Contact Salutation`, `Contact Person Name`, `Designation`, `Calling Number`, `WhatsApp Number`, `Emails`, `Tax ID / GST Number`, `Website`, `Current Status`, `Buyer Grade`, `Potential`, `Potential Reason`, `Product Range`, `Currently Buying From`, `Overall Remarks`, `Status`.
  - **Expected Result:** `created: 2, failed: 0`. Clean import with full contact, salutation, category, and city linking.
- **File 2 (Duplicate / Conflict Data):** `buyer_duplicate_data.xlsx`
  - **Rows:** 5 rows testing Note 66 3-way deduplication:
    - Row 2: "Darsh Impex" -> Triggers Duplicate Company Name collision.
    - Row 3: "Sunrise FMCG Exports Pvt. Ltd." with Calling Number `+91 77384172578` -> Triggers Duplicate Calling Number collision.
    - Row 4: "Horizon Pack Solutions LLP" with WhatsApp Number `+91 77384172578` -> Triggers Duplicate WhatsApp Number collision.
    - Row 5: "Alpha Pack Industries" -> First entry in batch.
    - Row 6: "Alpha Pack Industries" -> Second entry in batch -> Triggers in-file duplicate collision.
  - **Expected Result:** 4 duplicate conflicts correctly captured and isolated; existing records protected from overwrite.

### 33.3. Product Master (`/masters/products`)
- **Folder:** `testingimportfile/`
- **File 1 (Clean Data):** `product_new_data.xlsx`
  - **Rows:** 3 new machine products ("High Speed Continuous Band Sealer Model CBS-900", "Semi-Automatic Carton Sealer Model FX-500", "Heavy Duty Liquid Piston Filling Machine 500ml").
  - **Headers:** `Product Name (As Per Tally)`, `Product Code`, `Brand`, `Category`, `Sub Category`, `HSN Code`, `UOM`, `Organization`, `Branches`, `Pack. Qty`, `Pack. Net Weight`, `Pack. Gross Weight`, `Length (cm)`, `Width (cm)`, `Height (cm)`, `Pack. Unit CBM`, `Refund VAT %`, `Compliance & License Requirements`, `Specification`, `Status`.
  - **Expected Result:** `created: 3, failed: 0`. All 3 products created with auto-calculated CBM and valid category-to-subcategory mapping.
- **File 2 (Duplicate / Conflict Data):** `product_duplicate_data.xlsx`
  - **Rows:** 4 rows:
    - Row 2: Product Name "Ink Cup Set ( TDY 380C)" -> Triggers duplicate Product Name collision (existing code `DAR-01849`).
    - Row 3: Product Code `DAR-01851` -> Triggers duplicate Product Code collision (existing product "Ink Roll (MY 380F)").
    - Row 4: "Digital Ultrasonic Cleaner 30L Industrial" (Code `PRD-BATCH-DUP-01`) -> First entry in batch.
    - Row 5: "Digital Ultrasonic Cleaner 30L Industrial" (Code `PRD-BATCH-DUP-02`) -> Triggers in-file duplicate Product Name collision.
  - **Expected Result:** 3 duplicate conflicts captured and skipped; zero corruption of existing catalog.

### 33.4. Inquiry Consignment Line Items (`/inquiries/{inquiry_id}/items`)
- **Folder:** `testingimportfile/`
- **File 1 (Clean Data):** `inquiry_items_new_data.xlsx`
  - **Rows:** 4 valid line items referencing active Product Master items:
    - Row 2: "Ink Cup Set ( TDY 380C)" (Code `DAR-01849`, Qty: 50, Status: Approved)
    - Row 3: "Ink Roll (MY 380F)" (Code `DAR-01851`, Qty: 100, Status: Proposed)
    - Row 4: "Mother Board for Handy and Printer" (Code `DAR-01852`, Qty: 20, Status: Approved)
    - Row 5: "Motor (Tdy 380)" (Code `DAR-01853`, Qty: 15, Status: Proposed)
  - **Headers:** `Product Name`, `Product Code`, `Quantity`, `UOM`, `Brand Preference`, `Product Specs / Remarks`, `Status`.
  - **Expected Result:** `created: 4, failed: 0`. All 4 items imported into consignment with automatic UOM inheritance and consignment rollup calculation.
- **File 2 (Duplicate & Validation Test Data):** `inquiry_items_duplicate_data.xlsx`
  - **Rows:** 4 rows testing duplicate items and validation handling:
    - Row 2: "Ink Cup Set ( TDY 380C)" (Qty: 50, Status: Approved) -> Initial entry.
    - Row 3: "Ink Cup Set ( TDY 380C)" (Qty: 50, Status: Approved) -> Duplicate line item entry.
    - Row 4: "Non-Existent Mystery Widget 999" (Code `NON-EXISTENT-SKU-999`) -> Triggers "Product not found in Product Master" failure.
    - Row 5: "Motor (Tdy 380)" with Quantity `0` -> Triggers "Invalid quantity. Must be a positive number" failure.
  - **Expected Result:** 2 valid rows imported; 2 invalid rows accurately flagged with exact row numbers and error descriptions.

---
*End of Master Features & Testing Specification Manual. Maintained for Inhyma Solutions Enterprise ERP.*