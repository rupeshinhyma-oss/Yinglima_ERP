/**
 * Product Price Directory (Supplier Pricing Catalog).
 *
 * Dedicated module allowing sales, procurement, and management to view, search,
 * and inline-edit purchase prices across all products and suppliers.
 * Implements Option 1: Best Price Main Row + Expandable Accordion Sub-table.
 */

import { Fragment, useCallback, useEffect, useMemo, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { Breadcrumb } from "@/components/Breadcrumb";
import { Pagination } from "@/components/Pagination";
import { SideDrawer, DetailFieldGrid } from "@/components/SideDrawer";
import { Banner, Modal } from "@/components/ui";
import { SearchableDropdown } from "@/components/SearchableDropdown";
import { apiDelete, apiGet, apiPatch, apiPost, apiPostMultipart, API_ORIGIN, toQueryString } from "@/lib/api";
import { useLookup } from "@/lib/lookups";
import type { Brand, Hsn, Product, ProductCategory, ProductSubCategory, Uom } from "@/types";

interface ProductPriceRow {
  product_id: string;
  product_code: string | null;
  product_name: string;
  product_name_tally: string;
  barcode: string | null;
  category_id: string | null;
  category_name: string | null;
  sub_category_id: string | null;
  sub_category_name: string | null;
  brand_id: string | null;
  brand_name: string | null;
  uom_id: string | null;
  uom_code: string | null;
  images: string[] | null;
  best_price: number | null;
  best_currency: string | null;
  primary_supplier_id: string | null;
  primary_supplier_name: string | null;
  primary_link_id: string | null;
  supplier_count: number;
  has_price: boolean;
}

interface SupplierQuote {
  link_id: string;
  product_id: string;
  supplier_id: string;
  supplier_name: string;
  supplier_code: string | null;
  contact_calling_number: string | null;
  contact_whatsapp_number: string | null;
  contact_wechat_number: string | null;
  city_name: string | null;
  state_name: string | null;
  country_name: string | null;
  unit_price: number | null;
  currency: string;
  moq: number | null;
  notes: string | null;
  updated_at: string | null;
  created_at: string | null;
}

interface SupplierLookupItem {
  id: string;
  company_name: string;
  supplier_type?: string;
}

function resolveImageUrl(url: string | null | undefined): string {
  if (!url) return "";
  let clean = url.trim();
  if ((clean.startsWith('"') && clean.endsWith('"')) || (clean.startsWith("'") && clean.endsWith("'"))) {
    clean = clean.slice(1, -1).trim();
  }
  if (!clean) return "";
  if (clean.toLowerCase().startsWith("/static/uploads/")) {
    clean = "/static/uploads/" + clean.slice("/static/uploads/".length);
  } else if (clean.toLowerCase().startsWith("/uploads/")) {
    clean = "/uploads/" + clean.slice("/uploads/".length);
  }
  if (clean.startsWith("data:") || clean.startsWith("http://") || clean.startsWith("https://")) {
    return encodeURI(clean);
  }
  const fullUrl = `${API_ORIGIN}${clean.startsWith("/") ? "" : "/"}${clean}`;
  return encodeURI(fullUrl);
}

function formatCurrency(amount: number | null | undefined, currency = "CNY"): string {
  if (amount == null) return "—";
  const symbol = currency === "USD" ? "$" : currency === "EUR" ? "€" : currency === "INR" ? "₹" : "¥";
  return `${symbol} ${Number(amount).toFixed(2)}`;
}

export function ProductPricesPage() {
  // Query Filters & Pagination State
  const [items, setItems] = useState<ProductPriceRow[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<unknown>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(50);
  const [totalItems, setTotalItems] = useState<number>(0);
  const [totalPages, setTotalPages] = useState<number>(1);

  const [searchTerm, setSearchTerm] = useState<string>("");
  const [debouncedSearch, setDebouncedSearch] = useState<string>("");
  const [categoryFilter, setCategoryFilter] = useState<string>("");
  const [subCategoryFilter, setSubCategoryFilter] = useState<string>("");
  const [brandFilter, setBrandFilter] = useState<string>("");
  const [pricingStatusFilter, setPricingStatusFilter] = useState<"all" | "priced" | "unpriced">("all");
  const [sortBy, setSortBy] = useState<string>("product_name_tally");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");

  // Accordion Expand State: product_id -> boolean
  const [expandedRows, setExpandedRows] = useState<Record<string, boolean>>({});
  const [supplierQuotes, setSupplierQuotes] = useState<Record<string, SupplierQuote[]>>({});
  const [loadingQuotes, setLoadingQuotes] = useState<Record<string, boolean>>({});

  // Inline Price Editing State
  const [editingLinkId, setEditingLinkId] = useState<string | null>(null);
  const [editPriceInput, setEditPriceInput] = useState<string>("");
  const [savingLinkId, setSavingLinkId] = useState<string | null>(null);

  // Sub-table Quick Add State
  const [subTableSupplierId, setSubTableSupplierId] = useState<Record<string, string>>({});
  const [subTablePrice, setSubTablePrice] = useState<Record<string, string>>({});
  const [subTableCurrency, setSubTableCurrency] = useState<Record<string, string>>({});
  const [subTableMoq, setSubTableMoq] = useState<Record<string, string>>({});
  const [subTableSaving, setSubTableSaving] = useState<Record<string, boolean>>({});

  // Modals
  const [assignModalProduct, setAssignModalProduct] = useState<ProductPriceRow | null>(null);
  const [assignSupplierId, setAssignSupplierId] = useState<string>("");
  const [assignUnitPrice, setAssignUnitPrice] = useState<string>("");
  const [assignCurrency, setAssignCurrency] = useState<string>("CNY");
  const [assignMoq, setAssignMoq] = useState<string>("");
  const [assignNotes, setAssignNotes] = useState<string>("");
  const [assignSubmitting, setAssignSubmitting] = useState<boolean>(false);

  // Bulk Import Modal
  const [importModalOpen, setImportModalOpen] = useState<boolean>(false);
  const [importFile, setImportFile] = useState<File | null>(null);
  const [importSubmitting, setImportSubmitting] = useState<boolean>(false);
  const [importResult, setImportResult] = useState<{
    total_rows: number;
    created: number;
    updated: number;
    failed: number;
    errors: Array<{ row: number; error: string }>;
  } | null>(null);

  // Product Detail Drawer
  const [drawerProduct, setDrawerProduct] = useState<Product | null>(null);
  const [drawerLoading, setDrawerLoading] = useState<boolean>(false);

  // Lookups
  const categories = useLookup<ProductCategory>("/masters/product-categories", 250);
  const subCategories = useLookup<ProductSubCategory>("/masters/product-sub-categories", 500);
  const brands = useLookup<Brand>("/masters/brands", 250);
  const uoms = useLookup<Uom>("/masters/uom", 100);
  const hsnCodes = useLookup<Hsn>("/masters/hsn", 250);

  const [allSuppliers, setAllSuppliers] = useState<SupplierLookupItem[]>([]);

  // Load active suppliers list for dropdowns via fast lightweight lookup
  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const { data } = await apiGet<SupplierLookupItem[]>("/inventory/product-prices/suppliers-lookup");
        if (!active) return;
        setAllSuppliers(Array.isArray(data) ? data : []);
      } catch (e) {
        console.error("Failed to load suppliers for lookup:", e);
      }
    })();
    return () => {
      active = false;
    };
  }, []);

  // Searchable supplier dropdown fetchers
  const supplierFetcher = useCallback(
    async (term: string) => {
      let list = allSuppliers;
      if (list.length === 0) {
        try {
          const { data } = await apiGet<SupplierLookupItem[]>("/inventory/product-prices/suppliers-lookup");
          list = Array.isArray(data) ? data : [];
          setAllSuppliers(list);
        } catch {
          list = [];
        }
      }
      const clean = term.trim().toLowerCase();
      const filtered = clean
        ? list.filter(
            (s) =>
              s.company_name.toLowerCase().includes(clean) ||
              (s.supplier_type && s.supplier_type.toLowerCase().includes(clean))
          )
        : list;
      return filtered.map((s) => ({
        value: s.id,
        label: `${s.company_name}${s.supplier_type ? ` (${s.supplier_type})` : ""}`,
      }));
    },
    [allSuppliers]
  );

  const supplierLabelFetcher = useCallback(
    async (id: string) => {
      if (!id) return "";
      let list = allSuppliers;
      if (list.length === 0) {
        try {
          const { data } = await apiGet<SupplierLookupItem[]>("/inventory/product-prices/suppliers-lookup");
          list = Array.isArray(data) ? data : [];
          setAllSuppliers(list);
        } catch {
          list = [];
        }
      }
      const match = list.find((s) => s.id === id);
      return match ? `${match.company_name}${match.supplier_type ? ` (${match.supplier_type})` : ""}` : id;
    },
    [allSuppliers]
  );

  // Debounce search input without firing duplicate requests on mount
  useEffect(() => {
    if (searchTerm === debouncedSearch) return;
    const timer = setTimeout(() => {
      setDebouncedSearch(searchTerm);
      setPage(1);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchTerm, debouncedSearch]);

  // Scoped subcategories
  const scopedSubCategories = useMemo(() => {
    if (!categoryFilter) return subCategories.items;
    return subCategories.items.filter((sc) => sc.category_id === categoryFilter);
  }, [categoryFilter, subCategories.items]);

  // Load Main Product Prices List
  const fetchPrices = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params: Record<string, string | number> = {
        page,
        page_size: pageSize,
        sort_by: sortBy,
        sort_dir: sortDir,
      };

      if (debouncedSearch.trim()) params.search = debouncedSearch.trim();
      if (categoryFilter) params.category_id = categoryFilter;
      if (subCategoryFilter) params.sub_category_id = subCategoryFilter;
      if (brandFilter) params.brand_id = brandFilter;
      if (pricingStatusFilter === "priced") params.has_price = "true";
      else if (pricingStatusFilter === "unpriced") params.has_price = "false";

      const url = `/inventory/product-prices${toQueryString(params)}`;
      const { data, meta } = await apiGet<ProductPriceRow[]>(url);

      setItems(data || []);
      const metaAny = meta as Record<string, any> | undefined;
      if (metaAny) {
        setTotalItems(metaAny.total_items ?? 0);
        setTotalPages(metaAny.total_pages ?? 1);
      }
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, debouncedSearch, categoryFilter, subCategoryFilter, brandFilter, pricingStatusFilter, sortBy, sortDir]);

  const handleSort = (columnKey: string) => {
    if (sortBy === columnKey) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortBy(columnKey);
      setSortDir("asc");
    }
    setPage(1);
  };

  useEffect(() => {
    fetchPrices();
  }, [fetchPrices]);

  // Load Supplier Quotes for an Expanded Row
  const loadProductSuppliers = useCallback(async (productId: string) => {
    setLoadingQuotes((prev) => ({ ...prev, [productId]: true }));
    try {
      const { data } = await apiGet<SupplierQuote[]>(`/inventory/product-prices/${productId}/suppliers`);
      const quotes = data || [];
      setSupplierQuotes((prev) => ({ ...prev, [productId]: quotes }));

      // Also keep the main row strictly synchronized with the database quotes
      if (quotes.length > 0) {
        const sorted = [...quotes].sort((a, b) => (a.unit_price ?? 999999) - (b.unit_price ?? 999999));
        const best = sorted[0];
        setItems((prev) =>
          prev.map((r) => {
            if (r.product_id === productId) {
              return {
                ...r,
                best_price: best.unit_price,
                best_currency: best.currency || r.best_currency,
                primary_supplier_id: best.supplier_id,
                primary_supplier_name: best.supplier_name,
                primary_link_id: best.link_id,
                supplier_count: quotes.length,
                has_price: best.unit_price != null,
              };
            }
            return r;
          })
        );
      }
    } catch (err) {
      console.error(`Failed to load quotes for product ${productId}:`, err);
    } finally {
      setLoadingQuotes((prev) => ({ ...prev, [productId]: false }));
    }
  }, []);

  // Hover Pre-fetching: Fetches supplier quotes into memory as soon as mouse hovers over row or button
  const prefetchProductSuppliers = useCallback(
    (productId: string, supplierCount?: number) => {
      if (supplierCount === 0) {
        setSupplierQuotes((prev) => (prev[productId] ? prev : { ...prev, [productId]: [] }));
        return;
      }
      if (supplierQuotes[productId] || loadingQuotes[productId]) return;
      loadProductSuppliers(productId);
    },
    [loadProductSuppliers, supplierQuotes, loadingQuotes]
  );

  const toggleRowExpansion = useCallback(
    (productId: string, supplierCount?: number) => {
      setExpandedRows((prev) => {
        const nextState = !prev[productId];
        if (nextState) {
          if (supplierCount === 0) {
            setSupplierQuotes((q) => (q[productId] ? q : { ...q, [productId]: [] }));
          } else if (!supplierQuotes[productId] && !loadingQuotes[productId]) {
            loadProductSuppliers(productId);
          }
        }
        return { ...prev, [productId]: nextState };
      });
    },
    [loadProductSuppliers, supplierQuotes, loadingQuotes]
  );

  // Start Inline Price Edit
  const startInlineEdit = (linkId: string, currentPrice: number | null) => {
    setEditingLinkId(linkId);
    setEditPriceInput(currentPrice != null ? String(currentPrice) : "");
  };

  const cancelInlineEdit = () => {
    setEditingLinkId(null);
    setEditPriceInput("");
  };

  // Commit Inline Price Edit with Instant Optimistic UI
  const saveInlinePrice = async (linkId: string, productId: string) => {
    const clean = editPriceInput.replace(/[^0-9.]/g, "");
    const num = parseFloat(clean);
    if (isNaN(num) || num < 0) {
      cancelInlineEdit();
      return;
    }

    // 1. INSTANT OPTIMISTIC SUB-TABLE UPDATE
    const updatedQuotes = (supplierQuotes[productId] || []).map((q) =>
      q.link_id === linkId ? { ...q, unit_price: num } : q
    );
    updatedQuotes.sort((a, b) => (a.unit_price ?? 999999) - (b.unit_price ?? 999999));
    setSupplierQuotes((prev) => ({ ...prev, [productId]: updatedQuotes }));

    // 2. INSTANT OPTIMISTIC MAIN ROW UPDATE
    const newLowest =
      updatedQuotes.length > 0
        ? updatedQuotes.reduce<number | null>(
            (min, q) => (q.unit_price != null ? (min == null || q.unit_price < min ? q.unit_price : min) : min),
            null
          )
        : num;
    const newBestQuote = updatedQuotes.find((q) => q.unit_price === newLowest);

    setItems((prev) =>
      prev.map((row) => {
        if (row.product_id === productId) {
          const isPrimary = row.primary_link_id === linkId;
          return {
            ...row,
            best_price: newLowest,
            best_currency: newBestQuote ? newBestQuote.currency : row.best_currency,
            primary_supplier_id: isPrimary ? row.primary_supplier_id : newBestQuote ? newBestQuote.supplier_id : row.primary_supplier_id,
            primary_supplier_name: isPrimary ? row.primary_supplier_name : newBestQuote ? newBestQuote.supplier_name : row.primary_supplier_name,
            has_price: true,
          };
        }
        return row;
      })
    );

    setEditingLinkId(null);
    setSuccess("Price updated successfully");
    setTimeout(() => setSuccess(null), 3000);

    setSavingLinkId(linkId);
    try {
      await apiPatch(`/inventory/product-prices/${linkId}`, { unit_price: num });
    } catch (err) {
      alert("Failed to update price: " + (err instanceof Error ? err.message : String(err)));
      loadProductSuppliers(productId);
      fetchPrices();
    } finally {
      setSavingLinkId(null);
    }
  };

  // Delete a supplier quote link with Instant Optimistic UI
  const handleDeleteQuote = async (linkId: string, productId: string, supplierName: string) => {
    if (!confirm(`Remove price quote from ${supplierName}?`)) return;

    // 1. INSTANT OPTIMISTIC SUB-TABLE REMOVAL
    const remainingQuotes = (supplierQuotes[productId] || []).filter((q) => q.link_id !== linkId);
    setSupplierQuotes((prev) => ({ ...prev, [productId]: remainingQuotes }));

    // 2. INSTANT OPTIMISTIC MAIN ROW UPDATE
    const newLowest =
      remainingQuotes.length > 0
        ? remainingQuotes.reduce<number | null>(
            (min, q) => (q.unit_price != null ? (min == null || q.unit_price < min ? q.unit_price : min) : min),
            null
          )
        : null;
    const newBestQuote = remainingQuotes.find((q) => q.unit_price === newLowest);

    setItems((prev) =>
      prev.map((row) => {
        if (row.product_id === productId) {
          return {
            ...row,
            best_price: newLowest,
            best_currency: newBestQuote ? newBestQuote.currency : row.best_currency,
            primary_supplier_id: newBestQuote ? newBestQuote.supplier_id : null,
            primary_supplier_name: newBestQuote ? newBestQuote.supplier_name : null,
            primary_link_id: newBestQuote ? newBestQuote.link_id : null,
            supplier_count: remainingQuotes.length,
            has_price: newLowest != null,
          };
        }
        return row;
      })
    );

    setSuccess(`Quote from ${supplierName} removed`);
    setTimeout(() => setSuccess(null), 3000);

    try {
      await apiDelete(`/inventory/product-prices/${linkId}`);
    } catch (err) {
      alert("Failed to remove quote: " + (err instanceof Error ? err.message : String(err)));
      loadProductSuppliers(productId);
      fetchPrices();
    }
  };

  // Quick Add Supplier Quote in Sub-table with Instant Optimistic UI
  const handleQuickAddQuote = async (productId: string) => {
    const suppId = subTableSupplierId[productId];
    const priceStr = subTablePrice[productId];
    const curr = subTableCurrency[productId] || "CNY";
    const moqStr = subTableMoq[productId];

    if (!suppId || !priceStr) {
      return;
    }
    const cleanPrice = priceStr.replace(/[^0-9.]/g, "");
    const priceNum = parseFloat(cleanPrice);
    if (isNaN(priceNum) || priceNum < 0) {
      return;
    }

    const moqVal = moqStr ? parseFloat(moqStr.replace(/[^0-9.]/g, "")) : null;
    const resolvedSuppName = allSuppliers.find((s) => s.id === suppId)?.company_name || "Supplier";

    // 1. INSTANT OPTIMISTIC SUB-TABLE UPDATE
    setSupplierQuotes((prev) => {
      const existing = prev[productId] || [];
      const idx = existing.findIndex((q) => q.supplier_id === suppId);
      const newQuote: SupplierQuote = {
        link_id: idx >= 0 ? existing[idx].link_id : `temp-${Date.now()}`,
        product_id: productId,
        supplier_id: suppId,
        supplier_name: resolvedSuppName,
        supplier_code: null,
        contact_calling_number: idx >= 0 ? existing[idx].contact_calling_number : null,
        contact_whatsapp_number: idx >= 0 ? existing[idx].contact_whatsapp_number : null,
        contact_wechat_number: idx >= 0 ? existing[idx].contact_wechat_number : null,
        city_name: idx >= 0 ? existing[idx].city_name : null,
        state_name: idx >= 0 ? existing[idx].state_name : null,
        country_name: idx >= 0 ? existing[idx].country_name : null,
        unit_price: priceNum,
        currency: curr,
        moq: moqVal,
        notes: null,
        updated_at: new Date().toISOString(),
        created_at: new Date().toISOString(),
      };
      const nextList = idx >= 0 ? existing.map((q, i) => (i === idx ? newQuote : q)) : [...existing, newQuote];
      nextList.sort((a, b) => (a.unit_price ?? 999999) - (b.unit_price ?? 999999));
      return { ...prev, [productId]: nextList };
    });

    // 2. INSTANT OPTIMISTIC MAIN ROW UPDATE
    setItems((prev) =>
      prev.map((row) => {
        if (row.product_id === productId) {
          const isNewBest = row.best_price == null || priceNum <= row.best_price;
          const wasLinked = supplierQuotes[productId]?.some((q) => q.supplier_id === suppId);
          const newCount = wasLinked ? row.supplier_count : (row.supplier_count || 0) + 1;
          return {
            ...row,
            best_price: isNewBest ? priceNum : row.best_price,
            best_currency: isNewBest ? curr : row.best_currency,
            primary_supplier_id: isNewBest ? suppId : row.primary_supplier_id,
            primary_supplier_name: isNewBest ? resolvedSuppName : row.primary_supplier_name,
            supplier_count: newCount,
            has_price: true,
          };
        }
        return row;
      })
    );

    // 3. Clear inputs immediately
    setSubTableSupplierId((prev) => ({ ...prev, [productId]: "" }));
    setSubTablePrice((prev) => ({ ...prev, [productId]: "" }));
    setSubTableMoq((prev) => ({ ...prev, [productId]: "" }));
    setSuccess("Supplier quote added successfully");
    setTimeout(() => setSuccess(null), 3000);

    // 4. Background Sync with Server
    setSubTableSaving((prev) => ({ ...prev, [productId]: true }));
    try {
      const res = await apiPost<{ link_id: string }>("/inventory/product-prices/assign", {
        product_id: productId,
        supplier_id: suppId,
        unit_price: priceNum,
        currency: curr,
        moq: moqVal,
      });
      if (res.data?.link_id) {
        setItems((prev) =>
          prev.map((r) =>
            r.product_id === productId && (!r.primary_link_id || priceNum <= (r.best_price ?? 999999))
              ? { ...r, primary_link_id: res.data!.link_id, has_price: true }
              : r
          )
        );
      }
      loadProductSuppliers(productId);
    } catch (err) {
      alert("Failed to add supplier quote: " + (err instanceof Error ? err.message : String(err)));
      fetchPrices();
    } finally {
      setSubTableSaving((prev) => ({ ...prev, [productId]: false }));
    }
  };

  // Open Modal: Add / Assign Supplier & Price Quote
  const openAssignModal = (row: ProductPriceRow) => {
    setAssignModalProduct(row);
    setAssignSupplierId("");
    setAssignUnitPrice("");
    setAssignCurrency(row.best_currency || "CNY");
    setAssignMoq("");
    setAssignNotes("");
    if ((row.supplier_count || 0) > 0 && !supplierQuotes[row.product_id]) {
      loadProductSuppliers(row.product_id);
    }
  };

  const closeAssignModal = () => {
    setAssignModalProduct(null);
    setAssignSubmitting(false);
  };

  // Save Supplier Quote from Modal with Instant Optimistic UI
  const handleSaveAssignModal = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!assignModalProduct) return;
    if (!assignSupplierId) {
      alert("Please select a supplier");
      return;
    }
    const cleanPrice = assignUnitPrice.replace(/[^0-9.]/g, "");
    const priceVal = parseFloat(cleanPrice);
    if (isNaN(priceVal) || priceVal < 0) {
      alert("Please enter a valid unit price (>= 0)");
      return;
    }
    setAssignSubmitting(true);

    const productId = assignModalProduct.product_id;
    const suppId = assignSupplierId;
    const curr = assignCurrency;
    const moqVal = assignMoq ? parseFloat(assignMoq.replace(/[^0-9.]/g, "")) : null;
    const notesVal = assignNotes.trim() || null;
    const resolvedSuppName =
      allSuppliers.find((s) => s.id === suppId)?.company_name ||
      assignModalProduct.primary_supplier_name ||
      "Supplier";

    // 1. INSTANT OPTIMISTIC MAIN ROW UPDATE
    setItems((prev) =>
      prev.map((row) => {
        if (row.product_id === productId) {
          const isNewBest = row.best_price == null || priceVal <= row.best_price;
          const wasLinked = supplierQuotes[productId]?.some((q) => q.supplier_id === suppId);
          const newCount = wasLinked ? row.supplier_count : (row.supplier_count || 0) + 1;
          return {
            ...row,
            best_price: isNewBest ? priceVal : row.best_price,
            best_currency: isNewBest ? curr : row.best_currency,
            primary_supplier_id: isNewBest ? suppId : row.primary_supplier_id,
            primary_supplier_name: isNewBest ? resolvedSuppName : row.primary_supplier_name,
            supplier_count: newCount,
            has_price: true,
          };
        }
        return row;
      })
    );

    // 2. INSTANT OPTIMISTIC SUB-TABLE UPDATE (if quotes were already opened)
    setSupplierQuotes((prev) => {
      const existing = prev[productId];
      if (!existing) return prev;
      const idx = existing.findIndex((q) => q.supplier_id === suppId);
      const newQuote: SupplierQuote = {
        link_id: idx >= 0 ? existing[idx].link_id : `temp-${Date.now()}`,
        product_id: productId,
        supplier_id: suppId,
        supplier_name: resolvedSuppName,
        supplier_code: null,
        contact_calling_number: idx >= 0 ? existing[idx].contact_calling_number : null,
        contact_whatsapp_number: idx >= 0 ? existing[idx].contact_whatsapp_number : null,
        contact_wechat_number: idx >= 0 ? existing[idx].contact_wechat_number : null,
        city_name: idx >= 0 ? existing[idx].city_name : null,
        state_name: idx >= 0 ? existing[idx].state_name : null,
        country_name: idx >= 0 ? existing[idx].country_name : null,
        unit_price: priceVal,
        currency: curr,
        moq: moqVal,
        notes: notesVal,
        updated_at: new Date().toISOString(),
        created_at: idx >= 0 ? existing[idx].created_at : new Date().toISOString(),
      };
      const nextList = idx >= 0 ? existing.map((q, i) => (i === idx ? newQuote : q)) : [...existing, newQuote];
      nextList.sort((a, b) => (a.unit_price ?? 999999) - (b.unit_price ?? 999999));
      return { ...prev, [productId]: nextList };
    });

    // 3. INSTANT CLOSE & SUCCESS NOTIFICATION
    closeAssignModal();
    setSuccess("Supplier and price assigned successfully");
    setTimeout(() => setSuccess(null), 3000);

    // 4. Background Sync with Server
    try {
      const res = await apiPost<{ link_id: string }>("/inventory/product-prices/assign", {
        product_id: productId,
        supplier_id: suppId,
        unit_price: priceVal,
        currency: curr,
        moq: moqVal,
        notes: notesVal,
      });
      if (res.data?.link_id) {
        setItems((prev) =>
          prev.map((r) =>
            r.product_id === productId && (!r.primary_link_id || priceVal <= (r.best_price ?? 999999))
              ? { ...r, primary_link_id: res.data!.link_id, has_price: true }
              : r
          )
        );
      }
      loadProductSuppliers(productId);
    } catch (err) {
      alert("Failed to assign supplier: " + (err instanceof Error ? err.message : String(err)));
      fetchPrices();
    } finally {
      setAssignSubmitting(false);
    }
  };

  // Open Product Detail Drawer
  const openProductDrawer = async (productId: string) => {
    setDrawerLoading(true);
    try {
      const { data } = await apiGet<Product>(`/masters/products/${productId}`);
      setDrawerProduct(data);
    } catch (err) {
      console.error("Failed to load product details:", err);
    } finally {
      setDrawerLoading(false);
    }
  };

  const closeProductDrawer = () => {
    setDrawerProduct(null);
  };

  // Export
  const handleExport = (format: "xlsx" | "csv") => {
    window.open(`${API_ORIGIN}/api/v1/inventory/product-prices/export?format=${format}`, "_blank");
  };

  // Bulk Import
  const handleImportSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!importFile) return;

    setImportSubmitting(true);
    setImportResult(null);

    const formData = new FormData();
    formData.append("file", importFile);

    try {
      const { data } = await apiPostMultipart<any>("/inventory/product-prices/import", formData);
      setImportResult(data);
      setSuccess(`Import completed: ${data.created} created, ${data.updated} updated, ${data.failed} failed.`);
      fetchPrices();
    } catch (err) {
      alert("Import failed: " + (err instanceof Error ? err.message : String(err)));
    } finally {
      setImportSubmitting(false);
    }
  };

  return (
    <AppShell activeKey="product-prices">
      <main className="page">
        <Breadcrumb trail={["Inventory", "Product Prices"]} />

        {/* Page Header */}
        <div className="page-header" style={{ marginBottom: "20px", display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "16px" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <h1 style={{ margin: 0 }}>Product Price Directory</h1>
              <span className="badge badge-info" style={{ fontSize: "12px", padding: "4px 8px" }}>
                {totalItems} Products
              </span>
            </div>
            <div className="page-subtitle" style={{ marginTop: "4px" }}>
              Search, compare, and inline-edit supplier purchase prices across all catalog items.
            </div>
          </div>

          {/* Action Toolbar */}
          <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => handleExport("xlsx")}
              title="Export complete pricing directory to Excel"
            >
              📊 Export Excel
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => handleExport("csv")}
              title="Export complete pricing directory to CSV"
            >
              📄 Export CSV
            </button>
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => {
                setImportModalOpen(true);
                setImportResult(null);
                setImportFile(null);
              }}
            >
              📥 Bulk Import Prices
            </button>
            <button
              type="button"
              className="btn btn-small"
              onClick={fetchPrices}
              title="Refresh table data"
            >
              🔄 Refresh
            </button>
          </div>
        </div>

        <Banner error={error} success={success} />

        {/* Filters Card */}
        <div
          className="card"
          style={{
            marginBottom: "20px",
            padding: "16px 20px",
            background: "#ffffff",
            borderRadius: "8px",
            border: "1px solid #e2e8f0",
            boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
          }}
        >
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
              gap: "14px",
              alignItems: "flex-end",
            }}
          >
            {/* Search Input */}
            <div style={{ display: "flex", flexDirection: "column", gap: "6px", gridColumn: "span 2" }}>
              <label style={{ fontSize: "12.5px", fontWeight: 600, color: "#334155" }}>
                Search Catalog
              </label>
              <div style={{ position: "relative" }}>
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Search code, name, barcode, or supplier..."
                  style={{
                    width: "100%",
                    padding: "9px 12px 9px 34px",
                    borderRadius: "6px",
                    border: "1px solid #cbd5e1",
                    fontSize: "13.5px",
                    outline: "none",
                  }}
                />
                <span
                  style={{
                    position: "absolute",
                    left: "10px",
                    top: "50%",
                    transform: "translateY(-50%)",
                    color: "#94a3b8",
                    fontSize: "14px",
                  }}
                >
                  🔍
                </span>
                {searchTerm && (
                  <button
                    type="button"
                    onClick={() => setSearchTerm("")}
                    style={{
                      position: "absolute",
                      right: "10px",
                      top: "50%",
                      transform: "translateY(-50%)",
                      background: "transparent",
                      border: "none",
                      cursor: "pointer",
                      color: "#94a3b8",
                      fontSize: "14px",
                    }}
                  >
                    ✕
                  </button>
                )}
              </div>
            </div>

            {/* Category Filter */}
            <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
              <label style={{ fontSize: "12.5px", fontWeight: 600, color: "#334155" }}>Category</label>
              <select
                value={categoryFilter}
                onChange={(e) => {
                  setCategoryFilter(e.target.value);
                  setSubCategoryFilter("");
                  setPage(1);
                }}
                style={{
                  padding: "9px 12px",
                  borderRadius: "6px",
                  border: "1px solid #cbd5e1",
                  fontSize: "13.5px",
                  background: "#fff",
                }}
              >
                <option value="">All Categories</option>
                {categories.items.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Sub Category Filter */}
            <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
              <label style={{ fontSize: "12.5px", fontWeight: 600, color: "#334155" }}>Sub-Category</label>
              <select
                value={subCategoryFilter}
                onChange={(e) => {
                  setSubCategoryFilter(e.target.value);
                  setPage(1);
                }}
                style={{
                  padding: "9px 12px",
                  borderRadius: "6px",
                  border: "1px solid #cbd5e1",
                  fontSize: "13.5px",
                  background: "#fff",
                }}
              >
                <option value="">All Sub-Categories</option>
                {scopedSubCategories.map((sc) => (
                  <option key={sc.id} value={sc.id}>
                    {sc.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Brand Filter */}
            <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
              <label style={{ fontSize: "12.5px", fontWeight: 600, color: "#334155" }}>Brand</label>
              <select
                value={brandFilter}
                onChange={(e) => {
                  setBrandFilter(e.target.value);
                  setPage(1);
                }}
                style={{
                  padding: "9px 12px",
                  borderRadius: "6px",
                  border: "1px solid #cbd5e1",
                  fontSize: "13.5px",
                  background: "#fff",
                }}
              >
                <option value="">All Brands</option>
                {brands.items.map((b) => (
                  <option key={b.id} value={b.id}>
                    {b.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Price Status Filter */}
            <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
              <label style={{ fontSize: "12.5px", fontWeight: 600, color: "#334155" }}>Pricing Status</label>
              <select
                value={pricingStatusFilter}
                onChange={(e) => {
                  setPricingStatusFilter(e.target.value as any);
                  setPage(1);
                }}
                style={{
                  padding: "9px 12px",
                  borderRadius: "6px",
                  border: "1px solid #cbd5e1",
                  fontSize: "13.5px",
                  background: "#fff",
                }}
              >
                <option value="all">All Items</option>
                <option value="priced">Priced Items Only</option>
                <option value="unpriced">Unpriced Items Only</option>
              </select>
            </div>
          </div>
        </div>

        {/* Main Product Table */}
        <div
          className="card"
          style={{
            background: "#ffffff",
            borderRadius: "8px",
            border: "1px solid #e2e8f0",
            overflow: "hidden",
            boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
          }}
        >
          <div style={{ overflowX: "auto" }}>
            <table className="table" style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr style={{ background: "#f8fafc", borderBottom: "2px solid #e2e8f0", textAlign: "left" }}>
                  <th style={{ padding: "12px 14px", width: "70px", minWidth: "70px", textAlign: "center", color: "#475569", whiteSpace: "nowrap" }}>
                    Sr. No.
                  </th>
                  <th
                    onClick={() => handleSort("product_name_tally")}
                    style={{ padding: "12px 14px", color: "#475569", minWidth: "260px", cursor: "pointer", userSelect: "none" }}
                    title="Click to sort by Product Name"
                  >
                    Product Name &amp; Code {sortBy === "product_name_tally" ? (sortDir === "asc" ? "▲" : "▼") : "↕"}
                  </th>
                  <th style={{ padding: "12px 14px", color: "#475569", width: "160px" }}>Category &amp; Brand</th>
                  <th
                    onClick={() => handleSort("best_price")}
                    style={{ padding: "12px 14px", color: "#475569", width: "150px", cursor: "pointer", userSelect: "none" }}
                    title="Click to sort by Best Price"
                  >
                    Best Price (Quote) {sortBy === "best_price" ? (sortDir === "asc" ? "▲" : "▼") : "↕"}
                  </th>
                  <th style={{ padding: "12px 14px", color: "#475569", minWidth: "220px" }}>Primary Supplier</th>
                  <th style={{ padding: "12px 14px", color: "#475569", width: "150px", textAlign: "center" }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan={6} style={{ padding: "40px", textAlign: "center", color: "#64748b" }}>
                      <div style={{ fontSize: "16px", marginBottom: "8px" }}>⏳ Loading product prices...</div>
                      <div style={{ fontSize: "12px", color: "#94a3b8" }}>Searching through catalog items...</div>
                    </td>
                  </tr>
                ) : items.length === 0 ? (
                  <tr>
                    <td colSpan={6} style={{ padding: "40px", textAlign: "center", color: "#64748b" }}>
                      <div style={{ fontSize: "16px", marginBottom: "4px" }}>No products found</div>
                      <div style={{ fontSize: "13px", color: "#94a3b8" }}>
                        Try clearing search or changing the pricing status filter.
                      </div>
                    </td>
                  </tr>
                ) : (
                  items.map((row, idx) => {
                    const srNo = (page - 1) * pageSize + idx + 1;
                    const isExpanded = Boolean(expandedRows[row.product_id]);
                    const isEditingBestPrice = editingLinkId === row.primary_link_id;
                    const isSavingBestPrice = savingLinkId === row.primary_link_id;
                    const quotes = supplierQuotes[row.product_id] || [];
                    const isLoadingQuotes = loadingQuotes[row.product_id];

                    return (
                      <Fragment key={row.product_id}>
                        {/* Main Product Row with Hover Pre-fetching */}
                        <tr
                          onMouseEnter={() => prefetchProductSuppliers(row.product_id, row.supplier_count)}
                          style={{
                            background: isExpanded ? "#f1f5f9" : idx % 2 === 0 ? "#ffffff" : "#fafafa",
                            borderBottom: isExpanded ? "none" : "1px solid #e2e8f0",
                            transition: "background 0.15s ease",
                          }}
                        >
                          {/* Sr No */}
                          <td style={{ padding: "12px 14px", textAlign: "center", fontWeight: 600, color: "#64748b", fontSize: "13px" }}>
                            {srNo}
                          </td>

                          {/* Product Name & Code */}
                          <td style={{ padding: "12px 14px" }}>
                            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                              {/* Photo thumbnail */}
                              <div
                                style={{
                                  width: "40px",
                                  height: "40px",
                                  borderRadius: "6px",
                                  background: "#f1f5f9",
                                  border: "1px solid #e2e8f0",
                                  display: "flex",
                                  alignItems: "center",
                                  justifyContent: "center",
                                  overflow: "hidden",
                                  flexShrink: 0,
                                }}
                              >
                                {row.images && row.images.length > 0 ? (
                                  <img
                                    src={resolveImageUrl(row.images[0])}
                                    alt="Thumb"
                                    style={{ width: "100%", height: "100%", objectFit: "cover" }}
                                  />
                                ) : (
                                  <span style={{ fontSize: "18px", color: "#94a3b8" }}>📦</span>
                                )}
                              </div>

                              <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
                                <button
                                  type="button"
                                  onClick={() => openProductDrawer(row.product_id)}
                                  style={{
                                    background: "none",
                                    border: "none",
                                    padding: 0,
                                    color: "var(--color-primary, #2563eb)",
                                    fontSize: "14px",
                                    fontWeight: 700,
                                    cursor: "pointer",
                                    textAlign: "left",
                                    lineHeight: "1.3",
                                  }}
                                  title="Click to view product specifications"
                                >
                                  {row.product_name_tally || row.product_name}
                                </button>

                                <div style={{ display: "flex", alignItems: "center", gap: "6px", flexWrap: "wrap" }}>
                                  {row.product_code && (
                                    <span
                                      style={{
                                        fontSize: "11px",
                                        fontFamily: "monospace",
                                        background: "#e2e8f0",
                                        padding: "1px 5px",
                                        borderRadius: "4px",
                                        color: "#334155",
                                        fontWeight: 600,
                                      }}
                                    >
                                      {row.product_code}
                                    </span>
                                  )}
                                  {row.barcode && (
                                    <span style={{ fontSize: "11px", color: "#64748b" }}>
                                      Barcode: {row.barcode}
                                    </span>
                                  )}
                                </div>
                              </div>
                            </div>
                          </td>

                          {/* Category & Brand */}
                          <td style={{ padding: "12px 14px", fontSize: "13px" }}>
                            <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
                              <span style={{ fontWeight: 600, color: "#334155" }}>
                                {row.category_name || "—"}
                              </span>
                              <div style={{ display: "flex", alignItems: "center", gap: "4px", fontSize: "11.5px", color: "#64748b" }}>
                                <span>{row.brand_name || "Yinglima"}</span>
                                {row.uom_code && <span>• ({row.uom_code})</span>}
                              </div>
                            </div>
                          </td>

                          {/* Best Price (Inline Editable) */}
                          <td style={{ padding: "12px 14px" }}>
                            {row.has_price || row.best_price != null ? (
                              isEditingBestPrice ? (
                                <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                                  <span style={{ fontSize: "13px", fontWeight: 700, color: "#16a34a" }}>
                                    {row.best_currency === "USD" ? "$" : "¥"}
                                  </span>
                                  <input
                                    type="number"
                                    step="0.01"
                                    value={editPriceInput}
                                    onChange={(e) => setEditPriceInput(e.target.value)}
                                    autoFocus
                                    onKeyDown={(e) => {
                                      if (e.key === "Enter") saveInlinePrice(row.primary_link_id!, row.product_id);
                                      if (e.key === "Escape") cancelInlineEdit();
                                    }}
                                    disabled={isSavingBestPrice}
                                    style={{
                                      width: "80px",
                                      padding: "4px 6px",
                                      fontSize: "13px",
                                      fontWeight: 700,
                                      borderRadius: "4px",
                                      border: "1px solid #16a34a",
                                    }}
                                  />
                                  <button
                                    type="button"
                                    onClick={() => saveInlinePrice(row.primary_link_id!, row.product_id)}
                                    disabled={isSavingBestPrice}
                                    style={{
                                      background: "#16a34a",
                                      color: "#fff",
                                      border: "none",
                                      borderRadius: "4px",
                                      padding: "3px 6px",
                                      cursor: "pointer",
                                      fontSize: "11px",
                                    }}
                                    title="Save price (Enter)"
                                  >
                                    ✓
                                  </button>
                                  <button
                                    type="button"
                                    onClick={cancelInlineEdit}
                                    style={{
                                      background: "#e2e8f0",
                                      color: "#334155",
                                      border: "none",
                                      borderRadius: "4px",
                                      padding: "3px 6px",
                                      cursor: "pointer",
                                      fontSize: "11px",
                                    }}
                                    title="Cancel (Esc)"
                                  >
                                    ✕
                                  </button>
                                </div>
                              ) : (
                                <div
                                  onClick={() => row.primary_link_id ? startInlineEdit(row.primary_link_id, row.best_price) : openAssignModal(row)}
                                  style={{
                                    display: "inline-flex",
                                    alignItems: "center",
                                    gap: "6px",
                                    padding: "4px 8px",
                                    background: "#dcfce7",
                                    border: "1px solid #86efac",
                                    borderRadius: "6px",
                                    color: "#15803d",
                                    fontWeight: 700,
                                    fontSize: "13.5px",
                                    cursor: "pointer",
                                  }}
                                  title="Click to inline-edit best price"
                                >
                                  <span>{formatCurrency(row.best_price, row.best_currency || "CNY")}</span>
                                  <span style={{ fontSize: "11px", opacity: 0.7 }}>✏️</span>
                                </div>
                              )
                            ) : (
                              <button
                                type="button"
                                onClick={() => openAssignModal(row)}
                                style={{
                                  padding: "4px 8px",
                                  background: "#fffbeb",
                                  border: "1px dashed #f59e0b",
                                  borderRadius: "6px",
                                  color: "#b45309",
                                  fontSize: "12px",
                                  fontWeight: 600,
                                  cursor: "pointer",
                                }}
                              >
                                + Add Price
                              </button>
                            )}
                          </td>

                          {/* Primary Supplier & Expand Badge */}
                          <td style={{ padding: "12px 14px", fontSize: "13px" }}>
                            {row.primary_supplier_name ? (
                              <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                                <span style={{ fontWeight: 600, color: "#1e293b" }}>
                                  {row.primary_supplier_name}
                                </span>
                                <div>
                                  <button
                                    type="button"
                                    onClick={() => toggleRowExpansion(row.product_id, row.supplier_count)}
                                    onMouseEnter={() => prefetchProductSuppliers(row.product_id, row.supplier_count)}
                                    style={{
                                      background: isExpanded ? "#2563eb" : "#f1f5f9",
                                      color: isExpanded ? "#ffffff" : "#2563eb",
                                      border: "1px solid",
                                      borderColor: isExpanded ? "#2563eb" : "#cbd5e1",
                                      borderRadius: "12px",
                                      padding: "2px 8px",
                                      fontSize: "11.5px",
                                      fontWeight: 600,
                                      cursor: "pointer",
                                      display: "inline-flex",
                                      alignItems: "center",
                                      gap: "4px",
                                    }}
                                  >
                                    <span>
                                      {row.supplier_count} {row.supplier_count === 1 ? "Supplier" : "Suppliers"}
                                    </span>
                                    <span>{isExpanded ? "▲" : "▼"}</span>
                                  </button>
                                </div>
                              </div>
                            ) : (
                              <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                                <span style={{ color: "#94a3b8" }}>—</span>
                                <button
                                  type="button"
                                  onClick={() => openAssignModal(row)}
                                  onMouseEnter={() => prefetchProductSuppliers(row.product_id, row.supplier_count)}
                                  className="btn btn-tiny btn-outline"
                                  style={{ fontSize: "11px", padding: "2px 6px" }}
                                >
                                  + Assign
                                </button>
                              </div>
                            )}
                          </td>

                          {/* Row Actions */}
                          <td style={{ padding: "12px 14px", textAlign: "center" }}>
                            <div style={{ display: "inline-flex", alignItems: "center", justifyContent: "center", gap: "6px" }}>
                              <button
                                type="button"
                                onClick={() => openAssignModal(row)}
                                onMouseEnter={() => prefetchProductSuppliers(row.product_id, row.supplier_count)}
                                className="btn btn-small btn-secondary"
                                style={{ fontSize: "12px", padding: "4px 8px" }}
                                title="Add another supplier quote for this product"
                              >
                                + Quote
                              </button>
                              <button
                                type="button"
                                onClick={() => toggleRowExpansion(row.product_id, row.supplier_count)}
                                onMouseEnter={() => prefetchProductSuppliers(row.product_id, row.supplier_count)}
                                className="btn btn-small"
                                style={{
                                  fontSize: "12px",
                                  padding: "4px 8px",
                                  background: isExpanded ? "#e2e8f0" : "#ffffff",
                                }}
                                title="Toggle supplier quotes comparison table"
                              >
                                {isExpanded ? "Close ▴" : "Compare ▾"}
                              </button>
                            </div>
                          </td>
                        </tr>

                        {/* Option 1 Accordion Sub-Table */}
                        {isExpanded && (
                          <tr style={{ background: "#f8fafc", borderBottom: "1px solid #e2e8f0" }}>
                            <td colSpan={6} style={{ padding: "16px 20px" }}>
                              <div
                                style={{
                                  background: "#ffffff",
                                  borderRadius: "8px",
                                  border: "1px solid #cbd5e1",
                                  padding: "16px",
                                  boxShadow: "0 2px 4px rgba(0,0,0,0.04)",
                                }}
                              >
                                <div
                                  style={{
                                    display: "flex",
                                    justifyContent: "space-between",
                                    alignItems: "center",
                                    marginBottom: "12px",
                                    borderBottom: "1px solid #e2e8f0",
                                    paddingBottom: "8px",
                                  }}
                                >
                                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                                    <span style={{ fontSize: "15px" }}>🏭</span>
                                    <strong style={{ fontSize: "14px", color: "#1e293b" }}>
                                      Supplier Quotations &amp; Comparison ({quotes.length} Quotes)
                                    </strong>
                                  </div>
                                  <button
                                    type="button"
                                    className="btn btn-tiny btn-secondary"
                                    onClick={() => loadProductSuppliers(row.product_id)}
                                  >
                                    🔄 Refresh Quotes
                                  </button>
                                </div>

                                {isLoadingQuotes ? (
                                  <div style={{ padding: "20px", textAlign: "center", color: "#64748b" }}>
                                    Loading supplier quotations...
                                  </div>
                                ) : quotes.length === 0 ? (
                                  <div style={{ padding: "16px", textAlign: "center", color: "#64748b" }}>
                                    No suppliers quoted this product yet. Add the first quote below.
                                  </div>
                                ) : (
                                  <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px", marginBottom: "16px" }}>
                                    <thead>
                                      <tr style={{ background: "#f1f5f9", textAlign: "left", color: "#475569" }}>
                                        <th style={{ padding: "8px 10px" }}>Supplier Name</th>
                                        <th style={{ padding: "8px 10px" }}>Location</th>
                                        <th style={{ padding: "8px 10px" }}>Quoted Price</th>
                                        <th style={{ padding: "8px 10px" }}>Currency</th>
                                        <th style={{ padding: "8px 10px" }}>MOQ</th>
                                        <th style={{ padding: "8px 10px" }}>Notes / Terms</th>
                                        <th style={{ padding: "8px 10px" }}>Updated</th>
                                        <th style={{ padding: "8px 10px", textAlign: "center" }}>Actions</th>
                                      </tr>
                                    </thead>
                                    <tbody>
                                      {quotes.map((q) => {
                                        const isSubEditing = editingLinkId === q.link_id;
                                        const isSubSaving = savingLinkId === q.link_id;
                                        const isLowest = q.unit_price != null && row.best_price != null && q.unit_price <= row.best_price;

                                        return (
                                          <tr
                                            key={q.link_id}
                                            style={{
                                              borderBottom: "1px solid #f1f5f9",
                                              background: isLowest ? "#f0fdf4" : "#ffffff",
                                            }}
                                          >
                                            {/* Supplier Name */}
                                            <td style={{ padding: "8px 10px", fontWeight: 600 }}>
                                              <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                                                <span>{q.supplier_name}</span>
                                                {isLowest && (
                                                  <span
                                                    style={{
                                                      fontSize: "10px",
                                                      background: "#16a34a",
                                                      color: "#fff",
                                                      padding: "1px 5px",
                                                      borderRadius: "10px",
                                                      fontWeight: 700,
                                                    }}
                                                  >
                                                    BEST
                                                  </span>
                                                )}
                                              </div>
                                              <div style={{ fontSize: "11px", color: "#64748b", fontWeight: 400 }}>
                                                {q.contact_calling_number && `📞 ${q.contact_calling_number}`}
                                                {q.contact_wechat_number && ` • 💬 WeChat: ${q.contact_wechat_number}`}
                                              </div>
                                            </td>

                                            {/* Location */}
                                            <td style={{ padding: "8px 10px", color: "#64748b" }}>
                                              {[q.city_name, q.state_name, q.country_name].filter(Boolean).join(", ") || "—"}
                                            </td>

                                            {/* Unit Price (Inline Editable) */}
                                            <td style={{ padding: "8px 10px" }}>
                                              {isSubEditing ? (
                                                <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                                                  <input
                                                    type="number"
                                                    min="0"
                                                    step="0.01"
                                                    value={editPriceInput}
                                                    onKeyDown={(e) => {
                                                      if (e.key === "-" || e.key === "e") {
                                                        e.preventDefault();
                                                      }
                                                      if (e.key === "Enter") saveInlinePrice(q.link_id, row.product_id);
                                                      if (e.key === "Escape") cancelInlineEdit();
                                                    }}
                                                    onChange={(e) => {
                                                      const clean = e.target.value.replace(/[^0-9.]/g, "");
                                                      setEditPriceInput(clean);
                                                    }}
                                                    autoFocus
                                                    disabled={isSubSaving}
                                                    style={{
                                                      width: "75px",
                                                      padding: "3px 6px",
                                                      fontSize: "12px",
                                                      borderRadius: "4px",
                                                      border: "1px solid #16a34a",
                                                    }}
                                                  />
                                                  <button
                                                    type="button"
                                                    onClick={() => saveInlinePrice(q.link_id, row.product_id)}
                                                    disabled={isSubSaving}
                                                    style={{
                                                      background: "#16a34a",
                                                      color: "#fff",
                                                      border: "none",
                                                      borderRadius: "4px",
                                                      padding: "2px 6px",
                                                      cursor: "pointer",
                                                      fontSize: "11px",
                                                    }}
                                                  >
                                                    ✓
                                                  </button>
                                                  <button
                                                    type="button"
                                                    onClick={cancelInlineEdit}
                                                    style={{
                                                      background: "#e2e8f0",
                                                      color: "#334155",
                                                      border: "none",
                                                      borderRadius: "4px",
                                                      padding: "2px 6px",
                                                      cursor: "pointer",
                                                      fontSize: "11px",
                                                    }}
                                                  >
                                                    ✕
                                                  </button>
                                                </div>
                                              ) : (
                                                <span
                                                  onClick={() => startInlineEdit(q.link_id, q.unit_price)}
                                                  style={{
                                                    cursor: "pointer",
                                                    fontWeight: 700,
                                                    color: isLowest ? "#15803d" : "#0f172a",
                                                    borderBottom: "1px dashed #94a3b8",
                                                  }}
                                                  title="Click to inline-edit this quote"
                                                >
                                                  {formatCurrency(q.unit_price, q.currency)} ✏️
                                                </span>
                                              )}
                                            </td>

                                            {/* Currency */}
                                            <td style={{ padding: "8px 10px", fontWeight: 600, color: "#475569" }}>
                                              {q.currency || "CNY"}
                                            </td>

                                            {/* MOQ */}
                                            <td style={{ padding: "8px 10px", color: "#475569" }}>
                                              {q.moq != null ? `${q.moq} pcs` : "—"}
                                            </td>

                                            {/* Notes */}
                                            <td style={{ padding: "8px 10px", color: "#64748b", maxWidth: "160px" }}>
                                              {q.notes || "—"}
                                            </td>

                                            {/* Date */}
                                            <td style={{ padding: "8px 10px", color: "#64748b", fontSize: "11.5px" }}>
                                              {q.updated_at ? new Date(q.updated_at).toLocaleDateString() : "—"}
                                            </td>

                                            {/* Actions */}
                                            <td style={{ padding: "8px 10px", textAlign: "center" }}>
                                              <button
                                                type="button"
                                                onClick={() => handleDeleteQuote(q.link_id, row.product_id, q.supplier_name)}
                                                style={{
                                                  background: "transparent",
                                                  border: "none",
                                                  color: "#ef4444",
                                                  cursor: "pointer",
                                                  fontSize: "13px",
                                                }}
                                                title="Delete this supplier quote"
                                              >
                                                🗑️
                                              </button>
                                            </td>
                                          </tr>
                                        );
                                      })}
                                    </tbody>
                                  </table>
                                )}

                                {/* Inline Row: Add Another Supplier Quote */}
                                <div
                                  style={{
                                    background: "#f1f5f9",
                                    borderRadius: "6px",
                                    padding: "10px 14px",
                                    display: "flex",
                                    alignItems: "center",
                                    gap: "10px",
                                    flexWrap: "wrap",
                                  }}
                                >
                                  <span style={{ fontSize: "12px", fontWeight: 700, color: "#334155" }}>
                                    + Add Another Supplier Quote:
                                  </span>

                                  {/* Select Supplier */}
                                  <select
                                    value={subTableSupplierId[row.product_id] || ""}
                                    onChange={(e) =>
                                      setSubTableSupplierId((prev) => ({
                                        ...prev,
                                        [row.product_id]: e.target.value,
                                      }))
                                    }
                                    style={{
                                      padding: "6px 10px",
                                      borderRadius: "4px",
                                      border: "1px solid #cbd5e1",
                                      fontSize: "12.5px",
                                      background: "#fff",
                                      minWidth: "180px",
                                    }}
                                  >
                                    <option value="">Select Supplier...</option>
                                    {allSuppliers.map((s) => (
                                      <option key={s.id} value={s.id}>
                                        {s.company_name}
                                      </option>
                                    ))}
                                  </select>

                                  {/* Price */}
                                  <input
                                    type="number"
                                    min="0"
                                    step="0.01"
                                    placeholder="Unit Price (e.g. 120.00)"
                                    value={subTablePrice[row.product_id] || ""}
                                    onKeyDown={(e) => {
                                      if (e.key === "-" || e.key === "e") {
                                        e.preventDefault();
                                      }
                                    }}
                                    onChange={(e) => {
                                      const clean = e.target.value.replace(/[^0-9.]/g, "");
                                      setSubTablePrice((prev) => ({
                                        ...prev,
                                        [row.product_id]: clean,
                                      }));
                                    }}
                                    style={{
                                      width: "140px",
                                      padding: "6px 10px",
                                      borderRadius: "4px",
                                      border: "1px solid #cbd5e1",
                                      fontSize: "12.5px",
                                    }}
                                  />

                                  {/* Currency */}
                                  <select
                                    value={subTableCurrency[row.product_id] || "CNY"}
                                    onChange={(e) =>
                                      setSubTableCurrency((prev) => ({
                                        ...prev,
                                        [row.product_id]: e.target.value,
                                      }))
                                    }
                                    style={{
                                      padding: "6px 8px",
                                      borderRadius: "4px",
                                      border: "1px solid #cbd5e1",
                                      fontSize: "12.5px",
                                      background: "#fff",
                                    }}
                                  >
                                    <option value="CNY">CNY (¥)</option>
                                    <option value="USD">USD ($)</option>
                                    <option value="EUR">EUR (€)</option>
                                    <option value="INR">INR (₹)</option>
                                  </select>

                                  {/* MOQ */}
                                  <input
                                    type="number"
                                    min="0"
                                    placeholder="MOQ (optional)"
                                    value={subTableMoq[row.product_id] || ""}
                                    onKeyDown={(e) => {
                                      if (e.key === "-" || e.key === "e") {
                                        e.preventDefault();
                                      }
                                    }}
                                    onChange={(e) => {
                                      const clean = e.target.value.replace(/[^0-9.]/g, "");
                                      setSubTableMoq((prev) => ({
                                        ...prev,
                                        [row.product_id]: clean,
                                      }));
                                    }}
                                    style={{
                                      width: "110px",
                                      padding: "6px 10px",
                                      borderRadius: "4px",
                                      border: "1px solid #cbd5e1",
                                      fontSize: "12.5px",
                                    }}
                                  />

                                  <button
                                    type="button"
                                    className="btn btn-primary"
                                    disabled={subTableSaving[row.product_id]}
                                    onClick={() => handleQuickAddQuote(row.product_id)}
                                    style={{ fontSize: "12px", padding: "6px 12px" }}
                                  >
                                    {subTableSaving[row.product_id] ? "Saving..." : "Save Quote"}
                                  </button>
                                </div>
                              </div>
                            </td>
                          </tr>
                        )}
                      </Fragment>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div style={{ padding: "12px 20px" }}>
            <Pagination
              pagination={{
                current_page: page,
                total_pages: totalPages,
                total_items: totalItems,
                page_size: pageSize,
              }}
              pageSize={pageSize}
              onPageChange={(p) => setPage(p)}
              onPageSizeChange={(sz) => {
                setPageSize(sz);
                setPage(1);
              }}
            />
          </div>
        </div>

        {/* Modal: Assign / Add Supplier Quote */}
        {assignModalProduct && (() => {
          const hasExisting = (assignModalProduct.supplier_count || 0) > 0 || assignModalProduct.best_price != null;
          const productQuotes = supplierQuotes[assignModalProduct.product_id] || [];
          const matchedQuote = assignSupplierId ? productQuotes.find((q) => q.supplier_id === assignSupplierId) : undefined;

          return (
            <Modal
              open={true}
              title={hasExisting ? "+ Add New Supplier Quotation" : "Assign Supplier & Price Quote"}
              variant="center"
              cardClassName="modal-overflow-visible"
              cardStyle={{ maxWidth: "540px", width: "95%", overflow: "visible" }}
              onClose={closeAssignModal}
            >
              <form
                onSubmit={handleSaveAssignModal}
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "16px",
                  padding: "20px 24px",
                  overflow: "visible",
                }}
              >
                {/* Product Info Banner */}
                <div
                  style={{
                    background: "#eff6ff",
                    border: "1px solid #bfdbfe",
                    borderRadius: "6px",
                    padding: "12px",
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                  }}
                >
                  <span style={{ fontSize: "20px" }}>📦</span>
                  <div>
                    <div style={{ fontWeight: 700, color: "#1e3a8a", fontSize: "14px" }}>
                      {assignModalProduct.product_name_tally || assignModalProduct.product_name}
                    </div>
                    <div style={{ fontSize: "12px", color: "#3b82f6" }}>
                      Code: {assignModalProduct.product_code || "—"} • Category: {assignModalProduct.category_name || "—"}
                    </div>
                  </div>
                </div>

                {/* Current Lowest Benchmark Banner (if product already has quotes) */}
                {hasExisting && (
                  <div
                    style={{
                      background: "#f0fdf4",
                      border: "1px solid #86efac",
                      borderRadius: "6px",
                      padding: "10px 14px",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      gap: "10px",
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                      <span style={{ fontSize: "16px" }}>🏷️</span>
                      <div>
                        <div style={{ fontSize: "11px", color: "#15803d", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.5px" }}>
                          Current Lowest Benchmark:
                        </div>
                        <div style={{ fontSize: "14px", fontWeight: 700, color: "#166534" }}>
                          {formatCurrency(assignModalProduct.best_price, assignModalProduct.best_currency || "CNY")}
                          {assignModalProduct.primary_supplier_name && (
                            <span style={{ fontWeight: 500, fontSize: "12px", color: "#15803d", marginLeft: "6px" }}>
                              (via {assignModalProduct.primary_supplier_name})
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    <div
                      style={{
                        background: "#dcfce7",
                        color: "#166534",
                        fontSize: "11.5px",
                        fontWeight: 700,
                        padding: "3px 10px",
                        borderRadius: "12px",
                        border: "1px solid #bbf7d0",
                        whiteSpace: "nowrap",
                      }}
                    >
                      {assignModalProduct.supplier_count || 1} {(assignModalProduct.supplier_count || 1) === 1 ? "Quote on file" : "Quotes on file"}
                    </div>
                  </div>
                )}

                {/* Supplier Selection (Type to search dropdown) */}
                <div style={{ display: "flex", flexDirection: "column", gap: "6px", position: "relative", zIndex: 100 }}>
                  <label style={{ fontSize: "13px", fontWeight: 600, color: "#334155" }}>
                    Select Supplier <span style={{ color: "#ef4444" }}>*</span>
                  </label>
                  <SearchableDropdown
                    value={assignSupplierId || null}
                    onChange={(val) => setAssignSupplierId(val || "")}
                    placeholder="Type to search supplier (e.g. Yinglima, Darsh)..."
                    fetchOptions={supplierFetcher}
                    fetchLabelForValue={supplierLabelFetcher}
                    hasError={assignSubmitting && !assignSupplierId}
                  />
                  {matchedQuote && (
                    <div style={{ fontSize: "12px", color: "#b45309", background: "#fef3c7", padding: "6px 10px", borderRadius: "4px", border: "1px solid #fde68a", marginTop: "2px" }}>
                      ℹ️ <strong>{matchedQuote.supplier_name}</strong> already has a quote on file (
                      {formatCurrency(matchedQuote.unit_price, matchedQuote.currency)}). Entering a new price will update their quotation.
                    </div>
                  )}
                  {assignSubmitting && !assignSupplierId && (
                    <span style={{ fontSize: "12px", color: "#ef4444" }}>Please select a supplier.</span>
                  )}
                </div>

                {/* Price & Currency */}
                <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: "12px", position: "relative", zIndex: 10 }}>
                  <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                    <label style={{ fontSize: "13px", fontWeight: 600, color: "#334155" }}>
                      Unit Price <span style={{ color: "#ef4444" }}>*</span>
                    </label>
                    <input
                      type="number"
                      min="0"
                      step="0.01"
                      required
                      placeholder="e.g. 125.00"
                      value={assignUnitPrice}
                      onKeyDown={(e) => {
                        if (e.key === "-" || e.key === "e") {
                          e.preventDefault();
                        }
                      }}
                      onChange={(e) => {
                        const clean = e.target.value.replace(/[^0-9.]/g, "");
                        setAssignUnitPrice(clean);
                      }}
                      style={{
                        padding: "9px 12px",
                        borderRadius: "6px",
                        border:
                          assignSubmitting && (!assignUnitPrice || parseFloat(assignUnitPrice) < 0 || isNaN(parseFloat(assignUnitPrice)))
                            ? "1.5px solid #ef4444"
                            : "1px solid #cbd5e1",
                        fontSize: "13.5px",
                      }}
                    />
                    {assignSubmitting && (!assignUnitPrice || parseFloat(assignUnitPrice) < 0 || isNaN(parseFloat(assignUnitPrice))) && (
                      <span style={{ fontSize: "12px", color: "#ef4444" }}>Please enter a valid price (0 or greater).</span>
                    )}
                  </div>

                  <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                    <label style={{ fontSize: "13px", fontWeight: 600, color: "#334155" }}>Currency</label>
                    <select
                      value={assignCurrency}
                      onChange={(e) => setAssignCurrency(e.target.value)}
                      style={{
                        padding: "9px 12px",
                        borderRadius: "6px",
                        border: "1px solid #cbd5e1",
                        fontSize: "13.5px",
                        background: "#fff",
                      }}
                    >
                      <option value="CNY">CNY (¥)</option>
                      <option value="USD">USD ($)</option>
                      <option value="EUR">EUR (€)</option>
                      <option value="INR">INR (₹)</option>
                    </select>
                  </div>
                </div>

                {/* MOQ */}
                <div style={{ display: "flex", flexDirection: "column", gap: "6px", position: "relative", zIndex: 5 }}>
                  <label style={{ fontSize: "13px", fontWeight: 600, color: "#334155" }}>
                    Minimum Order Quantity (MOQ)
                  </label>
                  <input
                    type="number"
                    min="0"
                    placeholder="e.g. 50"
                    value={assignMoq}
                    onKeyDown={(e) => {
                      if (e.key === "-" || e.key === "e") {
                        e.preventDefault();
                      }
                    }}
                    onChange={(e) => {
                      const clean = e.target.value.replace(/[^0-9.]/g, "");
                      setAssignMoq(clean);
                    }}
                    style={{
                      padding: "9px 12px",
                      borderRadius: "6px",
                      border: "1px solid #cbd5e1",
                      fontSize: "13.5px",
                    }}
                  />
                </div>

                {/* Notes */}
                <div style={{ display: "flex", flexDirection: "column", gap: "6px", position: "relative", zIndex: 1 }}>
                  <label style={{ fontSize: "13px", fontWeight: 600, color: "#334155" }}>Notes / Remarks</label>
                  <textarea
                    rows={3}
                    placeholder="e.g. Quoted on WeChat, lead time 15 days, ex-factory."
                    value={assignNotes}
                    onChange={(e) => setAssignNotes(e.target.value)}
                    style={{
                      padding: "9px 12px",
                      borderRadius: "6px",
                      border: "1px solid #cbd5e1",
                      fontSize: "13.5px",
                      resize: "vertical",
                    }}
                  />
                </div>

                {/* Actions Footer */}
                <div
                  className="form-actions modal-footer"
                  style={{
                    display: "flex",
                    justifyContent: "flex-end",
                    gap: "10px",
                    marginTop: "6px",
                    padding: "16px 0 0 0",
                    borderTop: "1px solid #e2e8f0",
                    background: "transparent",
                    overflow: "visible",
                  }}
                >
                  <button type="button" className="btn btn-secondary" onClick={closeAssignModal}>
                    Cancel
                  </button>
                  <button type="submit" className="btn btn-primary" disabled={assignSubmitting}>
                    {assignSubmitting
                      ? "Saving Quote..."
                      : matchedQuote
                      ? "Update Supplier Quote"
                      : hasExisting
                      ? "+ Add Supplier Quote"
                      : "Save Supplier Quote"}
                  </button>
                </div>
              </form>
            </Modal>
          );
        })()}

        {/* Modal: Bulk Excel Import */}
        {importModalOpen && (
          <Modal
            open={true}
            title="Bulk Import Product Prices"
            variant="center"
            cardStyle={{ maxWidth: "600px", width: "95%" }}
            onClose={() => setImportModalOpen(false)}
          >
            <form onSubmit={handleImportSubmit} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              <p style={{ fontSize: "13.5px", color: "#475569", margin: 0 }}>
                Upload an Excel spreadsheet (<code>.xlsx</code>) containing columns for{" "}
                <strong>Product Code</strong>, <strong>Supplier Name</strong>, and <strong>Unit Price</strong>.
              </p>

              <div style={{ background: "#f8fafc", padding: "12px 14px", borderRadius: "6px", border: "1px solid #e2e8f0" }}>
                <a
                  href={`${API_ORIGIN}/api/v1/inventory/product-prices/sample-template`}
                  download="product_price_import_template.xlsx"
                  style={{
                    color: "var(--color-primary, #2563eb)",
                    fontWeight: 600,
                    fontSize: "13px",
                    textDecoration: "none",
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "6px",
                  }}
                >
                  📥 Download Sample Price Template (.xlsx)
                </a>
              </div>

              {/* File Input */}
              <div
                style={{
                  border: "2px dashed #cbd5e1",
                  borderRadius: "8px",
                  padding: "24px",
                  textAlign: "center",
                  background: "#fafafa",
                }}
              >
                <input
                  type="file"
                  accept=".xlsx"
                  id="bulk_price_excel"
                  onChange={(e) => setImportFile(e.target.files?.[0] || null)}
                  style={{ display: "none" }}
                />
                <label
                  htmlFor="bulk_price_excel"
                  style={{ cursor: "pointer", display: "flex", flexDirection: "column", alignItems: "center", gap: "8px" }}
                >
                  <span style={{ fontSize: "28px" }}>📊</span>
                  <span style={{ fontWeight: 600, color: "#1e293b", fontSize: "14px" }}>
                    {importFile ? importFile.name : "Click to select Excel file (.xlsx)"}
                  </span>
                  <span style={{ fontSize: "12px", color: "#94a3b8" }}>
                    {importFile ? `${(importFile.size / 1024).toFixed(1)} KB` : "Supports standard .xlsx workbooks"}
                  </span>
                </label>
              </div>

              {/* Import Results Display */}
              {importResult && (
                <div
                  style={{
                    background: importResult.failed === 0 ? "#f0fdf4" : "#fffbeb",
                    border: `1px solid ${importResult.failed === 0 ? "#86efac" : "#fde68a"}`,
                    borderRadius: "6px",
                    padding: "14px",
                  }}
                >
                  <div style={{ fontWeight: 700, fontSize: "13.5px", marginBottom: "6px", color: "#1e293b" }}>
                    Import Summary:
                  </div>
                  <div style={{ display: "flex", gap: "16px", fontSize: "13px", marginBottom: "8px" }}>
                    <span style={{ color: "#16a34a" }}>✅ Created: {importResult.created}</span>
                    <span style={{ color: "#2563eb" }}>🔄 Updated: {importResult.updated}</span>
                    <span style={{ color: "#dc2626" }}>❌ Failed: {importResult.failed}</span>
                  </div>

                  {importResult.errors && importResult.errors.length > 0 && (
                    <div style={{ maxHeight: "150px", overflowY: "auto", fontSize: "12px", color: "#b91c1c" }}>
                      <strong>Errors encountered:</strong>
                      <ul style={{ margin: "4px 0 0 16px", padding: 0 }}>
                        {importResult.errors.slice(0, 10).map((err, i) => (
                          <li key={i}>
                            Row {err.row}: {err.error}
                          </li>
                        ))}
                        {importResult.errors.length > 10 && (
                          <li>...and {importResult.errors.length - 10} more errors</li>
                        )}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* Actions */}
              <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px", marginTop: "8px" }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setImportModalOpen(false)}
                >
                  Close
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={!importFile || importSubmitting}
                >
                  {importSubmitting ? "Importing Data..." : "Start Import"}
                </button>
              </div>
            </form>
          </Modal>
        )}

        {/* Product Detail Drawer */}
        <SideDrawer
          open={drawerLoading || Boolean(drawerProduct)}
          title={
            drawerProduct
              ? `Product Detail #${drawerProduct.product_code || drawerProduct.id.slice(0, 6)}`
              : "Product Detail"
          }
          subtitle={drawerProduct ? drawerProduct.product_name_tally || drawerProduct.product_name || "" : ""}
          onClose={closeProductDrawer}
        >
          {drawerLoading || !drawerProduct ? (
            <div style={{ textAlign: "center", padding: "40px", color: "#64748b" }}>
              Loading product details...
            </div>
          ) : (
            <>
              {/* Product Photo */}
              {(drawerProduct.image_url || (drawerProduct.images && drawerProduct.images.length > 0)) && (
                <div
                  style={{
                    marginBottom: "20px",
                    textAlign: "center",
                    background: "#f8fafc",
                    padding: "16px",
                    borderRadius: "8px",
                    border: "1px solid #e2e8f0",
                  }}
                >
                  <img
                    src={resolveImageUrl(drawerProduct.image_url || drawerProduct.images?.[0])}
                    alt="Product Photo"
                    style={{
                      maxHeight: "220px",
                      maxWidth: "100%",
                      borderRadius: "8px",
                      objectFit: "contain",
                      boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                    }}
                  />
                </div>
              )}

              {/* Primary Specs */}
              <DetailFieldGrid
                fields={[
                  {
                    label: "Product Name (As Per Tally)",
                    value: drawerProduct.product_name_tally || drawerProduct.product_name || "—",
                    fullWidth: true,
                  },
                  {
                    label: "Brand",
                    value: brands.items.find((b) => b.id === drawerProduct.brand_id)?.name || "—",
                  },
                  {
                    label: "Category",
                    value: categories.items.find((c) => c.id === drawerProduct.category_id)?.name || "—",
                  },
                  {
                    label: "Sub Category",
                    value: subCategories.items.find((sc) => sc.id === drawerProduct.sub_category_id)?.name || "—",
                  },
                  {
                    label: "HSN Code",
                    value: hsnCodes.items.find((h) => h.id === drawerProduct.hsn_id)?.code || "—",
                  },
                  {
                    label: "UOM",
                    value: uoms.items.find((u) => u.id === drawerProduct.uom_id)?.code || "—",
                  },
                  {
                    label: "Packaging Quantity",
                    value: drawerProduct.packaging_quantity != null ? drawerProduct.packaging_quantity : "—",
                  },
                  {
                    label: "Refund VAT %",
                    value: (
                      <span style={{ color: "#16a34a", fontWeight: 700 }}>
                        {drawerProduct.refund_vat_percent != null ? `${drawerProduct.refund_vat_percent}%` : "0%"}
                      </span>
                    ),
                  },
                ]}
              />

              {/* Dimensions & CBM */}
              <div style={{ marginTop: "16px" }}>
                <DetailFieldGrid
                  fields={[
                    {
                      label: "Dimensions (L x W x H cm)",
                      value:
                        drawerProduct.length_cm || drawerProduct.width_cm || drawerProduct.height_cm
                          ? `${drawerProduct.length_cm || 0} x ${drawerProduct.width_cm || 0} x ${drawerProduct.height_cm || 0} cm`
                          : "—",
                    },
                    {
                      label: "Packaging Unit CBM",
                      value: (
                        <span style={{ color: "var(--color-primary, #2563eb)", fontWeight: 700 }}>
                          {drawerProduct.packaging_unit_cbm != null
                            ? Number(drawerProduct.packaging_unit_cbm).toFixed(6)
                            : "—"}
                        </span>
                      ),
                    },
                    {
                      label: "Pkg Net Wt (kg)",
                      value: drawerProduct.packaging_net_weight != null ? drawerProduct.packaging_net_weight : "—",
                    },
                    {
                      label: "Pkg Gross Wt (kg)",
                      value: drawerProduct.packaging_gross_weight != null ? drawerProduct.packaging_gross_weight : "—",
                    },
                  ]}
                />
              </div>

              {/* License Warning */}
              {drawerProduct.license_certificate_required && (
                <div
                  style={{
                    marginTop: "16px",
                    padding: "12px 14px",
                    background: "#fff1f2",
                    border: "1px solid #fecdd3",
                    borderRadius: "6px",
                    color: "#9f1239",
                    fontSize: "13px",
                  }}
                >
                  <strong style={{ display: "block", marginBottom: "2px" }}>
                    ⚠️ Required License / Certificate:
                  </strong>
                  <span>{drawerProduct.license_certificate_required}</span>
                </div>
              )}

              {/* Specification description */}
              {drawerProduct.specification && (
                <div
                  style={{
                    marginTop: "16px",
                    background: "#f8fafc",
                    border: "1px solid #e2e8f0",
                    borderRadius: "8px",
                    padding: "16px",
                  }}
                >
                  <span style={{ fontSize: "12px", fontWeight: 700, color: "#64748b", display: "block", marginBottom: "6px" }}>
                    Technical Specifications:
                  </span>
                  <p style={{ margin: 0, fontSize: "13px", color: "#0f172a", whiteSpace: "pre-wrap" }}>
                    {drawerProduct.specification}
                  </p>
                </div>
              )}
            </>
          )}
        </SideDrawer>
      </main>
    </AppShell>
  );
}
export default ProductPricesPage;
