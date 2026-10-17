import type { RecommendationResponse } from '../domain/recommendation';

const API_BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL ?? 'http://127.0.0.1:8000';

export async function requestRecommendations(
  query: string,
  budgetMax: number,
  signal?: AbortSignal,
): Promise<RecommendationResponse> {
  const response = await fetch(`${API_BASE_URL}/v1/recommendations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, budget_max: budgetMax }),
    signal,
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `추천 요청에 실패했습니다. (${response.status})`);
  }

  return response.json() as Promise<RecommendationResponse>;
}
