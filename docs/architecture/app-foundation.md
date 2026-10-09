# App Foundation Decision

## 목적

FITWISE가 `검색 → 추천 결과` 기술 프로토타입에서 실제 앱으로 확장될 때 필요한 저장소, 기술 스택, 데이터 경계와 도입 순서를 정한다. 한 명이 개발·운영할 수 있어야 하지만, 인증·보안·데이터 이력과 테스트 수준은 낮추지 않는다.

이 문서는 구현 기준을 제안하는 초안이다. 설문과 사용성 테스트로 첫 사용 사례가 확정되기 전에는 실제 브랜드 데이터, 결제, ERP 또는 복잡한 AI 인프라를 도입하지 않는다.

## 결정 요약

| 구분 | 선택 | 시점 | 이유 |
|---|---|---|---|
| 앱 | Expo SDK 57 · React Native · TypeScript · Expo Router | 지금 | Android·iOS를 한 코드베이스로 개발하고 현재 프로토타입을 유지 |
| API | FastAPI · Pydantic · Python | 지금 | OpenAPI 계약과 검증 규칙을 코드에서 함께 관리 |
| 관계형 데이터 | PostgreSQL on Supabase | Foundation 단계 | 사용자·상품·추천·피드백 간 관계와 변경 이력을 일관되게 관리 |
| 인증 | Supabase Auth | 개인 데이터 저장 직전 | 인증 식별자와 앱 프로필을 분리하고 세션 관리를 직접 구현하지 않음 |
| 이미지·파일 | Supabase Storage 비공개 버킷 | 옷장 사진 도입 시 | DB에는 메타데이터만, 원본 파일은 접근 정책이 있는 객체 저장소에 보관 |
| 기기 보안 저장 | Expo SecureStore | 로그인 도입 시 | 토큰처럼 민감한 작은 값을 OS 보안 저장소에 보관 |
| 기기 캐시 | AsyncStorage | 오프라인 UX 필요 시 | 비민감 설정·최근 조건만 캐시하며 원본 데이터로 사용하지 않음 |
| 오류 관제 | GitHub Issues → Sentry | 지금 → 비공개 베타 전 | 재현 가능한 개발 오류부터 관리하고 실제 앱 오류 수집은 동의·마스킹 후 도입 |
| CI | GitHub Actions · Vitest · Pytest | 지금 | PR마다 앱 정적 검사와 API 계약 회귀를 차단 |

## 목표 구조

```text
Expo mobile app
├── Expo Router                    화면·딥링크
├── domain / application           입력 검증·사용 사례
├── api client                     FastAPI 계약 소비
└── local storage                  SecureStore(민감) / Cache(비민감)
          │ HTTPS + user token
          ▼
FastAPI
├── request / response contract    Pydantic·OpenAPI
├── recommendation service         필터·점수·근거
├── repository layer               DB 접근 격리
└── observability                  request id·구조화 로그·오류 보고
          │ server credential
          ▼
Supabase
├── PostgreSQL                     제품의 Source of Truth
├── Auth                           사용자 인증
└── Storage                        옷장 사진·허가된 상품 이미지
```

모바일 앱은 서비스 역할 키나 DB 접속 문자열을 갖지 않는다. FastAPI가 추천과 수집 로직을 담당하고, 클라이언트가 Supabase Data API를 직접 사용하는 영역이 생기면 해당 테이블에 최소 권한과 Row Level Security(RLS)를 함께 적용한다.

## 저장소별 역할

### PostgreSQL — 제품 데이터의 최종 기준

다음처럼 관계, 제약 조건, 조회 이력이 중요한 데이터를 저장한다.

- 사용자 프로필과 선택 동의
- 옷장 아이템과 구조화된 속성
- 사용 권한과 출처가 확인된 상품·옵션·가격 스냅샷
- 추천 요청, 후보 점수, 노출한 근거와 신뢰도
- 저장·제외·구매 후 평가와 같은 명시적 피드백
- 외부 데이터 수집 실행 결과와 최신성

JSON은 원문 응답이나 실험 스냅샷처럼 구조가 아직 안정되지 않은 값에만 사용한다. 검색과 권한 판단에 쓰는 필드는 정규 컬럼으로 둔다.

### Supabase Storage — 파일

옷장 사진과 허가된 상품 이미지를 저장한다. DB에는 `bucket`, `object_path`, `owner_id`, `source`, `license_scope`, `created_at`, `deleted_at`만 저장한다. 사용자 옷장 사진은 공개 URL이 아닌 비공개 버킷과 만료되는 서명 URL을 기본으로 한다.

### 기기 저장소 — 최소 캐시

- SecureStore: 세션 토큰처럼 노출되면 안 되는 작은 값
- AsyncStorage: 테마, 비민감 필터, 최근 검색 초안
- 저장 금지: 서비스 역할 키, DB 비밀번호, 상세 신체정보 원본, 전체 추천 이력

앱 캐시는 언제든 삭제 가능한 복제본이며 PostgreSQL을 대체하지 않는다.

## 데이터 모델 v0

