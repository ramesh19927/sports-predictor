import { useEffect, useMemo, useState } from 'react';
import { FlatList, SafeAreaView, StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native';
import Constants from 'expo-constants';
import { StatusBar } from 'expo-status-bar';

const API_BASE = Constants.expoConfig?.extra?.apiBase || 'http://localhost:8000/api';

export default function App() {
  const [predictions, setPredictions] = useState([]);
  const [filters, setFilters] = useState({ sport: '', league: '', market_type: '' });
  const [error, setError] = useState('');

  useEffect(() => {
    const load = async () => {
      try {
        const params = new URLSearchParams();
        Object.entries(filters).forEach(([key, value]) => {
          if (value) params.append(key, value);
        });
        const res = await fetch(`${API_BASE}/predictions?${params.toString()}`);
        const data = await res.json();
        setPredictions(data);
        setError('');
      } catch (err) {
        setError('Unable to reach backend.');
      }
    };
    load();
  }, [filters]);

  const grouped = useMemo(() => {
    const map = new Map();
    predictions.forEach((p) => {
      if (!map.has(p.event)) map.set(p.event, []);
      map.get(p.event).push(p);
    });
    return Array.from(map.entries());
  }, [predictions]);

  const renderPrediction = ({ item }) => (
    <View style={styles.predictionCard}>
      <Text style={styles.predictionTitle}>{item.prediction}</Text>
      <Text style={styles.meta}>{item.market_type} · {item.probability}% · {item.confidence_tier}</Text>
      <Text style={styles.meta}>Source mix a{Math.round(item.source_mix?.analyst * 100)}% / m{Math.round(item.source_mix?.model * 100)}% / c{Math.round(item.source_mix?.context * 100)}%</Text>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="dark" />
      <Text style={styles.heading}>Sports Predictor</Text>
      <Text style={styles.meta}>Local-first predictions for this week and weekend</Text>

      <View style={styles.filterRow}>
        <TextInput style={styles.input} placeholder="Sport" value={filters.sport} onChangeText={(text) => setFilters({ ...filters, sport: text })} />
        <TextInput style={styles.input} placeholder="League" value={filters.league} onChangeText={(text) => setFilters({ ...filters, league: text })} />
        <TextInput style={styles.input} placeholder="Market" value={filters.market_type} onChangeText={(text) => setFilters({ ...filters, market_type: text })} />
      </View>

      {error ? <Text style={styles.error}>{error}</Text> : null}

      <FlatList
        data={grouped}
        keyExtractor={(item) => item[0]}
        renderItem={({ item }) => {
          const [event, preds] = item;
          return (
            <View style={styles.eventCard}>
              <View style={styles.eventHeader}>
                <View>
                  <Text style={styles.eventTitle}>{event}</Text>
                  <Text style={styles.meta}>{preds[0].sport} · {preds[0].league}</Text>
                </View>
                <TouchableOpacity>
                  <Text style={styles.link}>Details</Text>
                </TouchableOpacity>
              </View>
              <FlatList
                data={preds}
                keyExtractor={(p) => p.id}
                renderItem={renderPrediction}
                ItemSeparatorComponent={() => <View style={{ height: 8 }} />}
              />
            </View>
          );
        }}
        ItemSeparatorComponent={() => <View style={{ height: 12 }} />}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingTop: 32,
    paddingHorizontal: 16,
    backgroundColor: '#f8fafc',
  },
  heading: {
    fontSize: 24,
    fontWeight: '700',
    color: '#0f172a',
  },
  meta: {
    color: '#475569',
    marginTop: 4,
  },
  filterRow: {
    flexDirection: 'row',
    gap: 8,
    marginVertical: 12,
  },
  input: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 8,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  eventCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 12,
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 6,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  eventHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  eventTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#0f172a',
  },
  predictionCard: {
    backgroundColor: '#f8fafc',
    borderRadius: 10,
    padding: 10,
  },
  predictionTitle: {
    fontWeight: '600',
    color: '#0f172a',
  },
  link: {
    color: '#2563eb',
    fontWeight: '600',
  },
  error: {
    color: '#b91c1c',
    marginBottom: 8,
  },
});
