-- Representative read-only catalog search plan. Use only the disposable local/CI DB.
-- The CI log retains the actual plan; tiny synthetic fixtures are correctness
-- evidence, not a production-scale latency claim.
explain (analyze, buffers, format text)
with current_offers as (
    select distinct on (product.id)
        product.id as product_id,
        product.brand_name,
        product.product_name,
        product.category_code,
        offer.price_minor,
        offer.stock_status,
        offer.observed_at as offer_observed_at
    from catalog.products product
    join catalog.data_sources source on source.id = product.source_id
    join catalog.product_variants variant on variant.product_id = product.id
    join lateral (
        select candidate.price_minor, candidate.stock_status, candidate.observed_at, candidate.id
        from catalog.offers candidate
        where candidate.variant_id = variant.id
          and candidate.stock_status in ('in_stock', 'low_stock')
          and candidate.expires_at > now()
        order by candidate.observed_at desc, candidate.id
        limit 1
    ) offer on true
    where product.is_synthetic
      and source.rights_status = 'synthetic'
      and (source.expires_at is null or source.expires_at > now())
      and product.is_active
      and product.expires_at > now()
      and product.category_code = 'outerwear'
      and (product.product_name ilike '%네이비%' or product.brand_name ilike '%네이비%')
      and offer.price_minor <= 150000
    order by product.id, offer.price_minor asc, offer.observed_at desc
)
select *
from current_offers
order by price_minor asc, product_name asc, product_id
limit 20;
