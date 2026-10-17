# FITWISE Mobile Prototype

## 실행

```powershell
npm install
Copy-Item .env.example .env.local
npm start
```

API를 먼저 `services/api`에서 실행한다. 실제 휴대폰의 Expo Go로 확인할 때는 `.env.local`의 `EXPO_PUBLIC_API_BASE_URL`을 개발 PC의 같은 네트워크 IP로 변경한다.

```text
# Android Emulator
EXPO_PUBLIC_API_BASE_URL=http://10.0.2.2:8000

# 실제 휴대폰 예시
EXPO_PUBLIC_API_BASE_URL=http://192.168.0.10:8000
```

## 검증

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

상품은 모두 합성 데이터이며 실제 구매 판단에 사용할 수 없다.
