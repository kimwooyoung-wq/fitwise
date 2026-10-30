# FITWISE Prototype API

From `services/api`:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements-dev.txt
.\.venv\Scripts\python -m uvicorn app.main:app --reload
```

- Swagger UI: <http://127.0.0.1:8000/docs>
- OpenAPI JSON: <http://127.0.0.1:8000/openapi.json>
- Health: <http://127.0.0.1:8000/health>

## 카탈로그 검색

`GET /v1/catalog/search?q=네이비&category=outerwear&budget_max=150000`은 개발/검증용 PostgreSQL의 **합성 상품만** 조회한다. `DATABASE_URL`이 설정되지 않으면 503을 반환한다. API SQL도 source 권한, 상품 활성·만료 시각, 판매 조건의 재고·만료 시각을 모두 확인하고 예산을 강제한다. 검색어는 SQL 파라미터로 전달하고 LIKE 메타문자를 escape한다.

이 단계는 인증된 개인 옷장이나 실제 승인 상품 피드를 공개하는 경로가 아니다. 검색 SQL은 `product.is_synthetic`과 `source.rights_status = 'synthetic'`를 함께 요구한다. 실제 공급자 연결은 공식 피드/API, 계약상 저장·표시 권리와 자격 증명이 마련된 별도 작업 전까지 비활성화한다. 운영 DB나 실제 사용자 데이터를 이 프로토타입 API에 연결하지 않는다.

## DB/RLS·검색 검증

Issue #5의 DB 기반은 disposable 로컬/CI PostgreSQL에서만 검증한다. 저장소 루트에서 다음 순서로 준비한다.

```sh
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/tests/bootstrap.sql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/supabase/migrations/202610180001_foundation.sql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/supabase/migrations/202610300001_catalog_search_index.sql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/supabase/seed.sql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/supabase/seed.sql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/tests/assert_seed_idempotent.sql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/tests/explain_catalog_search.sql
python -m pip install -r services/api/requirements-dev.txt
python -m pytest -q services/api/tests
```

`db/tests/bootstrap.sql`은 CI에서만 Supabase Auth를 흉내 내는 테스트 shim이며 실제 Supabase에서 적용하지 않는다. 합성 seed와 EXPLAIN 스크립트는 운영 DB에서 실행하지 않는다. 작은 fixture의 실행 계획은 쿼리 동작 확인용이며 운영 규모의 성능 보증이 아니다.
