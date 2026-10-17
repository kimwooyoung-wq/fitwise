# FITWISE Prototype API

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements-dev.txt
.\.venv\Scripts\python -m uvicorn app.main:app --reload
```

- Swagger UI: <http://127.0.0.1:8000/docs>
- OpenAPI JSON: <http://127.0.0.1:8000/openapi.json>
- Health: <http://127.0.0.1:8000/health>

현재 응답은 합성 상품만 사용한다. 브랜드·상품 피드 계약이 확정되기 전에는 실제 상품이나 이미지를 추가하지 않는다.

## DB/RLS 초기 검증

Issue #5의 DB 기반은 로컬 또는 CI용 disposable PostgreSQL에서만 검증한다. Supabase CLI/Docker가 설치된 개발환경 또는 CI PostgreSQL 서비스에서 아래 순서로 실행한다.

From the repository root:

```sh
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/tests/bootstrap.sql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/supabase/migrations/202610180001_foundation.sql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/supabase/seed.sql
python -m pip install -r requirements-dev.txt
python -m pytest -q services/api/tests/test_database_rls.py services/api/tests/test_catalog_ingestion.py
```

`db/tests/bootstrap.sql`은 CI에서만 Supabase Auth의 최소 동작을 흉내 내는 테스트 shim이다. 실제 Supabase에서는 적용하지 않는다. 합성 seed는 외부 상품이 아니며, 운영 DB에 실행하지 않는다. 현재 Windows 개발환경에는 Docker, Supabase CLI, PostgreSQL이 설치되어 있지 않을 수 있으므로 실제 RLS 통합 결과는 CI 증빙을 확인한다.
