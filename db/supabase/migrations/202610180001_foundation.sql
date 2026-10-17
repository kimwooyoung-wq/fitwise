-- FITWISE development foundation. Apply only to a disposable/local Supabase DB
-- or the CI PostgreSQL service. Never run this migration against production.
create schema if not exists profile;
create schema if not exists catalog;

create table if not exists profile.wardrobe_items (
    id uuid primary key default gen_random_uuid(),
    owner_id uuid not null references auth.users (id) on delete cascade,
    category_code text not null check (length(category_code) between 1 and 64),
    item_name text not null check (length(item_name) between 1 and 160),
    color_code text,
    fit_code text,
    version integer not null default 1 check (version > 0),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    deleted_at timestamptz
);

create index if not exists wardrobe_items_owner_created_idx
    on profile.wardrobe_items (owner_id, created_at desc, id desc)
    where deleted_at is null;

alter table profile.wardrobe_items enable row level security;
alter table profile.wardrobe_items force row level security;

drop policy if exists wardrobe_select_own on profile.wardrobe_items;
create policy wardrobe_select_own on profile.wardrobe_items
    for select to authenticated
    using ((select auth.uid()) = owner_id and deleted_at is null);

drop policy if exists wardrobe_insert_own on profile.wardrobe_items;
create policy wardrobe_insert_own on profile.wardrobe_items
    for insert to authenticated
    with check ((select auth.uid()) = owner_id);

drop policy if exists wardrobe_update_own on profile.wardrobe_items;
create policy wardrobe_update_own on profile.wardrobe_items
    for update to authenticated
    using ((select auth.uid()) = owner_id and deleted_at is null)
    with check ((select auth.uid()) = owner_id);

drop policy if exists wardrobe_delete_own on profile.wardrobe_items;
create policy wardrobe_delete_own on profile.wardrobe_items
    for delete to authenticated
    using ((select auth.uid()) = owner_id);

grant usage on schema profile to authenticated;
grant select, insert, update, delete on profile.wardrobe_items to authenticated;
revoke all on schema profile from anon;
revoke all on profile.wardrobe_items from anon;

create table if not exists catalog.data_sources (
    id uuid primary key default gen_random_uuid(),
    source_key text not null unique,
    display_name text not null,
    rights_status text not null check (rights_status in ('pending', 'approved', 'synthetic', 'revoked')),
    permitted_uses text[] not null default '{}',
    terms_url text,
    reviewed_at timestamptz,
    expires_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    check (rights_status <> 'approved' or (reviewed_at is not null and terms_url like 'https://%' and cardinality(permitted_uses) > 0))
);

create table if not exists catalog.products (
    id uuid primary key default gen_random_uuid(),
    source_id uuid not null references catalog.data_sources (id),
    source_product_id text not null,
    brand_name text not null,
    product_name text not null,
    category_code text not null,
    product_url text not null,
    observed_at timestamptz not null,
    expires_at timestamptz not null,
    is_active boolean not null default true,
    is_synthetic boolean not null default false,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (source_id, source_product_id)
);

create index if not exists catalog_products_category_active_idx
    on catalog.products (category_code, id)
    where is_active;

create table if not exists catalog.product_variants (
    id uuid primary key default gen_random_uuid(),
    product_id uuid not null references catalog.products (id) on delete cascade,
    source_variant_id text not null,
    color_code text,
    size_label text not null,
    measurements jsonb not null default '{}'::jsonb,
    unique (product_id, source_variant_id)
);

create table if not exists catalog.offers (
    id uuid primary key default gen_random_uuid(),
    variant_id uuid not null references catalog.product_variants (id) on delete cascade,
    seller_name text not null,
    price_minor bigint not null check (price_minor >= 0),
    currency_code varchar(3) not null,
    stock_status text not null check (stock_status in ('in_stock', 'low_stock', 'out_of_stock', 'unknown')),
    purchase_url text not null,
    observed_at timestamptz not null,
    expires_at timestamptz not null,
    unique (variant_id, seller_name, observed_at)
);

alter table catalog.data_sources enable row level security;
alter table catalog.products enable row level security;
alter table catalog.product_variants enable row level security;
alter table catalog.offers enable row level security;

drop policy if exists sources_read_nonrevoked on catalog.data_sources;
create policy sources_read_nonrevoked on catalog.data_sources
    for select to authenticated
    using (rights_status in ('approved', 'synthetic') and (expires_at is null or expires_at > now()));

-- Internal source metadata is not exposed to client roles. Product visibility
-- requires an approved/synthetic source and a current, active record.
drop policy if exists products_read_permitted_current on catalog.products;
create policy products_read_permitted_current on catalog.products
    for select to authenticated
    using (
        is_active
        and expires_at > now()
        and exists (
            select 1 from catalog.data_sources source
            where source.id = products.source_id
              and source.rights_status in ('approved', 'synthetic')
              and (source.expires_at is null or source.expires_at > now())
              and (source.rights_status = 'synthetic' or 'product_display' = any(source.permitted_uses))
        )
    );

drop policy if exists variants_read_permitted_current on catalog.product_variants;
create policy variants_read_permitted_current on catalog.product_variants
    for select to authenticated
    using (exists (select 1 from catalog.products product where product.id = product_variants.product_id));

drop policy if exists offers_read_permitted_current on catalog.offers;
create policy offers_read_permitted_current on catalog.offers
    for select to authenticated
    using (
        expires_at > now()
        and stock_status in ('in_stock', 'low_stock')
        and exists (select 1 from catalog.product_variants variant where variant.id = offers.variant_id)
    );

grant usage on schema catalog to authenticated;
revoke all on schema catalog from anon;
revoke all on all tables in schema catalog from anon, authenticated;
grant usage on schema catalog to authenticated;
grant select (id, rights_status, permitted_uses, expires_at) on catalog.data_sources to authenticated;
grant select on catalog.products, catalog.product_variants, catalog.offers to authenticated;

comment on table profile.wardrobe_items is 'User-owned wardrobe data; access must be constrained by owner_id RLS.';
comment on table catalog.data_sources is 'Private source-rights registry. Never expose credentials or raw partner payloads.';
comment on table catalog.products is 'Only current products from approved or explicitly synthetic sources are visible to authenticated clients.';
