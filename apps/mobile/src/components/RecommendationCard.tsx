import { StyleSheet, Text, View } from 'react-native';

import type { Recommendation } from '../domain/recommendation';

const strategyColor = {
  safe: '#D8FF3E',
  balanced: '#72D4FF',
  bold: '#C9A7FF',
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
  card: { backgroundColor: '#181818', borderColor: '#303030', borderWidth: 1, borderRadius: 24, padding: 20, gap: 7 },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  strategy: { fontSize: 12, fontWeight: '800', letterSpacing: 1.4 },
  confidence: { color: '#A6A6A6', fontSize: 12 },
  swatch: { height: 5, borderRadius: 99, marginVertical: 8 },
  brand: { color: '#8F8F8F', fontSize: 12 },
  title: { color: '#FFFFFF', fontSize: 22, fontWeight: '700' },
  price: { color: '#FFFFFF', fontSize: 16, fontWeight: '600', marginBottom: 10 },
  label: { color: '#BDBDBD', fontSize: 12, fontWeight: '700', marginTop: 6 },
  reason: { color: '#F2F2F2', fontSize: 14, lineHeight: 21 },
  caution: { color: '#C8C8C8', fontSize: 14, lineHeight: 21 },
  synthetic: { color: '#707070', fontSize: 10, letterSpacing: 1, marginTop: 10 },
});
