// src/pages/Complaints.jsx
import { useEffect, useState, useCallback } from 'react'
import { complaintsApi, workersApi } from '../api/api'
import toast from 'react-hot-toast'
import { MdSearch, MdFilterList, MdVisibility, MdAssignment,
         MdEdit, MdImage, MdClose } from 'react-icons/md'
import { format } from 'date-fns'

const STATUSES   = ['Submitted','Under Review','Assigned','In Progress','Resolved','Rejected']
const CATEGORIES = ['Road Issues','Streetlight Issues','Water Supply Problems',
                    'Drainage Problems','Garbage Collection Issues','Sanitation Issues']

const statusClass = s => ({
  'Submitted':'submitted','Under Review':'under-review','Assigned':'assigned',
  'In Progress':'in-progress','Resolved':'resolved','Rejected':'rejected'
}[s] || 'submitted')

const catIcon = c => ({
  'Road Issues':'🛣️','Streetlight Issues':'💡','Water Supply Problems':'💧',
  'Drainage Problems':'🌊','Garbage Collection Issues':'🗑️','Sanitation Issues':'🚽'
}[c] || '📋')

export default function Complaints() {
  const [complaints, setComplaints] = useState([])
  const [pagination, setPagination] = useState({})
  const [workers,    setWorkers]    = useState([])
  const [loading,    setLoading]    = useState(true)
  const [search,     setSearch]     = useState('')
  const [filterStatus,   setFilterStatus]   = useState('')
  const [filterCategory, setFilterCategory] = useState('')
  const [page, setPage] = useState(1)
  // Modals
  const [viewModal,   setViewModal]   = useState(null)  // complaint detail
  const [assignModal, setAssignModal] = useState(null)  // assign worker
  const [statusModal, setStatusModal] = useState(null)  // change status
  const [imageModal,  setImageModal]  = useState(null)  // image preview
  const [selectedWorker, setSelectedWorker] = useState('')
  const [newStatus,      setNewStatus]      = useState('')
  const [statusNotes,    setStatusNotes]    = useState('')

  const fetchComplaints = useCallback(() => {
    setLoading(true)
    complaintsApi.getAll({ page, per_page:12, search, status:filterStatus, category:filterCategory })
      .then(r => { setComplaints(r.data.data.complaints); setPagination(r.data.data.pagination) })
      .catch(() => toast.error('Failed to load complaints'))
      .finally(() => setLoading(false))
  }, [page, search, filterStatus, filterCategory])

  useEffect(() => { fetchComplaints() }, [fetchComplaints])
  useEffect(() => {
    workersApi.getAll({ is_active:1 })
      .then(r => setWorkers(r.data.data.workers))
      .catch(() => {})
  }, [])

  const handleAssign = async () => {
    if (!selectedWorker) { toast.error('Select a worker'); return }
    try {
      await complaintsApi.assign(assignModal.complaint_id, selectedWorker)
      toast.success('Worker assigned!')
      setAssignModal(null); fetchComplaints()
    } catch (e) { toast.error(e.response?.data?.message || 'Failed') }
  }

  const handleStatusChange = async () => {
    if (!newStatus) { toast.error('Select a status'); return }
    try {
      await complaintsApi.updateStatus(statusModal.complaint_id, newStatus, statusNotes)
      toast.success('Status updated!')
      setStatusModal(null); fetchComplaints()
    } catch (e) { toast.error(e.response?.data?.message || 'Failed') }
  }

  const handleView = async (c) => {
    try {
      const { data } = await complaintsApi.getById(c.complaint_id)
      setViewModal(data.data)
    } catch { toast.error('Failed to load details') }
  }

  return (
    <div>
      <div className="page-header">
        <div className="page-title">
          <h2>Complaints Management</h2>
          <p>{pagination.total || 0} total complaints registered</p>
        </div>
      </div>

      <div className="card">
        {/* Filters */}
        <div className="filters-bar">
          <div className="search-wrapper">
            <MdSearch className="search-icon" />
            <input className="search-input" placeholder="Search by ID, title, complainant…"
              value={search} onChange={e => { setSearch(e.target.value); setPage(1) }} />
          </div>
          <select className="form-control" style={{width:160}}
            value={filterStatus} onChange={e => { setFilterStatus(e.target.value); setPage(1) }}>
            <option value="">All Statuses</option>
            {STATUSES.map(s => <option key={s}>{s}</option>)}
          </select>
          <select className="form-control" style={{width:200}}
            value={filterCategory} onChange={e => { setFilterCategory(e.target.value); setPage(1) }}>
            <option value="">All Categories</option>
            {CATEGORIES.map(c => <option key={c}>{c}</option>)}
          </select>
          <button className="btn btn-outline btn-sm" onClick={fetchComplaints}>
            <MdFilterList /> Refresh
          </button>
        </div>

        {/* Table */}
        {loading ? <div className="spinner-wrap"><div className="spinner"/></div> : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>ID</th><th>Title</th><th>Category</th>
                  <th>Complainant</th><th>Status</th><th>Priority</th>
                  <th>Worker</th><th>Date</th><th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {complaints.length === 0 ? (
                  <tr><td colSpan={9}>
                    <div className="empty-state">
                      <div className="empty-icon">📋</div>
                      <h3>No complaints found</h3>
                    </div>
                  </td></tr>
                ) : complaints.map(c => (
                  <tr key={c.complaint_id}>
                    <td><code style={{fontSize:12, background:'#f1f5f9', padding:'2px 6px', borderRadius:4}}>{c.complaint_id}</code></td>
                    <td style={{maxWidth:180}}>
                      <div style={{fontWeight:600, fontSize:13}}>{c.title}</div>
                      {c.image_url && (
                        <img src={c.image_url} alt="" className="complaint-img"
                          style={{marginTop:4}} onClick={() => setImageModal(c.image_url)} />
                      )}
                    </td>
                    <td><span className="badge">{catIcon(c.category)} {c.category}</span></td>
                    <td>
                      <div style={{fontSize:13, fontWeight:600}}>{c.user_name}</div>
                      <div style={{fontSize:11, color:'#94a3b8'}}>{c.user_mobile}</div>
                    </td>
                    <td><span className={`badge badge-${statusClass(c.status)}`}>{c.status}</span></td>
                    <td><span className={`badge badge-${(c.priority||'medium').toLowerCase()}`}>{c.priority}</span></td>
                    <td style={{fontSize:12}}>{c.worker_name || <span className="text-muted">—</span>}</td>
                    <td style={{fontSize:12, color:'#64748b'}}>{c.created_at ? format(new Date(c.created_at),'dd MMM yyyy') : '—'}</td>
                    <td>
                      <div className="flex gap-2">
                        <button className="btn-icon" title="View Details" onClick={() => handleView(c)}><MdVisibility /></button>
                        <button className="btn-icon" title="Assign Worker"
                          onClick={() => { setAssignModal(c); setSelectedWorker('') }}><MdAssignment /></button>
                        <button className="btn-icon" title="Change Status"
                          onClick={() => { setStatusModal(c); setNewStatus(c.status); setStatusNotes('') }}><MdEdit /></button>
                        {c.image_url && <button className="btn-icon" title="View Image"
                          onClick={() => setImageModal(c.image_url)}><MdImage /></button>}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {pagination.pages > 1 && (
          <div className="flex gap-2 items-center" style={{padding:'16px 24px', borderTop:'1px solid #e2e8f0'}}>
            <button className="btn btn-outline btn-sm" disabled={page<=1} onClick={()=>setPage(p=>p-1)}>← Prev</button>
            <span style={{fontSize:13, color:'#64748b'}}>Page {page} of {pagination.pages}</span>
            <button className="btn btn-outline btn-sm" disabled={page>=pagination.pages} onClick={()=>setPage(p=>p+1)}>Next →</button>
          </div>
        )}
      </div>

      {/* View Detail Modal */}
      {viewModal && (
        <div className="modal-overlay" onClick={() => setViewModal(null)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{viewModal.complaint_id} — {viewModal.title}</h3>
              <button className="modal-close" onClick={() => setViewModal(null)}><MdClose /></button>
            </div>
            <div className="modal-body">
              <div className="grid-2">
                <div><label className="form-label">Category</label><p>{viewModal.category}</p></div>
                <div><label className="form-label">Status</label>
                  <span className={`badge badge-${statusClass(viewModal.status)}`}>{viewModal.status}</span></div>
                <div><label className="form-label">Location</label><p>{viewModal.location}</p></div>
                <div><label className="form-label">Priority</label><p>{viewModal.priority}</p></div>
              </div>
              <div className="form-group mt-16">
                <label className="form-label">Description</label>
                <p style={{fontSize:14, color:'#475569', lineHeight:1.7}}>{viewModal.description}</p>
              </div>
              {viewModal.image_url && (
                <div className="form-group">
                  <label className="form-label">Complaint Photo</label>
                  <img src={viewModal.image_url} alt="Complaint" style={{width:'100%', borderRadius:8, maxHeight:300, objectFit:'cover'}} />
                </div>
              )}
              {viewModal.status_history?.length > 0 && (
                <div className="form-group">
                  <label className="form-label">Status Timeline</label>
                  {viewModal.status_history.map((h,i) => (
                    <div key={i} style={{display:'flex', gap:10, alignItems:'flex-start', marginBottom:8}}>
                      <div style={{width:8, height:8, borderRadius:'50%', background:'#1a56db', marginTop:6, flexShrink:0}} />
                      <div>
                        <strong style={{fontSize:13}}>{h.new_status}</strong>
                        <span style={{fontSize:11, color:'#94a3b8', marginLeft:8}}>{h.changed_at ? format(new Date(h.changed_at),'dd MMM yyyy HH:mm') : ''}</span>
                        {h.notes && <p style={{fontSize:12, color:'#64748b'}}>{h.notes}</p>}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Assign Worker Modal */}
      {assignModal && (
        <div className="modal-overlay" onClick={() => setAssignModal(null)}>
          <div className="modal" onClick={e => e.stopPropagation()} style={{maxWidth:400}}>
            <div className="modal-header">
              <h3>Assign Worker</h3>
              <button className="modal-close" onClick={() => setAssignModal(null)}><MdClose /></button>
            </div>
            <div className="modal-body">
              <p style={{fontSize:13, marginBottom:16, color:'#475569'}}>
                Assigning worker to: <strong>{assignModal.complaint_id}</strong>
              </p>
              <div className="form-group">
                <label className="form-label">Select Worker</label>
                <select className="form-control" value={selectedWorker} onChange={e => setSelectedWorker(e.target.value)}>
                  <option value="">Choose a worker…</option>
                  {workers.map(w => (
                    <option key={w.worker_id} value={w.worker_id}>
                      {w.worker_name} — {w.department}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-outline" onClick={() => setAssignModal(null)}>Cancel</button>
              <button className="btn btn-primary" onClick={handleAssign}>Assign</button>
            </div>
          </div>
        </div>
      )}

      {/* Status Modal */}
      {statusModal && (
        <div className="modal-overlay" onClick={() => setStatusModal(null)}>
          <div className="modal" onClick={e => e.stopPropagation()} style={{maxWidth:420}}>
            <div className="modal-header">
              <h3>Update Status</h3>
              <button className="modal-close" onClick={() => setStatusModal(null)}><MdClose /></button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label className="form-label">New Status</label>
                <select className="form-control" value={newStatus} onChange={e => setNewStatus(e.target.value)}>
                  {STATUSES.map(s => <option key={s}>{s}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Notes (optional)</label>
                <textarea className="form-control" rows={3} value={statusNotes}
                  onChange={e => setStatusNotes(e.target.value)} placeholder="Add a note…" />
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-outline" onClick={() => setStatusModal(null)}>Cancel</button>
              <button className="btn btn-primary" onClick={handleStatusChange}>Update</button>
            </div>
          </div>
        </div>
      )}

      {/* Image Preview Modal */}
      {imageModal && (
        <div className="modal-overlay" onClick={() => setImageModal(null)}>
          <img src={imageModal} alt="Complaint" style={{maxWidth:'90vw', maxHeight:'90vh', borderRadius:12, boxShadow:'0 20px 60px rgba(0,0,0,0.5)'}} />
        </div>
      )}
    </div>
  )
}
