# FITWISE Prototype API

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements-dev.txt
.\.venv\Scripts\python -m uvicorn app.main:app --reload
```

- Swagger UI: <http://127.0.0.1:8000/docs>
- OpenAPI JSON: <http://127.0.0.1:8000/openapi.json>
- Health: <http://127.0.0.1:8000/health>

현재 응답은 합성 상품만 사용한다. 브랜드·상품 피드 계약이 확정되기 전에는 실제 상품이나 이미지를 추가하지 않는다.
