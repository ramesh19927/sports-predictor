import { useEffect, useMemo, useState } from 'react'
import axios from 'axios'
import PredictionTable from './components/PredictionTable'
import Filters from './components/Filters'
import EventDetail from './components/EventDetail'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api'

export default function App() {
  const [predictions, setPredictions] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [selectedEvent, setSelectedEvent] = useState(null)
  const [filters, setFilters] = useState({ sport: '', league: '', market_type: '', confidence: '' })

  useEffect(() => {
    const fetchPredictions = async () => {
      setLoading(true)
      setError('')
      try {
        const params = {
          sport: filters.sport || undefined,
          league: filters.league || undefined,
          market_type: filters.market_type || undefined,
          confidence: filters.confidence || undefined,
        }
        const { data } = await axios.get(`${API_BASE}/predictions`, { params })
        setPredictions(data)
      } catch (err) {
        setError('Unable to load predictions. Check that the API is running.')
      } finally {
        setLoading(false)
      }
    }
    fetchPredictions()
  }, [filters])

  const events = useMemo(() => {
    const grouped = {}
    predictions.forEach((p) => {
      grouped[p.event] = grouped[p.event] || { meta: p, predictions: [] }
      grouped[p.event].predictions.push(p)
    })
    return Object.values(grouped)
  }, [predictions])

  return (
    <div className="app-shell">
      <header>
        <div>
          <p className="meta">Local-first sports intelligence</p>
          <h1>Sports Predictor</h1>
        </div>
      </header>

      <div className="card">
        <h2 className="section-title">Filters</h2>
        <Filters onChange={setFilters} />
      </div>

      <div className="card">
        <h2 className="section-title">Predictions</h2>
        {loading && <div className="loading">Loading predictions…</div>}
        {error && <div className="error">{error}</div>}
        {!loading && !error && (
          <PredictionTable
            predictions={predictions}
            onSelect={(eventName) => setSelectedEvent(eventName)}
          />
        )}
      </div>

      {selectedEvent && (
        <div className="event-detail">
          <EventDetail eventName={selectedEvent} events={events} onClose={() => setSelectedEvent(null)} />
        </div>
      )}
    </div>
  )
}
