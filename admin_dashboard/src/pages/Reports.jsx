// src/pages/Reports.jsx
import { useState } from 'react'
import { analyticsApi } from '../api/api'
import toast from 'react-hot-toast'
import { MdDownload, MdPictureAsPdf } from 'react-icons/md'
import { format } from 'date-fns'

export default function Reports() {
  const [filters, setFilters] = useState({ from_date: '', to_date: '', category: '' })
  const [report,  setReport]  = useState(null)
  const [loading, setLoading] = useState(false)

  const CATEGORIES = ['Road Issues','Streetlight Issues','Water Supply Problems','Drainage Problems','Garbage Collection Issues','Sanitation Issues']

  const handleGenerate = async () => {
    setLoading(true)
    try {
      const { data } = await analyticsApi.getReport(filters)
      setReport(data.data.report)
      toast.success('Report generated successfully')
    } catch (e) {
      toast.error('Failed to generate report')
    } finally {
      setLoading(false)
    }
  }

  const handleExportCSV = () => {
    if (!report || report.length === 0) return toast.error('No data to export')
    
    // Simple CSV conversion
    const headers = ['Complaint ID', 'Title', 'Category', 'Status', 'Location', 'Created At', 'Resolved At', 'Complainant', 'Worker', 'Rating']
    const csvRows = [headers.join(',')]
    
    report.forEach(row => {
      const r = [
        row.complaint_id,
        `"${row.title.replace(/"/g, '""')}"`,
        row.category,
        row.status,
        `"${row.location.replace(/"/g, '""')}"`,
        row.created_at,
        row.resolved_at || 'N/A',
        row.complainant_name,
        row.worker_name || 'Unassigned',
        row.rating || 'N/A'
      ]
      csvRows.push(r.join(','))
    })
    
    const blob = new Blob([csvRows.join('\n')], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `Vemavaram_CSP_Report_${format(new Date(), 'yyyyMMdd_HHmmss')}.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  }

  return (
    <div>
      <div className="page-header">
        <div className="page-title">
          <h2>Reports & Analytics</h2>
          <p>Generate detailed complaint reports and export data</p>
        </div>
      </div>

      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-header">
          <h3>Report Filters</h3>
        </div>
        <div className="card-body">
          <div className="filters-bar" style={{ background: 'transparent', padding: 0, border: 'none' }}>
            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label">From Date</label>
              <input type="date" className="form-control" value={filters.from_date} onChange={e => setFilters({...filters, from_date: e.target.value})} />
            </div>
            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label">To Date</label>
              <input type="date" className="form-control" value={filters.to_date} onChange={e => setFilters({...filters, to_date: e.target.value})} />
            </div>
            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label">Category</label>
              <select className="form-control" value={filters.category} onChange={e => setFilters({...filters, category: e.target.value})}>
                <option value="">All Categories</option>
                {CATEGORIES.map(c => <option key={c}>{c}</option>)}
              </select>
            </div>
            <div className="form-group" style={{ display: 'flex', alignItems: 'flex-end' }}>
              <button className="btn btn-primary" style={{ height: 42 }} onClick={handleGenerate} disabled={loading}>
                {loading ? 'Generating...' : 'Generate Report'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {report && (
        <div className="card">
          <div className="card-header">
            <div>
              <h3>Report Results</h3>
              <p>Found {report.length} records</p>
            </div>
            <div className="flex gap-2">
              <button className="btn btn-outline" onClick={handleExportCSV}>
                <MdDownload /> Export CSV
              </button>
            </div>
          </div>
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>ID</th><th>Title</th><th>Status</th><th>Date</th><th>Worker</th>
                </tr>
              </thead>
              <tbody>
                {report.length === 0 ? (
                  <tr><td colSpan={5}><div className="empty-state">No records found for selected filters</div></td></tr>
                ) : report.map((r, i) => (
                  <tr key={i}>
                    <td><code>{r.complaint_id}</code></td>
                    <td><div style={{fontWeight:500}}>{r.title}</div><div style={{fontSize:11, color:'#64748b'}}>{r.category}</div></td>
                    <td><span className="badge">{r.status}</span></td>
                    <td>{format(new Date(r.created_at), 'dd MMM yyyy')}</td>
                    <td>{r.worker_name || 'â€”'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

