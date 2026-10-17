from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_recommendations_respect_budget_and_include_evidence() -> None:
    response = client.post(
        "/v1/recommendations",
        json={"query": "회사 워크숍 검은 슬랙스 상의", "budget_max": 150000},
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["recommendations"]) == 3
    assert {item["strategy"] for item in body["recommendations"]} == {"safe", "balanced", "bold"}
    assert all(item["price"] <= 150000 for item in body["recommendations"])
    assert all(item["reasons"] and item["cautions"] for item in body["recommendations"])
    assert all(item["synthetic"] is True for item in body["recommendations"])


def test_recommendations_can_return_empty_without_relaxing_budget() -> None:
    response = client.post(
        "/v1/recommendations",
        json={"query": "회사 워크숍 검은 슬랙스 상의", "budget_max": 10000},
    )
    assert response.status_code == 200
    assert response.json()["recommendations"] == []


def test_invalid_request_returns_validation_error() -> None:
    response = client.post("/v1/recommendations", json={"query": "옷", "budget_max": 5000})
    assert response.status_code == 422


def test_openapi_exposes_recommendation_contract() -> None:
    schema = client.get("/openapi.json").json()
    assert "/v1/recommendations" in schema["paths"]
    post = schema["paths"]["/v1/recommendations"]["post"]
    assert post["requestBody"]["required"] is True
    assert "200" in post["responses"]
