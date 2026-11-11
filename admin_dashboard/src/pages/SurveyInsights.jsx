// src/pages/SurveyInsights.jsx
import { useEffect, useState } from 'react'
import { analyticsApi } from '../api/api'

export default function SurveyInsights() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    analyticsApi.getSurvey()
      .then(r => setData(r.data.data))
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="spinner-wrap"><div className="spinner" /></div>
  if (!data) return <div className="empty-state">Failed to load survey data</div>

  const { village, total_responses, survey_year, insights } = data

  const getIcon = (category) => {
    if (category.includes('Road')) return '🛣️'
    if (category.includes('Water')) return '💧'
    if (category.includes('Light')) return '💡'
    if (category.includes('Drain')) return '🌊'
    if (category.includes('Garbage')) return '🗑️'
    return '📋'
  }

  return (
    <div>
      <div className="page-header">
        <div className="page-title">
          <h2>Village Survey Insights</h2>
          <p>Field survey data for {village} ({survey_year})</p>
        </div>
        <div style={{ background: 'var(--surface)', padding: '8px 16px', borderRadius: 8, border: '1px solid var(--border)', fontSize: 14, fontWeight: 600 }}>
          Total Respondents: <span style={{ color: 'var(--primary)', fontSize: 16 }}>{total_responses}</span>
        </div>
      </div>

      <div className="insights-grid">
        {insights.map((ins, i) => (
          <div className="insight-card" key={i}>
            <div className="insight-header">
              <div className="insight-icon" style={{ background: 'var(--surface-2)' }}>
                {getIcon(ins.category)}
              </div>
              <div>
                <h4>{ins.category}</h4>
              </div>
            </div>
            
            <span className={`severity severity-${ins.severity.toLowerCase()}`}>
              {ins.severity} Priority
            </span>
            
            <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 16, minHeight: 40 }}>
              {ins.description}
            </p>

            <div className="progress-bar-wrap">
              <div className="progress-bar" style={{ 
                width: `${ins.percentage}%`,
                background: ins.severity === 'Critical' ? 'var(--danger)' :
                            ins.severity === 'High' ? 'var(--warning)' : 'var(--primary)'
              }} />
            </div>
            
            <div className="insight-stats">
              <span>{ins.response_count} households affected</span>
              <span style={{ fontWeight: 600 }}>{ins.percentage}%</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