| 테이블 | 핵심 책임 | 민감도 |
|---|---|---|
| `profiles` | 사용자 ID, 선택적 신체·핏 선호, 동의 버전 | 높음 |
| `wardrobe_items` | 사용자 보유 의류 속성, 이미지 참조 | 높음 |
| `products` | 출처·권리·카테고리·브랜드 기준 정보 | 보통 |
| `product_variants` | 색상·사이즈·실측·재고 식별자 | 보통 |
| `price_snapshots` | 가격, 통화, 확인 시각 | 보통 |
| `recommendation_requests` | 목적·예산·필터·모델/규칙 버전 | 높음 |
| `recommendation_results` | 후보·세부 점수·근거·주의점·신뢰도 | 높음 |
| `feedback_events` | 저장·제외·선택·핏 평가 | 높음 |
| `data_sources` | 제공처, 이용 범위, 갱신 정책 | 보통 |
| `import_runs` | 수집 시각, 성공·실패·건수·오류 | 보통 |
| `audit_events` | 데이터 접근·삭제 등 보안상 필요한 사건 | 높음 |

모든 핵심 테이블은 UUID 기본키, `created_at`, `updated_at`을 갖고 사용자 소유 행은 `user_id`로 격리한다. 추천 결과에는 사용한 규칙/모델 버전과 입력 스냅샷을 남겨 같은 결과를 재현할 수 있게 한다.

## 프로토타입 전에 확정할 문서

### 반드시 작성

- MVP PRD: 첫 사용자, 첫 구매 상황, 포함·제외 범위, 성공 지표
- 사용자 흐름: 검색 입력 → 조건 확인 → 세 추천 → 근거 확인 → 피드백
- API 계약: 정상·빈 결과·검증 오류·서버 오류 응답
- 데이터 사전: 필드 정의, 단위, 필수 여부, 출처, 보존 기간, 민감도
- ERD v0와 삭제 흐름: 계정·옷장 사진·추천 이력 삭제 방식
- 권한표: 익명·본인·서버·관리자가 가능한 읽기/쓰기
- 오류 분류와 관제 절차: `docs/operations/error-management.md`
- 테스트 전략: 단위·계약·통합·E2E·실기기별 통과 기준

### 베타 전에 확정

- 개인정보 수집 동의와 보존·삭제 정책
- Supabase RLS 정책과 허용·거부 테스트
- 백업·복구 절차와 목표 복구 시간
- Sentry 필드 마스킹, 표본 비율, 사용자 동의 범위
- 상품 데이터 제공 계약, 이미지 권리와 갱신 실패 처리
- 추천 품질 고정 평가셋과 변경 전후 비교 기준

## 도입 순서

1. 현재 합성 데이터 프로토타입으로 흐름과 API 계약을 검증한다.
2. 설문·경쟁 분석을 끝내고 첫 사용 사례와 성공 지표를 확정한다.
3. SQL 마이그레이션으로 `profiles`, `products`, `recommendation_*`, `feedback_events` 최소 구조를 만든다.
4. 인증을 붙이고 사용자 소유 테이블에 RLS와 허용·거부 테스트를 작성한다.
5. 허가된 소규모 상품 데이터로 통합 테스트를 수행한다.
6. 옷장 사진이 실제로 필요할 때만 비공개 Storage 버킷을 연다.
7. 비공개 베타 전에 오류 관제, 삭제, 백업·복구를 검증한다.

## 의도적으로 보류하는 기술

- **pgvector**: 자연어/이미지 의미 검색이 규칙·SQL 검색보다 유효하다는 평가 결과가 생긴 뒤 도입한다.
- **Redis**: 측정된 지연, 캐시, 작업 큐 또는 rate limit 요구가 생기기 전에는 운영 대상을 늘리지 않는다.
- **ERP 전체 기능**: 상품·재고·주문을 직접 운영하는 사업 모델이 검증되기 전에는 공급 데이터 어댑터만 설계한다.
- **LLM 중심 추천**: 필터와 점수는 결정적으로 유지한다. LLM은 의도 구조화·설명 초안에 한정하고 실패 시 대체 경로를 둔다.
- **Next.js 웹 앱**: 모바일 핵심 흐름이 검증된 후 동일 API 계약을 재사용해 확장한다.

## 준비 완료 기준

- [ ] 첫 사용 사례와 비목표가 PRD에 적혀 있다.
- [ ] API 요청·응답·오류가 OpenAPI와 테스트로 고정돼 있다.
- [ ] 데이터 사전과 ERD v0에 소유자·출처·민감도·삭제 규칙이 있다.
- [ ] 개발·테스트·운영 환경과 비밀값이 분리돼 있다.
- [ ] RLS 정책과 허용·거부 테스트 계획이 있다.
- [ ] 실제 상품·이미지의 이용 권한과 갱신 정책이 확인돼 있다.
- [ ] 로딩·빈 결과·오류·재시도·오프라인 상태 기준이 있다.
- [ ] 오류 수집에서 신체정보·검색 원문·토큰이 제거된다.
- [ ] 사람이 수행할 실기기·접근성·개인정보 확인 항목이 정해져 있다.

## 공식 참고 자료

- [Expo Router introduction](https://docs.expo.dev/router/introduction/)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Supabase Database](https://supabase.com/docs/guides/database/overview)
- [Supabase Row Level Security](https://supabase.com/docs/guides/database/postgres/row-level-security)
- [Supabase Storage access control](https://supabase.com/docs/guides/storage/security/access-control)
