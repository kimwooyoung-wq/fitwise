# FITWISE 보안 벤치마크와 실행 계획

> 작성일: 2026-10-12 · 공개 문서와 정책을 바탕으로 한 설계 검토이며 개별 서비스의 보안 감사를 의미하지 않는다.

## 보호 대상과 위협

FITWISE가 다루게 될 가능성이 있는 체형·평소 사이즈, 옷장 사진, 구매·검색 이력과 추천 피드백은 계정 식별자와 결합되면 개인의 생활 패턴과 취향을 드러낼 수 있다. 주요 위협은 다음과 같다.

- 다른 사용자의 프로필·옷장·추천 이력에 대한 수평 권한 상승
- 공개 버킷, 예측 가능한 URL과 과도한 로그를 통한 사진·검색 원문 노출
- 앱 번들에 포함된 서비스 역할 키 또는 데이터베이스 비밀번호 유출
- 상품·리뷰 수집 파이프라인을 통한 악성·오염 데이터 유입
- AI 설명이 실제 가격·재고·실측·후기를 사실처럼 생성하는 오류
- 계정 삭제 후 캐시, 검색 색인, 파생 데이터와 백업에 남는 잔존 데이터

## 공식 기준

| 기준 | FITWISE 적용 |
|---|---|
| [OWASP MASVS](https://mas.owasp.org/MASVS/) | STORAGE, CRYPTO, AUTH, NETWORK, PLATFORM, CODE, RESILIENCE, PRIVACY를 모바일 출시 체크리스트로 사용한다. |
| [OWASP MASVS Privacy](https://mas.owasp.org/MASVS/12-MASVS-PRIVACY/) | 민감 데이터와 기기 자원 접근을 최소화하고 실제 수집 행위가 공개 정책과 일치하는지 검증한다. |
| [개인정보보호위원회 안전성 확보조치 안내서](https://pipc.go.kr/np/cop/bbs/selectBoardList.do?bbsId=BS217&etc1=%EA%B3%BC%EA%B1%B0+%EC%95%88%EB%82%B4%EC%84%9C&mCode=G010030030) | 접근권한, 접근통제, 암호화, 접속기록, 악성프로그램 방지, 재해 대비와 파기를 운영 기준에 반영한다. 법적 의무의 최종 판단은 출시 지역과 처리 형태가 확정된 뒤 전문가 검토를 받는다. |
| [Supabase 데이터 보안](https://supabase.com/docs/guides/database/secure-data) | 공개 키는 RLS·최소 권한과 함께 사용하고 service role·secret key는 앱에 넣지 않는다. |
| [Supabase RLS](https://supabase.com/docs/guides/database/postgres/row-level-security) | 모든 사용자 소유 행에 `auth.uid()` 기반 소유권 검사를 적용하고 사용자 수정 가능한 metadata를 권한 판단에 사용하지 않는다. |
| [Supabase Storage 접근 제어](https://supabase.com/docs/guides/storage/security/access-control) | 옷장 사진은 비공개 버킷과 사용자별 경로 정책을 사용하며 업로드·조회·수정·삭제를 각각 테스트한다. |

## 유사 서비스 공개 정책에서 얻은 교훈

| 서비스 | 공개 정책에서 확인한 내용 | FITWISE 결정 |
|---|---|---|
| [Acloset](https://www.acloset.app/privacy/) | 프로필·사이즈·업로드 콘텐츠 등 수집 항목과 사용 목적, 암호화·접근통제 방침을 설명하며 결제는 플랫폼 사업자가 처리한다고 밝힌다. | 기능별 수집 목적을 분리하고 결제 도입 시 카드 원문을 직접 저장하지 않는다. 필요한 데이터만 점진적으로 요청한다. |
| [Whering](https://www.whering.co/privacy-policy) | 의류 사진, 기기·사용 정보를 목적과 보존기간별로 설명하고 계정 삭제 후 처리 기간을 공개한다. | 데이터 사전에 목적·보존기간·삭제 경로를 필수 필드로 둔다. 분석 로그는 짧은 보존을 기본으로 한다. |
| [Whering 공개 범위 정책](https://whering.co.uk/privacy) | 계정과 업로드 콘텐츠를 기본 비공개로 두고 공개 전환 시 재공유 위험을 알린다. | FITWISE 옷장과 추천 이력은 기본 비공개다. 커뮤니티 기능은 MVP에서 제외하고, 향후 공개 시 항목별 명시 동의를 받는다. |

서비스 정책은 각 사업자가 공개한 설명일 뿐 실제 구현의 안전성을 보증하지 않는다. FITWISE는 정책 문구 복사 대신 자동화된 거부 테스트와 삭제 검증으로 통제를 증명한다.

## 단계별 보안 구조

```text
Expo app
  -> TLS API / short-lived user token
FastAPI
  -> input validation / rate limit / request_id / authorization
PostgreSQL
  -> constraints / RLS / least privilege / audit events
Private object storage
  -> MIME·size validation / user path policy / expiring signed URL
AX pipeline
  -> licensed input / schema validation / quarantine / versioned output
```

### 앱과 인증

- 비밀번호를 직접 저장하지 않고 관리형 인증을 사용한다.
- 액세스 토큰은 OS 보안 저장소에 두고 일반 `AsyncStorage`와 로그에 남기지 않는다.
- 딥링크와 OAuth redirect URI를 허용 목록으로 제한한다.
- 세션 만료·탈취 의심 시 서버에서 폐기할 수 있게 하고, 관리자 기능에는 MFA를 적용한다.

### API와 SQL

- 모든 객체 조회는 `resource.user_id == authenticated_user_id`를 서버와 RLS에서 이중 확인한다.
- 입력 길이·형식·열거값·파일 크기를 API 경계에서 제한하고 SQL은 매개변수화한다.
- 추천 요청과 피드백 쓰기는 idempotency key와 transaction을 사용한다.
- 401·403·404 응답으로 다른 사용자 자원의 존재가 추정되지 않도록 계약을 통일한다.
- 관리자·수집 작업은 일반 사용자 역할과 별도 DB 역할을 사용한다.

### 사진과 상품 데이터

- 옷장 사진은 EXIF를 제거하고 허용 MIME을 재검사한 뒤 비공개 버킷에 저장한다.
- 원본 사진의 공개 URL을 만들지 않고 짧은 만료의 서명 URL을 사용한다.
- 외부 상품·리뷰는 출처와 사용권한이 확인된 피드만 수집하고 검증 실패 데이터는 격리한다.
- 이미지 프록시는 SSRF 방지를 위해 허용 도메인, 크기, redirect와 content type을 제한한다.

### AI·AX

- 개인정보 원문을 외부 모델에 보내지 않는 것이 기본이며 필요 시 제공자·목적·보존·학습 사용 여부를 먼저 확정한다.
- 프롬프트에는 데이터가 아니라 최소화된 구조화 속성을 사용한다.
- 가격·재고·실측·후기는 결정적 데이터 소스만 인용하고 모델이 생성하지 못하게 한다.
- prompt injection 문자열은 지시가 아닌 데이터로 처리하고 도구 호출·데이터 변경은 허용 목록과 사람 승인으로 제한한다.

### 로그·사고 대응·삭제

- 로그는 `request_id`, 오류 코드, 앱/API/모델 버전과 최소 성능 지표만 기본 수집한다.
- 이메일, 토큰, 검색 원문, 신체정보, 사진 URL과 설문 원문은 로그·Sentry·PR에서 제거한다.
- 보안 이벤트는 심각도, 탐지 시각, 영향 범위, 차단, 복구, 통지 판단과 재발 방지를 기록한다.
- 계정 삭제 작업은 DB, Storage, 캐시, 검색 색인과 파생 데이터별 상태를 추적하고 실패를 재시도한다.

## 구현 순서와 출시 게이트

### 지금 — 프로토타입

- 합성 상품과 비식별 집계 데이터만 사용한다.
- `.env.example`만 커밋하고 비밀값 패턴 검사를 CI에 유지한다.
- API 입력 검증, 안전한 오류 응답과 의존성 취약점 추적을 적용한다.

### 인증·데이터베이스 도입 PR

- 데이터 사전과 위협 모델을 확정한다.
- RLS 정책과 익명·본인·타인·관리자 허용/거부 테스트를 함께 제출한다.
- Storage 정책, EXIF 제거, 업로드 제한과 삭제 작업을 테스트한다.
- migration, 백업과 별도 환경 restore 증빙을 남긴다.

### 비공개 베타 전

- OWASP MASVS 체크와 API 권한 테스트를 수행한다.
- 운영 비밀값을 교체하고 Git history·앱 번들·로그 노출을 검사한다.
- 개인정보 처리방침, 보존기간, 계정·데이터 삭제 경로를 실제 동작과 일치시킨다.
- 사고대응 연락·중지·복구 절차와 모니터링 알림을 리허설한다.

다음 중 하나라도 실패하면 배포하지 않는다: 타인 데이터 접근, 공개 사진 URL, service role 키의 앱 포함, 삭제 잔존 데이터, 로그의 민감값, 근거 없는 AI 사실 생성.

