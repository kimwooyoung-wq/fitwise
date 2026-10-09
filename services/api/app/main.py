from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


@app.post(
    "/v1/recommendations",
    response_model=RecommendationResponse,
    tags=["recommendations"],
    summary="사용자 조건에 맞는 세 가지 추천 전략을 반환합니다.",
)
def create_recommendations(request: RecommendationRequest) -> RecommendationResponse:
    return recommend(request)
