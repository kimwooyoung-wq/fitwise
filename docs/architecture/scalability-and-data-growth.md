# 데이터 증가와 앱 성능 계획

> 상태: 기준선 v0 · 실제 측정 전 수치는 제안값이며 부하·실기기 결과로 조정한다.
> 기준일: 2026-10-13
> 관련 요구사항: FW-OPS-001, FW-DATA-001, FW-CATALOG-001, FW-QUALITY-001

## 결론

상품과 사용 기록이 늘어도 전체 데이터를 앱에 내려받지 않는다. FITWISE는 `서버에서 좁히기 → 필요한 필드만 페이지 단위로 전송 → 화면에 보이는 항목만 렌더링 → 삭제 가능한 캐시 사용`을 기본 원칙으로 한다. Redis, OpenSearch, 테이블 파티셔닝은 처음부터 넣지 않고 PostgreSQL과 앱의 측정값이 기준을 넘을 때만 도입한다.

“앱이 무거워진다”는 문제는 다음 네 가지를 따로 측정한다.

| 영역 | 대표 증상 | 먼저 할 일 |
|---|---|---|
| 설치 파일·JS bundle | 설치·업데이트와 첫 실행이 느림 | Expo Atlas로 릴리스 bundle의 증가 원인 확인, 사용하지 않는 의존성 제거 |
| 런타임 메모리·렌더링 | 긴 목록 스크롤 끊김, 종료 | 가상화 목록, 가벼운 셀, 썸네일, 릴리스 빌드 실기기 프로파일링 |
| 네트워크·이미지 | 화면 진입과 이미지 표시가 느림 | 필드 선택, cursor pagination, CDN 썸네일, 디스크 캐시와 만료 정책 |
| DB·검색 | 검색 p95 증가, 동기화 지연 | `EXPLAIN ANALYZE`, 실제 조회 패턴 인덱스, 증분 수집과 격리 큐 |

## 클라이언트 데이터 예산

- 검색 결과는 한 번에 20개를 기본으로 하고 API hard limit은 50개로 둔다.
- 추천은 서버가 30~50개 후보를 검색·평가한 뒤 상위 3개와 근거만 앱에 보낸다.
- 상품 목록에는 카드에 필요한 필드만 보내고, 실측표·후기 요약·긴 설명은 상세 진입 시 요청한다.
- 목록은 `FlatList`로 시작하고 실제 저사양 기기에서 문제가 재현될 때 `FlashList` 전환을 검토한다.
- 이미지 원본을 목록에서 사용하지 않는다. 공급처가 허용한 썸네일 또는 변환본을 사용하고 `expo-image`의 disk 또는 memory-disk cache와 placeholder를 적용한다.
- 앱 캐시는 최근 검색 조건, 비민감 UI 설정과 만료 가능한 응답만 보관한다. PostgreSQL을 대체하거나 신체정보·사진 URL·토큰을 일반 캐시에 저장하지 않는다.
- 캐시에는 `schema_version`, `fetched_at`, `expires_at`을 두고 로그아웃·계정 삭제·스키마 변경 시 관련 항목을 제거한다.

React Native 공식 문서는 큰 목록에서 화면 주변 항목만 유지하는 가상화와 배치 크기·window 크기의 메모리/응답성 절충을 설명한다. Shopify의 FlashList는 셀 재활용을 사용하며 릴리스 모드에서 측정할 것을 요구한다. Expo Image는 디스크·메모리 캐시, placeholder와 이미지 크기 제한을 지원한다.

## 서버와 DB 증가 대응

### 1. PostgreSQL 우선

초기에는 정규화된 PostgreSQL과 측정된 쿼리용 인덱스로 충분한지 먼저 검증한다.

- 무제한 조회와 `SELECT *`를 금지한다.
- 정렬이 안정적인 `id` 또는 `observed_at + id` cursor pagination을 사용한다.
- 사용자 소유 데이터에는 `owner_id`와 조회 조건을 함께 고려한 인덱스를 검토한다.
- 상품 검색은 카테고리·가격·판매 가능·사이즈 같은 hard filter를 먼저 적용한다.
- 인덱스 추가 전후 실행 계획과 p95를 기록하고 사용하지 않는 인덱스는 제거한다.
- RLS 정책에 쓰이는 열도 실제 실행 계획을 확인한다.

