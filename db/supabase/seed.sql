-- Optional LOCAL/CI development fixture only; do not use as production data.
insert into catalog.data_sources (
    source_key, display_name, rights_status, permitted_uses
)
values ('fitwise-synthetic-v1', 'FITWISE 합성 개발 fixture', 'synthetic', array['product_display'])
on conflict (source_key) do nothing;

insert into catalog.products (
    source_id, source_product_id, brand_name, product_name, category_code,
    product_url, observed_at, expires_at, is_synthetic
)
select id, 'synthetic-shirt-001', 'FITWISE LAB', '합성 네이비 셔츠 재킷', 'outerwear',
       'https://example.invalid/synthetic-shirt-001', timestamp with time zone '2026-10-18 00:00:00+00', timestamp with time zone '2099-01-01 00:00:00+00', true
from catalog.data_sources
where source_key = 'fitwise-synthetic-v1'
on conflict (source_id, source_product_id) do nothing;

insert into catalog.product_variants (product_id, source_variant_id, color_code, size_label)
select product.id, 'synthetic-shirt-001-m', 'navy', 'M'
from catalog.products product
join catalog.data_sources source on source.id = product.source_id
where source.source_key = 'fitwise-synthetic-v1'
  and product.source_product_id = 'synthetic-shirt-001'
on conflict (product_id, source_variant_id) do nothing;

insert into catalog.offers (
    variant_id, seller_name, price_minor, currency_code, stock_status,
    purchase_url, observed_at, expires_at
)
select variant.id, 'FITWISE synthetic fixture', 129000, 'KRW', 'in_stock',
       'https://example.invalid/synthetic-shirt-001', timestamp with time zone '2026-10-18 00:00:00+00', timestamp with time zone '2099-01-01 00:00:00+00'
from catalog.product_variants variant
join catalog.products product on product.id = variant.product_id
join catalog.data_sources source on source.id = product.source_id
where source.source_key = 'fitwise-synthetic-v1'
  and variant.source_variant_id = 'synthetic-shirt-001-m'
on conflict (variant_id, seller_name, observed_at) do nothing;
