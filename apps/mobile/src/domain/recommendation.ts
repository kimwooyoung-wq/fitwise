export type RecommendationStrategy = 'safe' | 'balanced' | 'bold';

export type Recommendation = {
  id: string;
  strategy: RecommendationStrategy;
  strategy_label: string;
  title: string;
  brand: string;
  category: string;
  price: number;
  currency: 'KRW';
  confidence: number;
  reasons: string[];
  cautions: string[];
  synthetic: boolean;
};

export type RecommendationResponse = {
  request_id: string;
  interpreted_conditions: {
    query: string;
    budget_max: number | null;
    occasion: string | null;
  };
  recommendations: Recommendation[];
  data_notice: string;
};

export function validateSearchInput(query: string, budgetText: string) {
  const normalizedQuery = query.trim();
  const budget = Number(budgetText.replace(/[^0-9]/g, ''));

  if (normalizedQuery.length < 5) {
    return { ok: false as const, message: '상황과 원하는 옷을 5자 이상 입력해 주세요.' };
  }
  if (!Number.isFinite(budget) || budget < 10_000 || budget > 10_000_000) {
    return { ok: false as const, message: '예산은 1만 원에서 1천만 원 사이로 입력해 주세요.' };
  }

  return { ok: true as const, query: normalizedQuery, budget };
}