PostgreSQL은 인덱스가 조회를 빠르게 하지만 쓰기·저장 비용도 늘리므로 신중히 사용하라고 안내한다. Supabase 역시 실제 쿼리 계획을 분석하고 조회 패턴에 맞는 인덱스를 선택하는 접근을 권장한다.

### 2. 수집은 전체 교체가 아니라 증분 처리

- 공급처 cursor와 checksum을 저장한다.
- 추가·변경·품절·삭제를 구분하고 같은 배치를 재처리해도 중복이 생기지 않게 한다.
- 원본 snapshot은 객체 저장소에 압축 보관하고 DB에는 정규화 값과 원본 참조만 둔다.
- 실패 레코드는 전체 배치를 막지 않고 quarantine으로 보내 재처리한다.
- 가격·재고·판매 링크에는 최신 시각과 만료 상태를 둔다.
- 앱은 브랜드 API를 직접 호출하지 않고 FITWISE API의 안정된 계약만 사용한다.

Google Merchant API도 상품을 고유 식별자로 추가·갱신·삭제하고, 대량 업로드는 비동기 병렬 요청을 지원한다. Shopify Storefront API는 전체 목록 대신 cursor 기반 페이지 정보를 제공한다. FITWISE는 이 패턴을 참고하되 접근 권한이 있는 파트너 데이터만 사용한다.

### 3. 확장 기술 도입 조건

| 기술 | 지금 상태 | 도입 검토 신호 |
|---|---|---|
| 복합 인덱스·partial index | 필요 쿼리부터 도입 | 반복되는 slow query가 실행 계획에서 확인됨 |
| read replica | 미도입 | 읽기 부하가 쓰기와 경합하고 DB 튜닝 후에도 SLO 실패 |
| Redis | 미도입 | 같은 비민감 결과의 반복 계산·rate limit·작업 큐 요구가 측정됨 |
| OpenSearch | 미도입 | PostgreSQL 검색이 목표 p95를 지속적으로 넘고 검색 기능이 병목으로 확인됨 |
| 테이블 파티셔닝 | 미도입 | 시간 기반 대용량 로그·가격 snapshot에서 삭제·조회 비용이 측정됨 |
| CDN 이미지 변환 | 파트너 권리 확인 후 | 이미지 전송이 화면 지연·트래픽의 주원인으로 확인됨 |

파티셔닝은 데이터가 많다는 이유만으로 적용하지 않는다. PostgreSQL 공식 문서도 잘못된 파티션 키와 과도한 파티션 수가 계획·실행 성능을 악화시킬 수 있다고 설명한다.

## 단계별 데이터 규모 검증

| 단계 | 합성·허가 데이터 | 필수 검증 |
|---|---:|---|
| Prototype | 20~50개 | API 계약, 빈 결과·오류·재시도, 목록 메모리 누수 없음 |
| Stage 0 catalog | 200~500개 | 검색 p95 300ms 이하, 필수 필드 누락 0, 중복 재처리 0 |
| Foundation 부하검사 | 10,000개 합성 데이터 | pagination 고정, 실행 계획 기록, 앱에 전체 응답 미전송 |
| Scale rehearsal | 100,000개 합성 데이터 | 병목 위치와 비용 확인; 검색엔진·파티셔닝 필요 여부 결정 |

10,000개와 100,000개는 운영 카탈로그 목표가 아니라 구조가 선형으로 악화되는 지점을 찾기 위한 합성 부하 데이터다.

## 성능 예산과 차단 조건

| 지표 | 제안 기준 | 실패 시 처리 |
|---|---:|---|
| 검색 API p95 | Stage 0 로컬 seed 300ms 이하 | 쿼리 계획·payload·직렬화 순서로 분석 |
| 핵심 API p95 | 출시 후보 1초 이하 | 기능 확장 중지, 병목 수정 |
| 추천 카드 수 | 기본 3개 | 더 많은 목록보다 비교 근거 개선 |
| 목록 요청 크기 | 기본 20, 최대 50 | 서버 hard limit 적용 |
| JS bundle 변화 | 기준선 대비 PR 단위 10% 초과 시 설명 필요 | Atlas 결과와 필요 의존성 증빙 |
| 긴 목록 스크롤 | 릴리스 빌드에서 눈에 띄는 blank·입력 지연 없음 | 셀 단순화·이미지 축소·가상화 조정 |
| 메모리 | 반복 검색 20회 후 지속 증가하지 않음 | 캐시·listener·이미지 참조 누수 조사 |

