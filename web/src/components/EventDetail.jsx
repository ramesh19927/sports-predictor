export default function EventDetail({ eventName, events, onClose }) {
  const event = events.find((e) => e.meta.event === eventName)
  if (!event) return null
  const { meta, predictions } = event

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <p className="meta">{meta.sport} · {meta.league}</p>
          <h3>{eventName}</h3>
          <p className="meta">{new Date(meta.event_date).toLocaleString()}</p>
        </div>
        <button onClick={onClose} style={{ border: 'none', background: '#e2e8f0', borderRadius: 8, padding: '0.45rem 0.75rem', cursor: 'pointer' }}>Close</button>
      </div>
      <div style={{ marginTop: '1rem' }}>
        {predictions.map((p) => (
          <div key={p.id} className="card" style={{ marginBottom: '0.75rem' }}>
            <strong>{p.prediction}</strong>
            <p className="meta">{p.market_type} · {p.probability}% · confidence {p.confidence_tier}</p>
            <p className="meta">Source mix: analyst {(p.source_mix?.analyst * 100).toFixed(0)}% · model {(p.source_mix?.model * 100).toFixed(0)}% · context {(p.source_mix?.context * 100).toFixed(0)}%</p>
            <ul>
              {p.factors?.map((f, idx) => <li key={idx}>{f}</li>)}
            </ul>
          </div>
        ))}
      </div>
    </div>
  )
}
