# FITWISE Mobile Prototype

## 실제 Android/iOS 휴대폰에서 실행

이 프로토타입은 공개 웹사이트가 아닙니다. 앱과 API를 개발 PC에서 실행한 뒤 Expo Go로 같은 Wi‑Fi에 연결된 휴대폰에서 확인합니다. API는 합성 상품만 반환합니다.

### 1. API 서버 실행

저장소 루트에서 PowerShell을 열고 다음을 실행합니다.

```powershell
cd services/api
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements-dev.txt
.\.venv\Scripts\python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

서버를 실행한 채로 둡니다. 휴대폰 브라우저에서 `http://<PC의-Wi-Fi-IPv4>:8000/health`를 열었을 때 `{"status":"ok"}`가 보여야 합니다.

### 2. PC의 Wi‑Fi IPv4 주소 확인

PowerShell에서 `ipconfig`를 실행합니다. 현재 연결된 Wi‑Fi 어댑터의 **IPv4 주소**를 사용하세요. VPN, 가상 어댑터, 이더넷이 아닌 휴대폰과 같은 Wi‑Fi에 연결된 어댑터의 주소여야 합니다.

### 3. 모바일 앱 환경 변수 설정

새 PowerShell 창에서 앱 폴더로 이동합니다.

```powershell
cd apps/mobile
npm install
Copy-Item .env.example .env.local
notepad .env.local
```

`.env.local`의 값을 PC에서 확인한 주소로 바꿉니다.

```text
EXPO_PUBLIC_API_BASE_URL=http://192.168.0.10:8000
```

위 IP는 예시입니다. 실제 PC의 Wi‑Fi IPv4 주소로 바꾸세요. `.env.local`은 저장소의 `.gitignore`에서 제외되어 있으므로 커밋하지 않습니다.

### 4. Expo Go에서 앱 열기

```powershell
npm start -- --lan --clear
```

PC와 휴대폰을 같은 Wi‑Fi에 연결하고, 휴대폰에서 Expo Go를 연 다음 터미널에 표시되는 QR 코드를 스캔합니다. 환경 변수를 바꾼 뒤에는 Expo를 완전히 종료하고 이 명령으로 다시 시작하세요.

### 주소 구분

| 실행 대상 | `EXPO_PUBLIC_API_BASE_URL` |
|---|---|
| PC에서 실행하는 앱 | `http://127.0.0.1:8000` |
| Android Emulator | `http://10.0.2.2:8000` |
| 실제 Android/iOS 휴대폰 | `http://<PC의 Wi‑Fi IPv4>:8000` |

`10.0.2.2`는 Android Emulator 전용 주소라서 실제 휴대폰에서는 사용할 수 없습니다. 휴대폰에 전달해 클릭하는 URL이 아니라 앱이 API를 호출할 때 사용하는 설정값입니다.

### 연결이 안 될 때

1. PC와 휴대폰이 같은 Wi‑Fi에 있는지 확인합니다. 게스트 Wi‑Fi나 기기 간 통신 차단 설정은 피하세요.
2. API 서버가 `--host 0.0.0.0 --port 8000`으로 실행 중인지 확인합니다.
3. 휴대폰 브라우저에서 `http://<PC의-Wi-Fi-IPv4>:8000/health`가 열리는지 확인합니다.
4. Windows 방화벽 알림이 나오면 신뢰하는 **개인 네트워크**에서만 Python 통신을 허용합니다. 공용 네트워크에 API를 노출하지 마세요.
5. `.env.local`의 IP와 포트가 맞는지 확인하고 Expo를 재시작합니다.

## 검증 명령

```powershell
npm run lint
npm run typecheck
npm test
npx expo-doctor
npx expo export --platform android --output-dir dist-android
```

## 현재 범위

- 상황과 예산 입력
- FastAPI 추천 요청
- Safe·Balanced·Bold 결과
- 추천 근거·주의점·데이터 신뢰도
- 입력 오류·로딩·빈 결과·API 오류·재시도

상품은 모두 합성 데이터이며 실제 구매 판단에 사용할 수 없습니다.
