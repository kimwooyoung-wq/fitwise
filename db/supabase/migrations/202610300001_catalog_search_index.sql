-- Supports the per-variant latest available offer lookup used by
-- services/api/app/catalog_search.py. Apply after the foundation migration.
create index if not exists catalog_offers_available_variant_observed_idx
    on catalog.offers (variant_id, observed_at desc, id)
    include (seller_name, price_minor, currency_code, stock_status, purchase_url, expires_at)
    where stock_status in ('in_stock', 'low_stock');
