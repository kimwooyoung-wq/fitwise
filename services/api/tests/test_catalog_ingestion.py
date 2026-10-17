from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from app.catalog_ingestion import CatalogRecord, SourcePolicy, validate_record, validate_source_policy

NOW = datetime(2026, 10, 18, 0, 0, tzinfo=timezone.utc)


def synthetic_policy() -> SourcePolicy:
    return SourcePolicy("synthetic-fixture", "synthetic", frozenset())


def approved_policy() -> SourcePolicy:
    return SourcePolicy(
        "partner-feed",
        "approved",
        frozenset({"catalog_storage", "product_display"}),
        reviewed_at=NOW - timedelta(days=1),
        expires_at=NOW + timedelta(days=30),
        terms_url="https://example.invalid/partner-terms",
    )


def product_record(*, expires_at: datetime | None = None) -> CatalogRecord:
    return CatalogRecord(
        "sku-1", "Authorized brand", "Synthetic test jacket", "outerwear",
        "https://example.invalid/products/sku-1", NOW - timedelta(minutes=1),
        expires_at or NOW + timedelta(hours=1),
    )


def test_synthetic_fixture_is_accepted_without_being_mistaken_for_live_source() -> None:
    validate_source_policy(synthetic_policy(), NOW)
    validate_record(product_record(), NOW)


def test_approved_source_requires_storage_and_display_rights() -> None:
    validate_source_policy(approved_policy(), NOW)
    with pytest.raises(ValueError, match="permit catalog storage"):
        validate_source_policy(SourcePolicy("partner", "approved", frozenset({"product_display"}), NOW, terms_url="https://example.invalid/terms"), NOW)


@pytest.mark.parametrize("status", ["pending", "revoked"])
def test_nonapproved_source_is_rejected(status: str) -> None:
    policy = SourcePolicy("source", status, frozenset({"catalog_storage", "product_display"}), NOW)
    with pytest.raises(ValueError, match="not approved"):
        validate_source_policy(policy, NOW)


def test_expired_source_and_product_are_rejected() -> None:
    expired = SourcePolicy(
        "partner", "approved", frozenset({"catalog_storage", "product_display"}),
        reviewed_at=NOW - timedelta(days=2), expires_at=NOW - timedelta(seconds=1),
        terms_url="https://example.invalid/partner-terms",
    )
    with pytest.raises(ValueError, match="expired"):
        validate_source_policy(expired, NOW)
    with pytest.raises(ValueError, match="expired"):
        validate_record(product_record(expires_at=NOW - timedelta(seconds=1)), NOW)


def test_non_https_and_timezone_naive_records_are_rejected() -> None:
    insecure = replace(product_record(), product_url="http://example.invalid/item")
    with pytest.raises(ValueError, match="HTTPS"):
        validate_record(insecure, NOW)
    naive = replace(product_record(), observed_at=datetime(2026, 10, 17))
    with pytest.raises(ValueError, match="timezone-aware"):
        validate_record(naive, NOW)
