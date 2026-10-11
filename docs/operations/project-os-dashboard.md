# WOOYOUNG PROJECT OS 대시보드 작업 및 점검 기록

> 최종 점검일: 2026-10-11 KST
> 공개 화면: https://wooyoung-project-os.w00young09111.chatgpt.site

## 목적

여러 프로젝트의 GitHub 저장소와 개인 실행 루틴을 한 화면에서 확인하기 위한 다크 테마 프로젝트 홈이다. FITWISE 개발 과정에서는 현재 과제 접근, 집중 세션 실행, 일일 루틴 및 주간 목표 확인에 사용한다.

## 구현된 영역

| 영역 | 구현 내용 | 점검 결과 |
|---|---|---|
| 메인 화면 | 다크 패션 무드의 반응형 홈, 동적 배경 및 실시간 서울 시간 | 정상 |
| 집중 세션 | 25분 집중, 5분 휴식, 15분 긴 휴식, 시작·일시정지·초기화 | 정상 |
| 상태 보존 | 타이머, 루틴, 주간 목표를 브라우저 `localStorage`에 저장 | 정상 |
| 일일 루틴 | 6개 루틴 체크 및 완료율 자동 계산 | 정상 |
| 주간 목표 | 3개 목표 체크 및 완료 개수 표시 | 정상 |
| GitHub Tasks | 저장소별 열린 Issue 표시, 진행 중·남은 과제 분류, 저장소 필터 | 정상·제한사항 참고 |
| Quick Access | FITWISE, SafeLink, SafeRoad, 인생게임 저장소 바로가기 | 정상 |
| 접근성·레이아웃 | 버튼 레이블, 새 창 링크 보호 속성, 가로 넘침 여부 확인 | 정상 |

## 비공개 Notion 운영 구조

Notion은 코드나 상세 로그의 원본이 아니라 개인 진행 상태를 빠르게 확인하는 보조 화면이다.

| 페이지 | 역할 | GitHub 기준 |
|---|---|---|
| `09 / PROJECT CONTROL CENTER` | 작업명, 상태, 우선순위, 마감일, 담당자, Issue·PR 링크 | Issue와 PR |
| `10 / ENGINEERING CONTROL CENTER` | 데이터·SQL·UI/UX·개인정보·보안·AX 품질 기준 요약 | `docs/architecture/engineering-quality-plan.md` |
| `TEST & INCIDENT LOG` | 테스트·오류·재검증 상태와 증빙 링크 | `docs/quality/test-log.md`, Actions, PR |

테스트 표는 `테스트 / 오류명`, `상태`, `구분`, `실행일`, `환경`, `결과`, `심각도`, `Commit / PR`, `담당자`, `증빙`, `재검증일` 속성을 사용한다. 실제 개인정보, 토큰, 전체 stack trace와 운영 데이터는 Notion에 복사하지 않는다.

## 연결된 저장소

- FITWISE: https://github.com/kimwooyoung-wq/fitwise
- SafeLink: https://github.com/sunhan2002-cyber/safelink
- SafeRoad: https://github.com/hansung-SafeRoad/saferoad
- 인생게임: https://github.com/sunhan2002-cyber/hansung-lifegame

## 2026-10-08 동작 점검

- 집중 타이머 시작 후 `24:59`로 감소하는 것을 확인했다.
- 타이머 일시정지와 초기화 후 `25:00` 복원을 확인했다.
- 일일 루틴 1개 체크 시 완료율이 `17%`, 해제 시 `0%`로 돌아오는 것을 확인했다.
- 주간 목표 1개 체크 시 `1 / 3`, 해제 시 `0 / 3`으로 돌아오는 것을 확인했다.
- SafeLink 필터에서 열린 Issue가 없을 때 빈 상태 화면을 확인했다.
- SafeRoad 필터에서 열린 Issue 4개가 표시되는 것을 확인했다.
- 네 프로젝트 카드의 GitHub 주소와 새 창 열기 설정을 확인했다.
- 브라우저 콘솔 오류와 데스크톱 가로 스크롤이 없음을 확인했다.

## GitHub 과제 표시 기준

- 공개 GitHub Issues API 호출이 가능한 환경에서는 5분 간격으로 최신 열린 Issue를 불러온다.
- `진행`, `in progress`, `doing`, `wip`, `작업 중` 라벨이 있으면 **진행 중**으로 분류한다.
- 나머지 열린 Issue는 **남은 과제**로 분류한다.
- 앱 내 브라우저가 GitHub API를 제한하는 경우, 직접 확인한 백업 데이터와 확인 날짜를 표시한다.
- 열린 Issue가 없는 저장소에서는 해당 저장소의 GitHub Issues 화면으로 이동할 수 있다.

## 현재 제한사항

1. GitHub API가 차단된 환경에서는 자동 갱신 대신 점검 시점의 백업 데이터를 사용한다.
2. 타이머와 체크 상태는 현재 브라우저에만 저장되며 다른 기기와 동기화되지 않는다.
3. Issue 상태 분류 품질을 유지하려면 각 저장소에서 진행 상태 라벨을 일관되게 사용해야 한다.

## 다음 보완 후보

- 서버 측 GitHub 프록시 또는 GitHub App 연동으로 API 제한 환경에서도 실시간 동기화
- 프로젝트별 Issue 라벨 규칙 통일
- 사용자 계정 기반 타이머·루틴 데이터 동기화
- FITWISE 현재 주차 문서와 GitHub Issue의 자동 연결

