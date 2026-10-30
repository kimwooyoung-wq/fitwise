-- Assert that the synthetic seed remains idempotent after repeated execution.
-- Run only against the disposable local/CI database.
do $$
declare
    source_count integer;
    product_count integer;
    variant_count integer;
    offer_count integer;
begin
    select count(*) into source_count
      from catalog.data_sources
     where source_key = 'fitwise-synthetic-v1';

    select count(*) into product_count
      from catalog.products product
      join catalog.data_sources source on source.id = product.source_id
     where source.source_key = 'fitwise-synthetic-v1'
       and product.source_product_id = 'synthetic-shirt-001';

    select count(*) into variant_count
      from catalog.product_variants variant
      join catalog.products product on product.id = variant.product_id
      join catalog.data_sources source on source.id = product.source_id
     where source.source_key = 'fitwise-synthetic-v1'
       and product.source_product_id = 'synthetic-shirt-001'
       and variant.source_variant_id = 'synthetic-shirt-001-m';

    select count(*) into offer_count
      from catalog.offers offer
      join catalog.product_variants variant on variant.id = offer.variant_id
      join catalog.products product on product.id = variant.product_id
      join catalog.data_sources source on source.id = product.source_id
     where source.source_key = 'fitwise-synthetic-v1'
       and product.source_product_id = 'synthetic-shirt-001'
       and variant.source_variant_id = 'synthetic-shirt-001-m'
       and offer.seller_name = 'FITWISE synthetic fixture';

    if source_count <> 1 or product_count <> 1 or variant_count <> 1 or offer_count <> 1 then
        raise exception 'synthetic seed is not idempotent: source %, product %, variant %, offer %',
            source_count, product_count, variant_count, offer_count;
    end if;
end
$$;
