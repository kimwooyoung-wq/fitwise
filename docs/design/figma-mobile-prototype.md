# FITWISE Figma Mobile Prototype v0

> 상태: **디자인 검증 전 초안**  
> Figma: https://www.figma.com/design/QwbVZABZL9cgxVNepWCO0T  
> 기준일: 2026-10-14 KST

## 목적

최종 설문 21건에서 우선순위로 확인된 `사이즈·핏 판단`, `여러 후보 비교`, `흩어진 정보 결합` 문제를 하나의 모바일 흐름으로 시각화했다. 이 파일은 구현 방향과 사용자 과업을 검토하기 위한 편집 가능한 디자인 산출물이며, 추천 정확도나 제품 효과가 검증됐다는 의미가 아니다.

## 화면 구성

| 화면 | 검증하려는 질문 | 핵심 요소 |
|---|---|---|
| `01 · Intent Search` | 사용자가 상황·예산을 짧게 입력할 수 있는가 | 자연어 검색, 예산, 빠른 조건 |
| `02 · Recommendation Results` | 무한 목록 대신 세 전략을 이해할 수 있는가 | Safe·Balanced·Bold, 추천 이유, 주의점 |
| `03 · Fit Evidence` | 사이즈 제안과 불확실성을 함께 이해하는가 | 추천 사이즈, 신뢰도, 실측·후기 근거 |
| `04 · Wardrobe Match` | 기존 옷과의 조합이 결정에 도움이 되는가 | 보유 의류 조합, 활용도, 중복 위험 |

```text
상황·예산 입력
  → 세 가지 추천 전략 비교
  → 사이즈·핏 근거 확인
  → 보유 의류와 조합 확인
```

## 시각 기준

| Token | Value | Use |
|---|---|---|
| Canvas | `#070708` | 전체 배경 |
| Surface | `#121214` | 카드·바텀 영역 |
| Elevated | `#1B1B1F` | 강조 카드 |
| Signal | `#D8FF3E` | 주요 행동·선택 상태 |
| Text Primary | `#F5F5F7` | 제목·핵심 정보 |
| Text Secondary | `#9B9BA1` | 보조 설명 |

Figma에서는 한글 렌더링 일관성을 위해 `Noto Sans KR`을 사용했다. 앱 구현은 별도 결정이 없으면 Expo·React Native의 플랫폼 시스템 폰트를 유지한다.

## 데이터와 개인정보 원칙

- 모든 상품명, 가격, 점수와 체형 정보는 합성 예시다.
- 실제 브랜드 이미지, 사용자 사진, 연락처와 설문 원문을 포함하지 않는다.
- 추천 사이즈는 의료적·절대적 판단이 아니라 근거와 불확실성을 함께 보여주는 설명 예시다.
- 운영 데이터 연결 전 데이터 출처, 이용 권한, 갱신 시각과 삭제 정책을 먼저 검증한다.

## 구조 검증 결과

- 모바일 화면 4개 생성
- 버튼 상태를 재사용 가능한 component set으로 구성
- `FITWISE / Dark v0` 토큰 컬렉션 생성
- 텍스트 64개가 모두 `Noto Sans KR`을 사용하는지 검사: **PASS**
- 전체 화면 시각 점검과 카드 넘침 수정: **PASS**

## 남은 검증

1. 5명에게 동일한 구매 상황을 주고 검색 입력부터 후보 선택까지 수행시킨다.
2. 추천 이유 이해 여부, 후보 선택 완료, 선택 시간과 혼란 지점을 기록한다.
3. 로딩·빈 결과·오류·재시도 화면은 코드 프로토타입에서 확인하고 Figma에는 검증 결과에 따라 추가한다.
4. 테스트 후에만 문구, 정보 우선순위와 다음 구현 범위를 확정한다.

관련 문서: [Mobile Search Prototype](../architecture/mobile-search-prototype.md) · [Usability Test Plan](../research/usability-test-plan.md) · [Visual System](visual-system.md)
