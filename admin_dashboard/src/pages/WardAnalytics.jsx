// src/pages/WardAnalytics.jsx
import { useEffect, useState } from 'react'
import { analyticsApi } from '../api/api'
import { Bar } from 'react-chartjs-2'

export default function WardAnalytics() {
  const [stats, setStats]     = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    analyticsApi.getWardStats()
      .then(r => {
        const list = r.data?.data?.ward_stats || []
        setStats(list)
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="spinner-wrap"><div className="spinner" /></div>

  const displayStats = stats.length > 0 ? stats : [
    { ward_id: 1, ward_name: 'Ward 1', total_complaints: 0, resolved: 0, pending: 0, avg_resolution_time: 0, avg_satisfaction: 0 },
    { ward_id: 2, ward_name: 'Ward 2', total_complaints: 0, resolved: 0, pending: 0, avg_resolution_time: 0, avg_satisfaction: 0 },
    { ward_id: 3, ward_name: 'Ward 3', total_complaints: 0, resolved: 0, pending: 0, avg_resolution_time: 0, avg_satisfaction: 0 },
    { ward_id: 4, ward_name: 'Ward 4', total_complaints: 0, resolved: 0, pending: 0, avg_resolution_time: 0, avg_satisfaction: 0 },
    { ward_id: 5, ward_name: 'Ward 5', total_complaints: 0, resolved: 0, pending: 0, avg_resolution_time: 0, avg_satisfaction: 0 },
  ]

  const chartData = {
    labels: displayStats.map(s => s.ward_name || `Ward ${s.ward_id}`),
    datasets: [
      {
        label: 'Resolved',
        data: displayStats.map(s => Number(s.resolved) || 0),
        backgroundColor: '#10b981',
        borderRadius: 6,
      },
      {
        label: 'Pending',
        data: displayStats.map(s => Number(s.pending) || 0),
        backgroundColor: '#f59e0b',
        borderRadius: 6,
      }
    ]
  }

  return (
    <div>
      <div className="page-header">
        <div className="page-title">
          <h2>Ward-wise Analytics — Vemavaram Village</h2>
          <p>Real-time civic resolution metrics across Village Wards 1 to 5</p>
        </div>
      </div>

      <div className="stats-grid">
        {displayStats.map(s => (
          <div key={s.ward_id || s.ward_name} className="stat-card">
            <div className="stat-info">
              <div className="stat-value">{s.total_complaints || 0}</div>
              <div className="stat-label">{s.ward_name || `Ward ${s.ward_id}`} Complaints</div>
              <div className="stat-sub">{s.resolved || 0} Resolved | {s.pending || 0} Pending</div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--primary)' }}>
                {parseFloat(s.avg_resolution_time || 0).toFixed(1)}d
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Avg. Resolution</div>
            </div>
          </div>
        ))}
      </div>

      <div className="card mt-24">
        <div className="card-header">
          <h3>Ward Resolution Status</h3>
          <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>Comparison of Resolved vs Pending complaints per ward</p>
        </div>
        <div className="card-body" style={{ height: 320 }}>
          <Bar data={chartData} options={{
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: { beginAtZero: true, ticks: { stepSize: 1 } }
            }
          }} />
        </div>
      </div>
    </div>
  )
}
