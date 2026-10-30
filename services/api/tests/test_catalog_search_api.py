"""PostgreSQL-backed API tests; DATABASE_URL must target disposable CI/local DB."""
from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from app.main import app

pytestmark = pytest.mark.skipif(
    not os.getenv("DATABASE_URL"),
    reason="DATABASE_URL not configured; catalog search requires disposable PostgreSQL",
)
client = TestClient(app)


def test_search_returns_only_affordable_synthetic_catalog_rows() -> None:
    response = client.get(
        "/v1/catalog/search",
        params={"q": "네이비", "category": "outerwear", "budget_max": 150000},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["query"] == "네이비"
    assert len(body["items"]) == 1
    item = body["items"][0]
    assert item["product_name"] == "합성 네이비 셔츠 재킷"
    assert item["price_minor"] == 129000
    assert item["stock_status"] == "in_stock"


def test_search_honors_budget_category_and_empty_results() -> None:
    over_budget = client.get(
        "/v1/catalog/search",
        params={"category": "outerwear", "budget_max": 100000},
    )
    wrong_category = client.get(
        "/v1/catalog/search",
        params={"category": "bottom", "budget_max": 150000},
    )
    unmatched = client.get(
        "/v1/catalog/search",
        params={"q": "없는상품", "budget_max": 150000},
    )

    assert over_budget.status_code == wrong_category.status_code == unmatched.status_code == 200
    assert over_budget.json()["items"] == []
    assert wrong_category.json()["items"] == []
    assert unmatched.json()["items"] == []


def test_search_treats_sql_metacharacters_as_literal_text() -> None:
    response = client.get(
        "/v1/catalog/search",
        params={"q": "%' OR 1=1 --", "budget_max": 150000},
    )

    assert response.status_code == 200
    assert response.json()["items"] == []
