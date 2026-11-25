# FITWISE 개발 환경 설정

이 저장소는 **Expo·React Native 모바일 앱 + FastAPI + PostgreSQL** 모노레포입니다. 별도의 Next.js 웹 앱은 현재 범위에 없습니다. 제품 헌장에 따라 웹은 모바일 P0 검증 이후에 다시 검토합니다.

## 준비물

- Git
- Docker Desktop (Docker Compose v2 포함)
- Node.js 22
- Python 3.13

## 1. 로컬 DB 시작

저장소 루트에서 PowerShell을 엽니다.

```powershell
Copy-Item .env.example .env
docker compose up -d db
docker compose ps
```

DB 포트는 기본 `127.0.0.1:5432`에만 공개됩니다. 다른 PC·휴대폰·인터넷에서 DB 포트로 직접 접속할 수 없습니다. 비밀번호와 데이터베이스 이름을 바꾸면 `.env` 안의 `DATABASE_URL`도 같은 값으로 맞춥니다.

새 DB 볼륨에서는 pgvector extension이 초기화됩니다. 기존 데이터 볼륨을 재사용하고 extension을 아직 만들지 않았다면 다음 명령을 실행합니다.

```powershell
docker compose exec -T db sh -lc 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "CREATE EXTENSION IF NOT EXISTS vector;"'
```

## 2. 합성 데이터용 스키마 준비

아래 절차는 버릴 수 있는 로컬 개발 DB에서만 실행합니다. `db/tests/bootstrap.sql`은 Supabase Auth를 흉내 내는 테스트 shim이며 실제 Supabase나 운영 DB에 적용하지 않습니다.

```powershell
docker compose exec -T db sh -lc 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /opt/fitwise/db/tests/bootstrap.sql'
docker compose exec -T db sh -lc 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /opt/fitwise/db/supabase/migrations/202610180001_foundation.sql'
docker compose exec -T db sh -lc 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /opt/fitwise/db/supabase/migrations/202610300001_catalog_search_index.sql'
docker compose exec -T db sh -lc 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /opt/fitwise/db/supabase/seed.sql'
docker compose exec -T db sh -lc 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /opt/fitwise/db/supabase/seed.sql'
docker compose exec -T db sh -lc 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /opt/fitwise/db/tests/assert_seed_idempotent.sql'
```

두 번째 seed 실행은 중복 데이터를 만들지 않는지 확인하는 절차입니다. 데이터는 합성 fixture이며 실제 상품 정보를 넣지 않습니다.

## 3. API 실행

새 PowerShell 창을 열고 저장소 루트에서 실행합니다.

```powershell
$databaseUrlLine = Get-Content .env | Where-Object { $_ -match '^DATABASE_URL=' } | Select-Object -First 1
$env:DATABASE_URL = ($databaseUrlLine -split '=', 2)[1]
Set-Location services/api
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements-dev.txt
.\.venv\Scripts\python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

다른 창에서 API 상태를 확인합니다.

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

정상 응답은 `status: ok`입니다. API를 휴대폰에서 호출할 때는 개발 PC의 사설 Wi-Fi IP와 포트 8000을 앱의 로컬 환경 파일에 설정합니다. 휴대폰 테스트는 신뢰할 수 있는 사설 네트워크와 합성 데이터로만 하며 이 개발 API를 인터넷에 공개하지 않습니다.

## 4. 모바일 앱 실행

저장소 루트의 별도 PowerShell 창에서 실행합니다.

```powershell
Set-Location apps/mobile
npm ci
Copy-Item .env.example .env.local
npm start
```

`.env.local`의 `EXPO_PUBLIC_API_BASE_URL`은 실행 대상에 맞춥니다.

| 대상 | 예시 |
|---|---|
| Android Emulator | `http://10.0.2.2:8000` |
| iOS Simulator | `http://127.0.0.1:8000` |
| 실제 휴대폰 | `http://개발PC의_사설_IP:8000` |

실제 휴대폰은 개발 PC와 같은 Wi-Fi를 사용해야 합니다. 방화벽에서 로컬 개발 연결이 차단되면 사설 네트워크의 포트 8000 접근을 허용해야 할 수 있습니다.

## 5. 검사 명령

검사는 개발자가 변경 범위에 맞춰 실행합니다. 이 문서 작성 PR에서는 로컬 검사나 기기 검사를 실행했다고 주장하지 않습니다.

```powershell
# 모바일 (apps/mobile에서)
npm run lint
npm run typecheck
npm test

# API (services/api에서)
python -m pytest -q

# 로컬 데이터베이스 (저장소 루트에서)
docker compose ps
```

PR CI는 모바일 lint·typecheck·테스트, API 테스트, PostgreSQL/RLS/카탈로그 작업을 별도 job으로 실행합니다. CI 통과는 기기 확인이나 사람의 설정 재현을 대신하지 않습니다.

## 문제 해결

- `docker compose ps`에서 DB가 healthy가 아니면 `docker compose logs db`로 시작 오류를 확인합니다.
- 로컬 5432 포트가 이미 사용 중이면 `.env`에서 `POSTGRES_PORT`를 바꾸고 `DATABASE_URL` 포트도 같은 값으로 수정합니다.
- API 카탈로그 검색이 503이면 API를 실행한 PowerShell의 `DATABASE_URL`이 올바른지 확인합니다.
- 모바일 API 연결이 안 되면 시뮬레이터별 주소, PC와 휴대폰의 동일 Wi-Fi, PC 방화벽을 확인합니다.
- DB를 멈출 때는 `docker compose down`을 사용합니다. 데이터까지 지우는 `docker compose down -v`는 로컬 DB를 완전히 초기화하려는 경우에만 사용합니다.

## 보안·데이터 한계

- `.env`는 로컬 개발 전용이며 저장소에 커밋하지 않습니다.
- 이 초기 API는 실사용자 계정 인증을 제공하지 않습니다. 운영 자료·개인 신체 정보·실구매 정보는 연결하지 않습니다.
- 카탈로그 검색 결과는 합성 상품입니다. 공식 공급원과 사용 권리가 정해지기 전까지 실제 브랜드 상품 피드를 연결하지 않습니다.
