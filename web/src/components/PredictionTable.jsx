import { useMemo, useState } from 'react'

const sortPredictions = (predictions, sortKey, direction) => {
  const sorted = [...predictions]
  sorted.sort((a, b) => {
    if (sortKey === 'probability') {
      return direction === 'asc' ? a.probability - b.probability : b.probability - a.probability
    }
    const aVal = (a[sortKey] || '').toString().toLowerCase()
    const bVal = (b[sortKey] || '').toString().toLowerCase()
    return direction === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal)
  })
  return sorted
}

export default function PredictionTable({ predictions, onSelect }) {
  const [sortKey, setSortKey] = useState('probability')
  const [direction, setDirection] = useState('desc')

  const sorted = useMemo(() => sortPredictions(predictions, sortKey, direction), [predictions, sortKey, direction])

  const toggleSort = (key) => {
    if (key === sortKey) {
      setDirection(direction === 'asc' ? 'desc' : 'asc')
    } else {
      setSortKey(key)
      setDirection('asc')
    }
  }

  const renderBadge = (tier) => <span className={`badge ${tier}`}>{tier}</span>

  return (
    <table className="prediction-table">
      <thead>
        <tr>
          <th>Event</th>
          <th onClick={() => toggleSort('sport')} style={{ cursor: 'pointer' }}>Sport</th>
          <th onClick={() => toggleSort('league')} style={{ cursor: 'pointer' }}>League</th>
          <th>Market</th>
          <th onClick={() => toggleSort('probability')} style={{ cursor: 'pointer' }}>Probability</th>
          <th>Confidence</th>
          <th>Source mix</th>
        </tr>
      </thead>
      <tbody>
        {sorted.map((p) => (
          <tr key={p.id} onClick={() => onSelect(p.event)} style={{ cursor: 'pointer' }}>
            <td>{p.event}</td>
            <td>{p.sport}</td>
            <td>{p.league}</td>
            <td>{p.market_type}</td>
            <td>{p.probability.toFixed ? p.probability.toFixed(1) : p.probability}%</td>
            <td>{renderBadge(p.confidence_tier)}</td>
            <td>
              <small>
                analyst {(p.source_mix?.analyst * 100).toFixed(0)}% · model {(p.source_mix?.model * 100).toFixed(0)}% · context {(p.source_mix?.context * 100).toFixed(0)}%
              </small>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
