"""PostgreSQL integration tests. DATABASE_URL must point to disposable CI/local DB."""

from __future__ import annotations

import os
import uuid

import psycopg
import pytest


DATABASE_URL = os.getenv("DATABASE_URL")
pytestmark = pytest.mark.skipif(not DATABASE_URL, reason="DATABASE_URL not configured")


@pytest.fixture(scope="module")
def users() -> tuple[uuid.UUID, uuid.UUID]:
    assert DATABASE_URL
    user_a, user_b = uuid.uuid4(), uuid.uuid4()
    with psycopg.connect(DATABASE_URL) as connection:
        connection.execute("insert into auth.users (id) values (%s), (%s)", (user_a, user_b))
    yield user_a, user_b
    with psycopg.connect(DATABASE_URL) as connection:
        connection.execute("delete from auth.users where id in (%s, %s)", (user_a, user_b))


def user_connection(user_id: uuid.UUID) -> psycopg.Connection:
    assert DATABASE_URL
    connection = psycopg.connect(DATABASE_URL)
    connection.execute("select set_config('request.jwt.claim.sub', %s, true)", (str(user_id),))
    connection.execute("set local role authenticated")
    return connection


def test_wardrobe_crud_isolated_by_owner(users: tuple[uuid.UUID, uuid.UUID]) -> None:
    user_a, user_b = users
    with user_connection(user_a) as connection:
        item_id = connection.execute(
            """insert into profile.wardrobe_items (owner_id, category_code, item_name)
               values (%s, 'top', 'synthetic test item') returning id""",
            (user_a,),
        ).fetchone()[0]
        assert connection.execute(
            "select item_name from profile.wardrobe_items where id = %s", (item_id,)
        ).fetchone() == ("synthetic test item",)

    with user_connection(user_b) as connection:
        assert connection.execute(
            "select id from profile.wardrobe_items where id = %s", (item_id,)
        ).fetchone() is None
        assert connection.execute(
            "update profile.wardrobe_items set item_name = 'tampered' where id = %s returning id",
            (item_id,),
        ).fetchone() is None
        assert connection.execute(
            "delete from profile.wardrobe_items where id = %s returning id", (item_id,)
        ).fetchone() is None

    with user_connection(user_a) as connection:
        changed = connection.execute(
            "update profile.wardrobe_items set item_name = 'updated', version = version + 1 where id = %s returning item_name",
            (item_id,),
        ).fetchone()
        assert changed == ("updated",)
        assert connection.execute(
            "delete from profile.wardrobe_items where id = %s returning id", (item_id,)
        ).fetchone() == (item_id,)


def test_catalog_excludes_unapproved_and_expired_products() -> None:
    assert DATABASE_URL
    pending_source_id, allowed_source_id, expired_source_id = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    pending_product_id, allowed_product_id, expired_product_id, expired_source_product_id = (
        uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    )
    with psycopg.connect(DATABASE_URL) as connection:
        connection.execute(
            """insert into catalog.data_sources (id, source_key, display_name, rights_status, permitted_uses)
               values (%s, 'test-pending-' || %s, 'pending test source', 'pending', '{}')""",
            (pending_source_id, str(pending_source_id)),
        )
        connection.execute(
            """insert into catalog.data_sources (id, source_key, display_name, rights_status, permitted_uses)
               values (%s, 'test-synthetic-' || %s, 'synthetic test source', 'synthetic', '{product_display}')""",
            (allowed_source_id, str(allowed_source_id)),
        )
        connection.execute(
            """insert into catalog.data_sources
               (id, source_key, display_name, rights_status, permitted_uses, expires_at)
               values (%s, 'test-expired-' || %s, 'expired synthetic source', 'synthetic', '{product_display}', now() - interval '1 second')""",
            (expired_source_id, str(expired_source_id)),
        )
        connection.execute(
            """insert into catalog.products
               (id, source_id, source_product_id, brand_name, product_name, category_code, product_url, observed_at, expires_at, is_synthetic)
               values (%s, %s, 'pending-1', 'Test', 'Pending product', 'top', 'https://example.invalid/pending', now(), now() + interval '1 day', false)""",
            (pending_product_id, pending_source_id),
        )
        connection.execute(
            """insert into catalog.products
               (id, source_id, source_product_id, brand_name, product_name, category_code, product_url, observed_at, expires_at, is_synthetic)
               values (%s, %s, 'synthetic-1', 'Test', 'Visible fixture', 'top', 'https://example.invalid/synthetic', now(), now() + interval '1 day', true)""",
            (allowed_product_id, allowed_source_id),
        )
        connection.execute(
            """insert into catalog.products
               (id, source_id, source_product_id, brand_name, product_name, category_code, product_url, observed_at, expires_at, is_synthetic)
               values (%s, %s, 'expired-product-1', 'Test', 'Expired product', 'top', 'https://example.invalid/expired-product', now(), now() - interval '1 second', true)""",
            (expired_product_id, allowed_source_id),
        )
        connection.execute(
            """insert into catalog.products
               (id, source_id, source_product_id, brand_name, product_name, category_code, product_url, observed_at, expires_at, is_synthetic)
               values (%s, %s, 'expired-source-product-1', 'Test', 'Expired source product', 'top', 'https://example.invalid/expired-source', now(), now() + interval '1 day', true)""",
            (expired_source_product_id, expired_source_id),
        )

    with user_connection(uuid.uuid4()) as connection:
        visible = {row[0] for row in connection.execute("select id from catalog.products")}
        assert allowed_product_id in visible
        assert pending_product_id not in visible
        assert expired_product_id not in visible
        assert expired_source_product_id not in visible

    with psycopg.connect(DATABASE_URL) as connection:
        connection.execute(
            "delete from catalog.products where id = any(%s)",
            ([pending_product_id, allowed_product_id, expired_product_id, expired_source_product_id],),
        )
        connection.execute(
            "delete from catalog.data_sources where id = any(%s)",
            ([pending_source_id, allowed_source_id, expired_source_id],),
        )