수치는 실제 기기 기준선을 만들기 위한 시작값이다. 개발 모드 측정으로 통과를 주장하지 않는다.

## 경쟁·상용 플랫폼에서 확인한 패턴

내부 시스템을 공개하지 않은 서비스의 아키텍처를 추정하지 않는다. 다음은 공개 화면 또는 공식 개발 문서로 확인 가능한 패턴이다.

| 공개 근거 | 확인 가능한 패턴 | FITWISE 적용 |
|---|---|---|
| MUSINSA 카테고리 | 수천 개 상품을 가격·사이즈·핏·스타일 등 구조화 필터로 좁힘 | 자연어 조건을 같은 hard filter로 변환 |
| SSF SHOP FAQ·상품 리뷰 | 신체·평소 사이즈로 후기 필터, 구매·찜 상품과 사이즈 비교 | 동의된 데이터만 사용한 근거형 사이즈 비교 |
| 29CM 콘텐츠 | 에디터 맥락과 소수 추천 상품을 연결 | 무한 목록보다 상황별 3개 후보와 설명 |
| Zigzag 판매자 정책 | 색상·사이즈 옵션과 상품 품질 기준을 공급자가 관리 | 공급처 검증·격리와 필수 필드 계약 |
| ABLY 공개 자료 | 관심사·상품 조회·구매 이력 기반 개인화를 설명 | 암묵 행동보다 먼저 명시적 선택·제외 피드백 검증 |
| Shopify Storefront API | cursor pagination과 필요한 상품 필드 조회 | 파트너별 어댑터 뒤의 공통 페이지 계약 |
| Google Merchant API | 고유 ID 기반 상품 수명주기와 갱신 | source ID·checksum·tombstone·최신성 관리 |

MUSINSA·29CM·SSF SHOP의 사용성 결과와 W CONCEPT·Zigzag·ABLY 앱 과업 결과는 [경쟁 서비스 검증 계획](../research/competitive-analysis.md)에 별도로 기록한다. 공개 마케팅 자료를 실제 성능이나 추천 품질의 증명으로 사용하지 않는다.

## 구현 체크리스트

- [ ] API 목록 계약에 cursor, `has_more`, hard limit과 허용 정렬 정의
- [ ] 상품 카드 DTO와 상세 DTO 분리
- [ ] 이미지 썸네일·캐시·만료·삭제 정책 정의
- [ ] 500·10,000·100,000개 합성 seed 생성 절차 작성
- [ ] DB slow query와 앱 bundle·메모리·scroll 측정 스크립트 추가
- [ ] 성능 결과를 `docs/quality/test-log.md`에 기록
- [ ] 기준 초과 시 기능 추가보다 병목 수정 PR을 우선

## 공식 참고 자료

- React Native FlatList 최적화: <https://reactnative.dev/docs/optimizing-flatlist-configuration>
- Shopify FlashList 성능: <https://shopify.github.io/flash-list/docs/fundamentals/performance/>
- Expo Image: <https://docs.expo.dev/versions/latest/sdk/image/>
- Expo bundle 분석: <https://docs.expo.dev/guides/analyzing-bundles/>
- Supabase query optimization: <https://supabase.com/docs/guides/database/query-optimization>
- Supabase Storage scaling: <https://supabase.com/docs/guides/storage/production/scaling>
- PostgreSQL indexes: <https://www.postgresql.org/docs/current/indexes.html>
- PostgreSQL partitioning: <https://www.postgresql.org/docs/current/ddl-partitioning.html>
- Shopify products pagination: <https://shopify.dev/docs/api/storefront/latest/queries/products>
- Google Merchant product lifecycle: <https://developers.google.com/merchant/api/guides/products/add-manage>
