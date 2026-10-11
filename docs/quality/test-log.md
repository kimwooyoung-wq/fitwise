# Test Log

## 사용 방법

이 문서는 검증 실행의 요약 기록이다. 상세 로그와 개인정보 제거 증빙은 GitHub Actions 또는 해당 PR에 두고 여기에는 재현에 필요한 정보와 결과만 남긴다.

새 실행은 기존 실패 기록을 수정하거나 삭제하지 않고 표의 위쪽에 추가한다.

## 실행 기록

| 실행일 | 범위 | 환경·버전 | 명령·시나리오 | 결과 | 증빙 | 후속 작업 |
|---|---|---|---|---|---|---|
| 2026-10-11 | 전체 회귀·문서 품질 | local · `feat/3-mobile-search-prototype` | `npm run lint`; `npm run typecheck`; `npm test`; `python -m pytest -q`; 문서 링크·비밀값 패턴 | PASS · 모바일 3개, API 5개 | PR #4 | 실기기·RLS·restore는 환경 도입 후 수행 |
| 2026-10-11 | API 테스트 의존성 | Windows sandbox · Python 3.12 | API 5개 수집 후 첫 `TestClient` 요청 | BLOCKED → PASS | `services/api/requirements-dev.txt` | 누락된 `httpx` 추가, `httpx2` 유지; socketpair 제한 밖에서 5개 재검증 |

## 실행 상세 템플릿

```md
### YYYY-MM-DD · 테스트 이름

- 실행자:
- 환경·기기:
- commit / PR:
- 테스트 데이터:
- 명령 또는 수동 절차:
- 기대 결과:
- 실제 결과:
- 결과: PASS / FAIL / BLOCKED
- 테스트 개수:
- 경고:
- 증빙:
- 관련 Issue:
- 수정 PR:
- 재검증일:
- 미실행 검사와 이유:
- 사람이 확인할 항목:
```

## 기록 금지

- 비밀번호, API 키, 토큰과 세션 값
- 실제 사용자의 이름, 연락처, 신체정보, 검색 원문과 사진
- 마스킹되지 않은 stack trace나 운영 DB row
- 이용 권한이 확인되지 않은 상품 이미지와 후기 원문

필요한 경우 내부 난수 ID, 오류 코드와 `request_id`만 남긴다.
