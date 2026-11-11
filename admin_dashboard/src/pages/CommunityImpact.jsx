// src/pages/CommunityImpact.jsx
import { useEffect, useState } from 'react'
import { analyticsApi } from '../api/api'
import { MdPublic, MdCheckCircleOutline, MdWaterDrop, MdLightbulbOutline, MdSanitizer } from 'react-icons/md'

export default function CommunityImpact() {
  const [data, setData]       = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    analyticsApi.getDashboard()
      .then(r => setData(r.data?.data))
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="spinner-wrap"><div className="spinner" /></div>

  const summary = data?.summary || {}
  const total = Number(summary.total) || 0
  const resolved = Number(summary.resolved) || 0
  const resolutionRate = total > 0 ? Math.round((resolved / total) * 100) : 100
  const avgRating = parseFloat(summary.avg_rating || 5)

  // Verified Civic Health Index calculated from database resolution & citizen ratings
  const devScore = total > 0
    ? Math.min(100, Math.round(resolutionRate * 0.7 + (avgRating / 5) * 30))
    : 100

  // Category health calculation based on active vs resolved complaints
  const categories = data?.category_breakdown || []
  const getCategoryHealth = (keyword) => {
    const match = categories.find(c => c.category.toLowerCase().includes(keyword.toLowerCase()))
    if (!match || match.count === 0) return 100 // No reported failures = healthy
    // Ratio of resolved complaints overall
    return Math.max(30, Math.round(resolutionRate))
  }

  return (
    <div>
      <div className="page-header" style={{ textAlign: 'center', marginBottom: 40 }}>
        <div className="village-badge" style={{ display: 'inline-flex', marginBottom: 16, transform: 'scale(1.2)' }}>
          <div className="icon"><MdPublic /></div>
        </div>
        <h2>Vemavaram Smart Village Dashboard</h2>
        <p>Verified Community Impact & Transparency Metrics</p>
      </div>

      <div className="impact-hero-grid">
        <div className="card hero-score">
          <div className="card-body" style={{ textAlign: 'center', padding: '40px 20px' }}>
            <h3 style={{ color: 'var(--text-muted)' }}>Civic Performance Index</h3>
            <div className="massive-score" style={{ fontSize: 72, fontWeight: 800, color: 'var(--primary)', margin: '16px 0' }}>
              {devScore}/100
            </div>
            <p style={{ color: 'var(--text-secondary)' }}>
              Calculated from {total} live citizen complaints & {resolved} completed field resolutions
            </p>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <h3>Infrastructure Health Index</h3>
            <p style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 16 }}>
              Dynamic stability score based on active infrastructure incidents
            </p>
            <div className="health-bars" style={{ marginTop: 16 }}>
              <HealthBar
                icon={<MdWaterDrop color="#3b82f6" />}
                label="Water Supply & Distribution"
                score={getCategoryHealth('water')}
              />
              <HealthBar
                icon={<MdSanitizer color="#22c55e" />}
                label="Sanitation & Drainage"
                score={getCategoryHealth('drainage')}
              />
              <HealthBar
                icon={<MdLightbulbOutline color="#eab308" />}
                label="Electrical, Lighting & Roads"
                score={getCategoryHealth('streetlight')}
              />
            </div>
          </div>
        </div>
      </div>

      <div className="stats-grid" style={{ marginTop: 32 }}>
        <StatCard title="Total Issues Registered" value={total} sub="Citizen reported problems" />
        <StatCard title="Issues Resolved" value={resolved} sub="Verified field completions" />
        <StatCard title="Resolution Efficiency" value={`${resolutionRate}%`} sub="Overall closure rate" />
        <StatCard
          title="Avg Resolution Days"
          value={`${summary.avg_resolution_days || 0}d`}
          sub="Turnaround time"
        />
      </div>
    </div>
  )
}

function HealthBar({ icon, label, score }) {
  const color = score >= 75 ? 'var(--success)' : score >= 50 ? 'var(--warning)' : 'var(--danger)'
  return (
    <div style={{ marginBottom: 20 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8, fontWeight: 600 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>{icon} {label}</div>
        <span style={{ color }}>{score}%</span>
      </div>
      <div className="progress-bar-wrap" style={{ height: 12, borderRadius: 6, background: '#f1f5f9' }}>
        <div className="progress-bar" style={{
          width: `${score}%`,
          background: color,
          borderRadius: 6,
          height: '100%',
          transition: 'width 0.6s ease'
        }} />
      </div>
    </div>
  )
}

function StatCard({ title, value, sub }) {
  return (
    <div className="stat-card" style={{ padding: '24px' }}>
      <div className="stat-info" style={{ marginLeft: 0 }}>
        <div className="stat-label" style={{ fontSize: 13, textTransform: 'uppercase', letterSpacing: 0.8 }}>{title}</div>
        <div className="stat-value" style={{ fontSize: 32, margin: '8px 0', fontWeight: 800 }}>{value}</div>
        <div className="stat-sub">{sub}</div>
      </div>
    </div>
  )
}
