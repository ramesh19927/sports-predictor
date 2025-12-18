import { useEffect, useState } from 'react'

const uniqueValues = (items, key) => Array.from(new Set(items.map((item) => item[key]).filter(Boolean)))

export default function Filters({ onChange }) {
  const [filters, setFilters] = useState({ sport: '', league: '', market_type: '', confidence: '' })

  useEffect(() => {
    onChange(filters)
  }, [filters, onChange])

  const update = (field, value) => {
    setFilters((prev) => ({ ...prev, [field]: value }))
  }

  return (
    <div className="filters">
      <label>
        Sport
        <input placeholder="e.g. soccer" value={filters.sport} onChange={(e) => update('sport', e.target.value)} />
      </label>
      <label>
        League
        <input placeholder="e.g. EPL" value={filters.league} onChange={(e) => update('league', e.target.value)} />
      </label>
      <label>
        Market type
        <input placeholder="moneyline, player prop" value={filters.market_type} onChange={(e) => update('market_type', e.target.value)} />
      </label>
      <label>
        Confidence
        <select value={filters.confidence} onChange={(e) => update('confidence', e.target.value)}>
          <option value="">Any</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
      </label>
    </div>
  )
}
