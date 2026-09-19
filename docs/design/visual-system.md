# FITWISE Visual System

## Direction

FITWISE의 디자인은 패션 에디토리얼의 절제된 분위기와 의사결정 도구의 명확성을 결합한다. 특정 브랜드의 화면을 복제하지 않고, 큰 이미지와 타이포그래피, 제한된 색상, 설명 가능한 데이터를 통해 독립적인 정체성을 만든다.

## Principles

### Editorial, not decorative

장식보다 이미지, 타이포그래피와 여백으로 분위기를 만든다. 그림자, 그라데이션과 불필요한 카드 사용을 최소화한다.

### Evidence before persuasion

높은 추천 점수만 강조하지 않는다. 추천 이유, 주의점, 데이터 범위와 신뢰도를 함께 보여준다.

### Less, but relevant

무한 상품 목록보다 목적이 분명한 소수의 선택지를 제공한다. 사용자가 더 보고 싶을 때 탐색 범위를 확장할 수 있게 한다.

### Mobile first

핵심 작업은 한 손으로 완료할 수 있어야 한다. 터치 대상은 최소 44px, 본문은 최소 16px를 기준으로 한다.

## Color

| Token | Value | Usage |
|---|---|---|
| Ink | `#111111` | 본문, 주요 버튼, 강한 대비 |
| Canvas | `#F7F7F4` | 기본 배경 |
| Surface | `#FFFFFF` | 이미지·정보 영역 |
| Muted | `#6B6B66` | 보조 정보 |
| Line | `#D9D9D4` | 구분선과 입력 경계 |
| Signal | `#D8FF3E` | 선택, 진행 상태, 핵심 신호 |
| Success | `#16794A` | 확인 완료와 긍정 상태 |
| Danger | `#D93F3F` | 오류와 경고 |

Signal 색상은 한 화면 면적의 약 10% 이하로 제한한다.

## Typography

| Role | Desktop | Mobile | Weight |
|---|---:|---:|---:|
| Display | 64px | 40px | 600 |
| Page title | 40px | 32px | 600 |
| Section title | 28px | 24px | 600 |
| Card title | 18px | 18px | 600 |
| Body | 16px | 16px | 400 |
| Caption | 13px | 13px | 400 |

- 한글: Pretendard
- 영문 및 숫자: Inter
- 본문 행간: 1.55~1.65
- 영문 디스플레이 문구는 필요할 때 대문자를 사용하되, 본문 전체에는 사용하지 않는다.

## Layout

- Desktop maximum width: `1440px`
- Reading content width: `720px`
- Desktop grid: 12 columns
- Tablet grid: 8 columns
- Mobile grid: 4 columns
- Product image ratio: `3 / 4`
- Spacing scale: `4, 8, 12, 16, 24, 32, 48, 64, 96`
- Radius scale: `0, 4, 8px`

## Components

### Buttons

- Primary: Ink 배경, 흰색 텍스트
- Secondary: 투명 배경, Ink 테두리
- Selected: Signal 배경, Ink 텍스트
- 높이: 모바일 최소 48px
- 모서리: 4px 또는 각진 형태

### Product cards

상품 이미지를 가장 큰 정보로 사용한다. 상품명, 가격과 핵심 적합도만 노출하고 세부 근거는 상세 화면에서 제공한다. 카드 전체에 그림자를 사용하지 않는다.

### Confidence

신뢰도는 색상만으로 전달하지 않는다. 숫자, 레이블과 근거 문장을 함께 표시한다.

```text
사이즈 신뢰도 84% · 높음
유사 체형 리뷰 32개와 상품 실측을 기준으로 계산했습니다.
```

### Recommendation strategies

추천 결과는 다음 세 가지 전략을 일관되게 사용한다.

- Safe Choice — 실패 가능성을 낮춘 선택
- Balanced Choice — 가격과 스타일의 균형
- Bold Choice — 취향을 더 선명하게 표현

## Avoid

- 보라색 AI 그라데이션과 반짝이는 AI 아이콘
- 모든 내용을 둥근 카드에 넣는 구성
- 의미 없는 점수와 검증되지 않은 정확도
- 이미지 위에 긴 설명을 겹치는 구성
- 색상만으로 상태를 구분하는 방식
- 특정 패션 브랜드의 로고, 카피와 화면을 그대로 복제하는 방식

## Accessibility

- 일반 텍스트 대비는 WCAG AA 기준을 만족한다.
- 키보드만으로 주요 흐름을 완료할 수 있어야 한다.
- 포커스 상태를 명확히 표시한다.
- 이미지에 의미 있는 대체 텍스트를 제공한다.
- 애니메이션 감소 설정을 존중한다.
