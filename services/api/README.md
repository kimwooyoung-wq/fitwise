# FITWISE Prototype API

## 개발 PC에서 실행

저장소 루트에서 PowerShell을 엽니다.

```powershell
cd services/api
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements-dev.txt
.\.venv\Scripts\python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

`--host 0.0.0.0`은 개발 PC의 네트워크 인터페이스에서 휴대폰 연결을 받기 위한 바인딩입니다. 휴대폰에서 접속할 때는 PC의 Wi‑Fi IPv4 주소를 사용합니다. 예를 들어 PC 주소가 `192.168.0.10`이면 휴대폰 브라우저에서 다음 주소를 확인합니다.

- Health: `http://192.168.0.10:8000/health`
- Swagger UI: `http://192.168.0.10:8000/docs`

API 포트는 신뢰하는 로컬 개발 네트워크에서만 사용하고 인터넷에 공개하지 마세요. 방화벽 허용이 필요하면 개인 네트워크에서만 Python 통신을 허용합니다.

## PC에서만 확인할 때

기존과 같이 로컬 주소를 사용할 수 있습니다.

- Swagger UI: <http://127.0.0.1:8000/docs>
- OpenAPI JSON: <http://127.0.0.1:8000/openapi.json>
- Health: <http://127.0.0.1:8000/health>

현재 응답은 합성 상품만 사용합니다. 브랜드·상품 피드 계약이 확정되기 전에는 실제 상품이나 이미지를 추가하지 않습니다.
