import { StyleSheet, Text, View } from 'react-native';

import type { Recommendation } from '../domain/recommendation';
import { colors } from '../design/colors';

const strategyColor = {
  safe: colors.strategySafe,
  balanced: colors.strategyBalanced,
  bold: colors.strategyBold,
} as const;

export function RecommendationCard({ item }: { item: Recommendation }) {
  const color = strategyColor[item.strategy];
  return (
    <View style={styles.card} accessibilityLabel={`${item.strategy_label} 추천 ${item.title}`}>
      <View style={styles.header}>
        <Text style={[styles.strategy, { color }]}>{item.strategy_label.toUpperCase()}</Text>
        <Text style={styles.confidence}>근거 충족 {Math.round(item.confidence * 100)}%</Text>
      </View>
      <View style={[styles.swatch, { backgroundColor: color }]} />
      <Text style={styles.brand}>{item.brand}</Text>
      <Text style={styles.title}>{item.title}</Text>
      <Text style={styles.price}>{item.price.toLocaleString('ko-KR')}원</Text>
      <Text style={styles.label}>추천 이유</Text>
      {item.reasons.map((reason) => <Text key={reason} style={styles.reason}>• {reason}</Text>)}
      <Text style={styles.label}>확인할 점</Text>
      {item.cautions.map((caution) => <Text key={caution} style={styles.caution}>• {caution}</Text>)}
      {item.synthetic && <Text style={styles.synthetic}>PROTOTYPE · 합성 상품 데이터</Text>}
    </View>
  );
}

const styles = StyleSheet.create({
  card: { backgroundColor: colors.surface, borderColor: colors.line, borderWidth: 1, borderRadius: 24, padding: 20, gap: 7 },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  strategy: { fontSize: 12, fontWeight: '800', letterSpacing: 1.4 },
  confidence: { color: colors.muted, fontSize: 12 },
  swatch: { height: 5, borderRadius: 99, marginVertical: 8 },
  brand: { color: colors.mutedStrong, fontSize: 12 },
  title: { color: colors.ink, fontSize: 22, fontWeight: '700' },
  price: { color: colors.walnut, fontSize: 16, fontWeight: '600', marginBottom: 10 },
  label: { color: colors.inkSoft, fontSize: 12, fontWeight: '700', marginTop: 6 },
  reason: { color: colors.ink, fontSize: 14, lineHeight: 21 },
  caution: { color: colors.inkSoft, fontSize: 14, lineHeight: 21 },
  synthetic: { color: colors.muted, fontSize: 10, letterSpacing: 1, marginTop: 10 },
});
