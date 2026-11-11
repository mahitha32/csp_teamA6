// src/pages/FeedbackPage.jsx
import { useEffect, useState } from 'react'
import { feedbackApi } from '../api/api'
import { format } from 'date-fns'

export default function FeedbackPage() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    feedbackApi.getSummary()
      .then(r => setData(r.data.data))
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="spinner-wrap"><div className="spinner" /></div>
  if (!data) return <div className="empty-state">Failed to load feedback</div>

  const { summary, recent_feedback } = data

  const renderStars = (rating) => {
    return <span className="stars">{'★'.repeat(rating)}{'☆'.repeat(5-rating)}</span>
  }

  const renderRatingBar = (stars, count, total) => {
    const pct = total > 0 ? (count / total) * 100 : 0
    return (
      <div className="rating-bar" key={stars}>
        <div className="label">{stars} Stars</div>
        <div className="bar"><div className="fill" style={{ width: `${pct}%` }} /></div>
        <div className="count">{count}</div>
      </div>
    )
  }

  return (
    <div>
      <div className="page-header">
        <div className="page-title">
          <h2>Villager Feedback</h2>
          <p>Post-resolution satisfaction ratings</p>
        </div>
      </div>

      <div className="charts-grid">
        <div className="card">
          <div className="card-header">
            <h3>Feedback Summary</h3>
          </div>
          <div className="card-body" style={{ display: 'flex', gap: 40, alignItems: 'center' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 48, fontWeight: 800, color: 'var(--text-primary)', lineHeight: 1 }}>
                {parseFloat(summary.avg_rating || 0).toFixed(1)}
              </div>
              <div className="stars" style={{ fontSize: 24, margin: '8px 0' }}>★★★★☆</div>
              <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>
                Based on {summary.total_feedback} reviews
              </div>
            </div>
            <div style={{ flex: 1 }}>
              {renderRatingBar(5, summary.five_star || 0, summary.total_feedback)}
              {renderRatingBar(4, summary.four_star || 0, summary.total_feedback)}
              {renderRatingBar(3, summary.three_star || 0, summary.total_feedback)}
              {renderRatingBar(2, summary.two_star || 0, summary.total_feedback)}
              {renderRatingBar(1, summary.one_star || 0, summary.total_feedback)}
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>Recent Reviews</h3>
        </div>
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Complaint ID</th><th>Category</th><th>Villager</th><th>Rating</th><th>Remarks</th><th>Date</th>
              </tr>
            </thead>
            <tbody>
              {recent_feedback.length === 0 ? (
                <tr><td colSpan={6}><div className="empty-state">No feedback received yet</div></td></tr>
              ) : recent_feedback.map((fb, i) => (
                <tr key={i}>
                  <td><code>{fb.complaint_id}</code></td>
                  <td>{fb.category}</td>
                  <td>{fb.user_name}</td>
                  <td style={{ fontSize: 16 }}>{renderStars(fb.rating)}</td>
                  <td style={{ maxWidth: 300, whiteSpace: 'normal', fontStyle: fb.remarks ? 'normal' : 'italic', color: fb.remarks ? 'inherit' : '#94a3b8' }}>
                    {fb.remarks || 'No remarks'}
                  </td>
                  <td>{format(new Date(fb.created_at), 'dd MMM yyyy')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
