from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .catalog_search import CatalogSearchResponse, search_synthetic_catalog
from .models import RecommendationRequest, RecommendationResponse
from .recommender import recommend

app = FastAPI(
    title="FITWISE Prototype API",
    version="0.1.0",
    description="검색 → 추천 결과 프로토타입을 검증하는 합성 데이터 API",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8081", "http://127.0.0.1:8081"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get(
    "/v1/catalog/search",
    response_model=CatalogSearchResponse,
    tags=["catalog"],
    summary="예산·카테고리·검색어에 맞는 현재 유효한 합성 카탈로그를 조회합니다.",
)
def search_catalog(
    q: str | None = Query(default=None, min_length=1, max_length=100),
    category: str | None = Query(default=None, pattern=r"^[a-z][a-z0-9_-]{0,63}$"),
    budget_max: int = Query(default=150_000, ge=10_000, le=10_000_000),
    limit: int = Query(default=20, ge=1, le=50),
) -> CatalogSearchResponse:
    try:
        return search_synthetic_catalog(
            query=q,
            category=category,
            budget_max=budget_max,
            limit=limit,
        )
    except HTTPException:
        raise


@app.post(
    "/v1/recommendations",
    response_model=RecommendationResponse,
    tags=["recommendations"],
    summary="사용자 조건에 맞는 세 가지 추천 전략을 반환합니다.",
)
def create_recommendations(request: RecommendationRequest) -> RecommendationResponse:
    return recommend(request)
