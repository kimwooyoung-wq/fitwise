import { useCallback, useEffect, useRef, useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  SafeAreaView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';

import { requestRecommendations } from '../api/client';
import { CatalogSearchPanel } from '../components/CatalogSearchPanel';
import { RecommendationCard } from '../components/RecommendationCard';
import { colors } from '../design/colors';
import { RecommendationResponse, validateSearchInput } from '../domain/recommendation';

type ScreenState =
  | { kind: 'idle' }
  | { kind: 'loading' }
  | { kind: 'success'; data: RecommendationResponse }
  | { kind: 'empty' }
  | { kind: 'error'; message: string };

const initialQuery = '15만 원 이하 회사 워크숍에 입을 상의. 검은 슬랙스와 어울리면 좋겠어.';

export default function SearchScreen() {
  const [query, setQuery] = useState(initialQuery);
  const [budget, setBudget] = useState('150000');
  const [validation, setValidation] = useState<string | null>(null);
  const [state, setState] = useState<ScreenState>({ kind: 'idle' });
  const abortRef = useRef<AbortController | null>(null);

  const search = useCallback(async () => {
    const validated = validateSearchInput(query, budget);
    if (!validated.ok) {
      setValidation(validated.message);
      return;
    }

    setValidation(null);
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    setState({ kind: 'loading' });

    try {
      const data = await requestRecommendations(validated.query, validated.budget, controller.signal);
      setState(data.recommendations.length ? { kind: 'success', data } : { kind: 'empty' });
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') return;
      setState({ kind: 'error', message: '추천 서버에 연결하지 못했습니다. API 실행 상태를 확인해 주세요.' });
    }
  }, [budget, query]);

  useEffect(() => () => abortRef.current?.abort(), []);

  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView style={styles.safeArea} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
        <FlatList
          data={state.kind === 'success' ? state.data.recommendations : []}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.content}
          keyboardShouldPersistTaps="handled"
          ListHeaderComponent={
            <View style={styles.headerBlock}>
              <Text style={styles.eyebrow}>FITWISE / DECISION PROTOTYPE</Text>
              <Text style={styles.heading}>상황을 말하면,{`\n`}살 옷을 좁혀드려요.</Text>
              <Text style={styles.description}>상품 수보다 추천 이유, 주의점, 데이터 신뢰도를 먼저 보여줍니다.</Text>
              <Text style={styles.label}>찾는 상황과 옷</Text>
              <TextInput
                accessibilityLabel="찾는 상황과 옷"
                multiline
                value={query}
                onChangeText={setQuery}
                placeholder="예: 첫 출근에 입을 15만 원 이하 재킷"
                placeholderTextColor={colors.placeholder}
                style={[styles.input, styles.queryInput]}
              />
              <Text style={styles.label}>최대 예산</Text>
              <TextInput
                accessibilityLabel="최대 예산"
                value={budget}
                onChangeText={setBudget}
                keyboardType="number-pad"
                placeholder="150000"
                placeholderTextColor={colors.placeholder}
                style={styles.input}
              />
              {validation && <Text style={styles.validation} accessibilityRole="alert">{validation}</Text>}
              <Pressable
                accessibilityRole="button"
                accessibilityLabel="추천 결과 보기"
                disabled={state.kind === 'loading'}
                onPress={search}
                style={({ pressed }) => [styles.cta, pressed && styles.ctaPressed]}
              >
                <Text style={styles.ctaText}>{state.kind === 'loading' ? '조건을 분석하는 중' : '추천 결과 보기'}</Text>
              </Pressable>
              {state.kind === 'loading' && <ActivityIndicator color={colors.amber} size="large" accessibilityLabel="추천 결과 로딩 중" />}
              {state.kind === 'empty' && (
                <View style={styles.stateBox}>
                  <Text style={styles.stateTitle}>조건에 맞는 후보가 없습니다.</Text>
                  <Text style={styles.stateBody}>예산을 높이거나 상황을 조금 넓혀 다시 검색해 주세요.</Text>
                </View>
              )}
              {state.kind === 'error' && (
                <View style={styles.stateBox}>
                  <Text style={styles.stateTitle}>결과를 불러오지 못했습니다.</Text>
                  <Text style={styles.stateBody}>{state.message}</Text>
                  <Pressable accessibilityRole="button" onPress={search} style={styles.retry}>
                    <Text style={styles.retryText}>다시 시도</Text>
                  </Pressable>
                </View>
              )}
              {state.kind === 'success' && (
                <View style={styles.resultHeader}>
                  <Text style={styles.eyebrow}>3 STRATEGIES</Text>
                  <Text style={styles.resultTitle}>추천 결과</Text>
                  <Text style={styles.stateBody}>{state.data.data_notice}</Text>
                </View>
              )}
            </View>
          }
          renderItem={({ item }) => <RecommendationCard item={item} />}
          ItemSeparatorComponent={() => <View style={styles.separator} />}
          ListFooterComponent={(
            <View>
              <CatalogSearchPanel budgetText={budget} />
              <Text style={styles.footer}>FITWISE는 현재 구매 결정을 검증하는 프로토타입입니다.</Text>
            </View>
          )}
        />
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: colors.canvas },
  content: { paddingHorizontal: 20, paddingTop: 32, paddingBottom: 56 },
  headerBlock: { gap: 12, marginBottom: 24 },
  eyebrow: { color: colors.walnut, fontSize: 11, fontWeight: '800', letterSpacing: 1.7 },
  heading: { color: colors.ink, fontSize: 38, fontWeight: '800', lineHeight: 44, letterSpacing: -1.2 },
  description: { color: colors.muted, fontSize: 15, lineHeight: 23, marginBottom: 12 },
  label: { color: colors.inkSoft, fontSize: 13, fontWeight: '700', marginTop: 6 },
  input: { backgroundColor: colors.surface, borderColor: colors.line, borderWidth: 1, borderRadius: 16, color: colors.ink, fontSize: 16, padding: 16 },
  queryInput: { minHeight: 116, textAlignVertical: 'top' },
  validation: { color: colors.danger, fontSize: 13 },
  cta: { alignItems: 'center', backgroundColor: colors.walnut, borderRadius: 16, padding: 17, marginTop: 6 },
  ctaPressed: { opacity: 0.82 },
  ctaText: { color: colors.surface, fontSize: 16, fontWeight: '800' },
  stateBox: { backgroundColor: colors.surfaceRaised, borderRadius: 20, padding: 20, gap: 8, marginTop: 8 },
  stateTitle: { color: colors.ink, fontSize: 18, fontWeight: '700' },
  stateBody: { color: colors.muted, fontSize: 14, lineHeight: 21 },
  retry: { alignSelf: 'flex-start', borderColor: colors.amber, borderWidth: 1, borderRadius: 12, paddingHorizontal: 14, paddingVertical: 9, marginTop: 8 },
  retryText: { color: colors.walnut, fontWeight: '700' },
  resultHeader: { gap: 8, marginTop: 20 },
  resultTitle: { color: colors.ink, fontSize: 28, fontWeight: '800' },
  separator: { height: 14 },
  footer: { color: colors.muted, textAlign: 'center', fontSize: 11, marginTop: 30 },
});
