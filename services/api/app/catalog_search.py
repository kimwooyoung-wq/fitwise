"""Read-only database search over explicitly synthetic catalog fixtures.

This endpoint must never expose approved/live product rows. Search text is
parameterized and its wildcards are escaped before the query is executed.
"""
from __future__ import annotations

import os
from typing import Literal

import psycopg
from fastapi import HTTPException
from pydantic import BaseModel, Field
from psycopg.rows import dict_row


class CatalogSearchResponse(BaseModel):
    query: str | None
    category: str | None
    budget_max: int
    items: list[dict[str, object]]
    data_notice: str = "검색 결과는 DB 연결 및 검색 흐름 검증용 합성 상품입니다."


SEARCH_SQL = """
with current_offers as (
    select distinct on (product.id)
        product.id as product_id,
        product.brand_name,
        product.product_name,
        product.category_code,
        product.product_url,
        product.observed_at as product_observed_at,
        product.expires_at as product_expires_at,
        offer.seller_name,
        offer.price_minor,
        offer.currency_code,
        offer.stock_status,
        offer.purchase_url,
        offer.observed_at as offer_observed_at,
        offer.expires_at as offer_expires_at
    from catalog.products product
    join catalog.data_sources source on source.id = product.source_id
    join catalog.product_variants variant on variant.product_id = product.id
    join lateral (
        select
            candidate.seller_name,
            candidate.price_minor,
            candidate.currency_code,
            candidate.stock_status,
            candidate.purchase_url,
            candidate.observed_at,
            candidate.expires_at
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
      and (%s::text is null or product.category_code = %s)
      and (
          %s::text is null
          or product.product_name ilike %s escape '!'
          or product.brand_name ilike %s escape '!'
          or product.category_code ilike %s escape '!'
      )
      and offer.price_minor <= %s
    order by product.id, offer.price_minor asc, offer.observed_at desc
)
select *
from current_offers
order by price_minor asc, product_name asc, product_id
limit %s
"""


def _like_pattern(query: str) -> str:
    escaped = query.replace("!", "!!").replace("%", "!%").replace("_", "!_")
    return f"%{escaped}%"


def search_synthetic_catalog(
    *,
    query: str | None,
    category: str | None,
    budget_max: int,
    limit: int = 20,
) -> CatalogSearchResponse:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise HTTPException(status_code=503, detail="카탈로그 데이터베이스가 설정되지 않았습니다.")

    normalized_query = " ".join(query.split()) if query else None
    pattern = _like_pattern(normalized_query) if normalized_query else None
    params = (
        category,
        category,
        normalized_query,
        pattern,
        pattern,
        pattern,
        budget_max,
        limit,
    )
    try:
        with psycopg.connect(database_url, row_factory=dict_row, connect_timeout=3) as connection:
            rows = connection.execute(SEARCH_SQL, params).fetchall()
    except psycopg.Error as exc:
        # Database details and user search text must not leak into API errors/logs.
        raise HTTPException(status_code=503, detail="카탈로그를 일시적으로 조회할 수 없습니다.") from exc

    return CatalogSearchResponse(
        query=normalized_query,
        category=category,
        budget_max=budget_max,
        items=[dict(row) for row in rows],
    )
