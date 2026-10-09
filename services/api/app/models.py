from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class Strategy(StrEnum):
    SAFE = "safe"
    BALANCED = "balanced"
    BOLD = "bold"


class RecommendationRequest(BaseModel):
    query: str = Field(min_length=5, max_length=500, examples=["15만 원 이하 회사 워크숍에 입을 상의"])
    budget_max: int = Field(ge=10_000, le=10_000_000, examples=[150_000])
    occasion: str | None = Field(default=None, max_length=80)

    @field_validator("query")
    @classmethod
    def query_must_not_be_blank(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if len(normalized) < 5:
            raise ValueError("query must contain at least five non-whitespace characters")
        return normalized


class InterpretedConditions(BaseModel):
    query: str
    budget_max: int | None
    occasion: str | None


class Recommendation(BaseModel):
    id: str
    strategy: Strategy
    strategy_label: str
    title: str
    brand: str
    category: str
    price: int
    currency: Literal["KRW"] = "KRW"
    confidence: float = Field(ge=0, le=1)
    reasons: list[str]
    cautions: list[str]
    synthetic: bool = True


class RecommendationResponse(BaseModel):
    request_id: str
    interpreted_conditions: InterpretedConditions
    recommendations: list[Recommendation]
    data_notice: str
