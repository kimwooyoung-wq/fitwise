import { useCallback, useEffect, useRef, useState } from 'react';
import { ActivityIndicator, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';

import { requestCatalogSearch } from '../api/client';
import type { CatalogItem, CatalogSearchResponse } from '../domain/catalog';

type SearchState =
  | { kind: 'idle' }
  | { kind: 'loading' }
  | { kind: 'success'; data: CatalogSearchResponse }
  | { kind: 'empty' }
  | { kind: 'error'; message: string };

function formatWon(amount: number): string {
  return new Intl.NumberFormat('ko-KR').format(amount);
}

function CatalogItemCard({ item }: { item: CatalogItem }) {
  return (
    <View style={styles.itemCard} accessibilityLabel={`합성 카탈로그 상품 ${item.product_name}`}>
      <Text style={styles.brand}>{item.brand_name}</Text>
      <Text style={styles.itemName}>{item.product_name}</Text>
      <Text style={styles.meta}>{item.category_code} · {item.seller_name}</Text>
      <Text style={styles.price}>{formatWon(item.price_minor)}원</Text>
      <Text style={styles.stock}>재고 상태: {item.stock_status === 'in_stock' ? '재고 있음' : '재고 적음'}</Text>
    </View>
  );
}

export function CatalogSearchPanel({ budgetText }: { budgetText: string }) {
  const [keyword, setKeyword] = useState('네이비');
  const [state, setState] = useState<SearchState>({ kind: 'idle' });
  const abortRef = useRef<AbortController | null>(null);

  const search = useCallback(async () => {
    const budgetMax = Number(budgetText.replace(/[^0-9]/g, ''));
    if (!Number.isFinite(budgetMax) || budgetMax < 10_000 || budgetMax > 10_000_000) {
      setState({ kind: 'error', message: '위쪽 예산을 1만 원에서 1천만 원 사이로 입력해 주세요.' });
      return;
    }
    if (keyword.trim().length < 1 || keyword.trim().length > 100) {
      setState({ kind: 'error', message: '상품명 또는 색상 키워드를 1~100자로 입력해 주세요.' });
      return;
    }

    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    setState({ kind: 'loading' });

    try {
      const data = await requestCatalogSearch(keyword.trim(), budgetMax, controller.signal);
      setState(data.items.length ? { kind: 'success', data } : { kind: 'empty' });
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') return;
      setState({ kind: 'error', message: 'DB 검색을 완료하지 못했습니다. API와 disposable PostgreSQL 설정을 확인해 주세요.' });
    }
  }, [budgetText, keyword]);

  useEffect(() => () => abortRef.current?.abort(), []);

  return (
    <View style={styles.panel}>
      <Text style={styles.eyebrow}>ENGINEERING CHECK / POSTGRES</Text>
      <Text style={styles.heading}>DB 카탈로그 검색</Text>
      <Text style={styles.description}>
        개발 검증용 합성 상품만 조회합니다. 실제 브랜드 상품이나 재고가 아닙니다.
      </Text>
      <TextInput
        accessibilityLabel="DB 카탈로그 검색 키워드"
        value={keyword}
        onChangeText={setKeyword}
        onSubmitEditing={search}
        returnKeyType="search"
        placeholder="예: 네이비"
        placeholderTextColor="#777777"
        style={styles.input}
      />
      <Pressable
        accessibilityRole="button"
        accessibilityLabel="DB 카탈로그 조회"
        disabled={state.kind === 'loading'}
        onPress={search}
        style={({ pressed }) => [styles.button, pressed && styles.buttonPressed, state.kind === 'loading' && styles.buttonDisabled]}
      >
        <Text style={styles.buttonText}>{state.kind === 'loading' ? 'DB 조회 중' : '합성 카탈로그 조회'}</Text>
      </Pressable>
      {state.kind === 'loading' && <ActivityIndicator color="#D8FF3E" accessibilityLabel="DB 카탈로그 조회 중" />}
      {state.kind === 'empty' && (
        <View style={styles.stateBox}>
          <Text style={styles.stateTitle}>조건에 맞는 합성 상품이 없습니다.</Text>
          <Text style={styles.stateBody}>키워드나 예산을 바꿔 다시 조회해 주세요.</Text>
        </View>
      )}
      {state.kind === 'error' && (
        <View style={styles.stateBox} accessibilityRole="alert">
          <Text style={styles.stateTitle}>DB 검색을 사용할 수 없습니다.</Text>
          <Text style={styles.stateBody}>{state.message}</Text>
          <Pressable accessibilityRole="button" onPress={search} style={styles.retry}>
            <Text style={styles.retryText}>다시 시도</Text>
          </Pressable>
        </View>
      )}
      {state.kind === 'success' && (
        <View style={styles.results}>
          <Text style={styles.stateBody}>{state.data.data_notice}</Text>
          {state.data.items.map((item) => <CatalogItemCard item={item} key={item.product_id} />)}
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  panel: { backgroundColor: '#111111', borderColor: '#343434', borderWidth: 1, borderRadius: 20, padding: 18, gap: 12, marginTop: 24 },
  eyebrow: { color: '#8E8E8E', fontSize: 10, fontWeight: '800', letterSpacing: 1.4 },
  heading: { color: '#FFFFFF', fontSize: 21, fontWeight: '800' },
  description: { color: '#A5A5A5', fontSize: 13, lineHeight: 20 },
  input: { backgroundColor: '#1A1A1A', borderColor: '#3B3B3B', borderWidth: 1, borderRadius: 12, color: '#FFFFFF', fontSize: 15, padding: 13 },
  button: { alignItems: 'center', backgroundColor: '#D8FF3E', borderRadius: 12, padding: 14 },
  buttonPressed: { opacity: 0.82 },
  buttonDisabled: { opacity: 0.6 },
  buttonText: { color: '#0A0A0A', fontSize: 14, fontWeight: '800' },
  stateBox: { backgroundColor: '#191919', borderRadius: 14, padding: 14, gap: 7 },
  stateTitle: { color: '#FFFFFF', fontSize: 14, fontWeight: '700' },
  stateBody: { color: '#A5A5A5', fontSize: 12, lineHeight: 18 },
  retry: { alignSelf: 'flex-start', borderColor: '#D8FF3E', borderWidth: 1, borderRadius: 10, paddingHorizontal: 12, paddingVertical: 8, marginTop: 4 },
  retryText: { color: '#D8FF3E', fontWeight: '700', fontSize: 12 },
  results: { gap: 10 },
  itemCard: { backgroundColor: '#191919', borderRadius: 14, borderColor: '#2B2B2B', borderWidth: 1, padding: 14, gap: 5 },
  brand: { color: '#999999', fontSize: 11, fontWeight: '700' },
  itemName: { color: '#FFFFFF', fontSize: 16, fontWeight: '700' },
  meta: { color: '#AAAAAA', fontSize: 12 },
  price: { color: '#D8FF3E', fontSize: 16, fontWeight: '800', marginTop: 4 },
  stock: { color: '#939393', fontSize: 11 },
});
