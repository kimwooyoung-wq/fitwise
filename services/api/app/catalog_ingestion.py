"""Provider-neutral catalog gate; it deliberately does not fetch or scrape data."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal
from urllib.parse import urlparse


RightsStatus = Literal["pending", "approved", "synthetic", "revoked"]


@dataclass(frozen=True)
class SourcePolicy:
    source_key: str
    rights_status: RightsStatus
    permitted_uses: frozenset[str]
    reviewed_at: datetime | None = None
    expires_at: datetime | None = None
    terms_url: str | None = None


@dataclass(frozen=True)
class CatalogRecord:
    external_id: str
    brand_name: str
    product_name: str
    category_code: str
    product_url: str
    observed_at: datetime
    expires_at: datetime


def validate_source_policy(policy: SourcePolicy, now: datetime | None = None) -> None:
    """Fail closed unless storage and display rights are explicit and current."""
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    if policy.rights_status == "synthetic":
        return
    if policy.rights_status != "approved":
        raise ValueError("source rights are not approved")
    if policy.reviewed_at is None or policy.reviewed_at.tzinfo is None:
        raise ValueError("approved sources require a timezone-aware rights review")
    if not policy.terms_url or urlparse(policy.terms_url).scheme != "https":
        raise ValueError("approved sources require an HTTPS terms or rights reference")
    if not {"catalog_storage", "product_display"}.issubset(policy.permitted_uses):
        raise ValueError("source must permit catalog storage and product display")
    if policy.expires_at is not None and (policy.expires_at.tzinfo is None or policy.expires_at <= current):
        raise ValueError("source authorization is expired")


def validate_record(record: CatalogRecord, now: datetime | None = None) -> None:
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    for field_name, value in (
        ("observed_at", record.observed_at),
        ("expires_at", record.expires_at),
    ):
        if value.tzinfo is None:
            raise ValueError(f"{field_name} must be timezone-aware")
    if not record.external_id.strip() or not record.brand_name.strip() or not record.product_name.strip():
        raise ValueError("external id, brand, and product name are required")
    if record.expires_at <= current or record.observed_at > current:
        raise ValueError("product record is expired or has a future observation time")
    parsed_url = urlparse(record.product_url)
    if parsed_url.scheme != "https" or not parsed_url.netloc:
        raise ValueError("product URL must be HTTPS")
