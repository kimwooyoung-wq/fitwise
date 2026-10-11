from uuid import uuid4

from .catalog import CATALOG
from .models import (
    InterpretedConditions,
    Recommendation,
    RecommendationRequest,
    RecommendationResponse,
    Strategy,
)

STRATEGY_LABELS = {
    Strategy.SAFE: "Safe choice",
    Strategy.BALANCED: "Balanced choice",
    Strategy.BOLD: "Bold choice",
}


def recommend(request: RecommendationRequest) -> RecommendationResponse:
    query_terms = set(request.query.replace(".", " ").split())
    eligible = [item for item in CATALOG if item["price"] <= request.budget_max]

    ranked = sorted(
        eligible,
        key=lambda item: (len(query_terms & item["tags"]), item["quality"], -item["price"]),
        reverse=True,
    )

    strategies = [Strategy.SAFE, Strategy.BALANCED, Strategy.BOLD]
    recommendations = []
    for strategy, item in zip(strategies, ranked[:3], strict=False):
        overlap = sorted(query_terms & item["tags"])
        reasons = [f"예산 {request.budget_max:,}원 이내"]
        reasons.append(f"입력 조건과 일치: {', '.join(overlap)}" if overlap else "기본 상황 태그와 카테고리 조건 충족")
        if "검은 슬랙스" in item["tags"]:
            reasons.append("검은 슬랙스와 조합 가능한 색상 가설")

        recommendations.append(
            Recommendation(
                id=item["id"],
                strategy=strategy,
                strategy_label=STRATEGY_LABELS[strategy],
                title=item["title"],
                brand=item["brand"],
                category=item["category"],
                price=item["price"],
                confidence=min(item["quality"], 0.9),
                reasons=reasons,
                cautions=[item["caution"], "실제 브랜드 상품과 재고는 연결되지 않았습니다."],
            )
        )

    return RecommendationResponse(
        request_id=str(uuid4()),
        interpreted_conditions=InterpretedConditions(
            query=request.query,
            budget_max=request.budget_max,
            occasion=request.occasion,
        ),
        recommendations=recommendations,
        data_notice="추천 결과는 흐름 검증용 합성 상품으로 생성되었습니다.",
    )
