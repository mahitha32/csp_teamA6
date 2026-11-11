// src/components/SLAWarnings.jsx
import { useEffect, useState } from 'react'
import { complaintsApi } from '../api/api'
import { MdWarning, MdCheckCircle } from 'react-icons/md'

export default function SLAWarnings() {
  const [warnings, setWarnings] = useState([])
  const [loading, setLoading]   = useState(true)

  useEffect(() => {
    // Check for open complaints that need attention
    complaintsApi.getAll({ per_page: 50 })
      .then(r => {
        const complaints = r.data?.data?.complaints || []
        const alerts = []
        const now = new Date()

        complaints.forEach(c => {
          if (c.status !== 'Resolved' && c.status !== 'Rejected') {
            const created = new Date(c.created_at)
            const diffHours = (now - created) / (1000 * 60 * 60)
            const daysOpen = Math.floor(diffHours / 24)

            // SLA thresholds based on category
            const maxDays = c.category === 'Drinking Water' || c.category === 'Water Supply Problems' ? 2 :
                            c.category === 'Sanitation Issues' || c.category === 'Drainage Problems' ? 3 : 5

            if (daysOpen >= maxDays) {
              alerts.push({
                complaintId: c.complaint_id,
                category: c.category,
                daysOpen,
                maxDays,
                level: 'Breached',
                location: c.location,
              })
            } else if (daysOpen >= maxDays - 1) {
              alerts.push({
                complaintId: c.complaint_id,
                category: c.category,
                daysOpen,
                maxDays,
                level: 'Warning',
                location: c.location,
              })
            }
          }
        })
        setWarnings(alerts)
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading || warnings.length === 0) return null

  return (
    <div style={{ marginBottom: 24 }}>
      <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8, color: 'var(--danger)' }}>
        <MdWarning /> Live SLA Alerts ({warnings.length})
      </h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 16 }}>
        {warnings.map(w => (
          <div key={w.complaintId} style={{
            background: w.level === 'Breached' ? '#fef2f2' : '#fffbeb',
            border: `1px solid ${w.level === 'Breached' ? '#fca5a5' : '#fcd34d'}`,
            padding: 16, borderRadius: 8
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
              <strong style={{ color: w.level === 'Breached' ? '#dc2626' : '#d97706' }}>{w.complaintId}</strong>
              <span className={`badge ${w.level === 'Breached' ? 'badge-urgent' : 'badge-medium'}`}>{w.level}</span>
            </div>
            <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
              {w.category} issue open for {w.daysOpen} days (SLA limit: {w.maxDays} days).
              <br />
              {w.level === 'Breached' ? 'SLA breached. Escalated to Panchayat Officer.' : 'Approaching SLA deadline.'}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
