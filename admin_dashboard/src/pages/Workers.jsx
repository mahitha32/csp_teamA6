// src/pages/Workers.jsx
import { useEffect, useState } from 'react'
import { workersApi } from '../api/api'
import toast from 'react-hot-toast'
import { MdAdd, MdEdit, MdClose, MdPeople } from 'react-icons/md'

const DEPARTMENTS = [
  'Roads & Infrastructure','Electrical & Streetlights','Water Supply',
  'Drainage & Sanitation','Waste Management','General Services'
]
const deptIcon = d => ({
  'Roads & Infrastructure':'🛣️','Electrical & Streetlights':'💡',
  'Water Supply':'💧','Drainage & Sanitation':'🌊',
  'Waste Management':'🗑️','General Services':'🔧'
}[d] || '👷')

const EMPTY = { worker_name:'', mobile:'', department:DEPARTMENTS[0] }

export default function Workers() {
  const [workers,  setWorkers]  = useState([])
  const [loading,  setLoading]  = useState(true)
  const [modal,    setModal]    = useState(null)   // null | 'add' | worker obj
  const [form,     setForm]     = useState(EMPTY)
  const [saving,   setSaving]   = useState(false)

  const fetch = () => {
    setLoading(true)
    workersApi.getAll()
      .then(r => setWorkers(r.data.data.workers))
      .catch(() => toast.error('Failed to load workers'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetch() }, [])

  const openAdd  = () => { setForm(EMPTY); setModal('add') }
  const openEdit = w => { setForm({ worker_name:w.worker_name, mobile:w.mobile, department:w.department }); setModal(w) }

  const handleSave = async () => {
    if (!form.worker_name || !form.mobile || !form.department) {
      toast.error('All fields are required'); return
    }
    setSaving(true)
    try {
      if (modal === 'add') {
        await workersApi.create(form)
        toast.success('Worker added successfully!')
      } else {
        await workersApi.update(modal.worker_id, form)
        toast.success('Worker updated!')
      }
      setModal(null); fetch()
    } catch (e) { toast.error(e.response?.data?.message || 'Save failed') }
    finally { setSaving(false) }
  }

  const toggleActive = async (w) => {
    try {
      await workersApi.update(w.worker_id, { is_active: w.is_active ? 0 : 1 })
      toast.success(w.is_active ? 'Worker deactivated' : 'Worker activated')
      fetch()
    } catch { toast.error('Failed to update') }
  }

  return (
    <div>
      <div className="page-header">
        <div className="page-title">
          <h2>Workers Management</h2>
          <p>{workers.length} workers registered</p>
        </div>
        <button className="btn btn-primary" onClick={openAdd}><MdAdd /> Add Worker</button>
      </div>

      {loading ? <div className="spinner-wrap"><div className="spinner"/></div> : (
        <div className="card">
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>ID</th><th>Worker Name</th><th>Department</th>
                  <th>Mobile</th><th>Status</th><th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {workers.length === 0 ? (
                  <tr><td colSpan={6}>
                    <div className="empty-state">
                      <div className="empty-icon">👷</div>
                      <h3>No workers added yet</h3>
                    </div>
                  </td></tr>
                ) : workers.map(w => (
                  <tr key={w.worker_id}>
                    <td style={{color:'#94a3b8', fontSize:12}}>#{w.worker_id}</td>
                    <td>
                      <div style={{display:'flex', alignItems:'center', gap:10}}>
                        <div style={{width:36,height:36,borderRadius:'50%',background:'linear-gradient(135deg,#1a7f5a,#1e6fa8)',display:'flex',alignItems:'center',justifyContent:'center',color:'#fff',fontWeight:700,fontSize:14}}>
                          {w.worker_name[0]}
                        </div>
                        <strong style={{fontSize:14}}>{w.worker_name}</strong>
                      </div>
                    </td>
                    <td><span className="badge">{deptIcon(w.department)} {w.department}</span></td>
                    <td style={{fontSize:13}}>{w.mobile}</td>
                    <td>
                      <span className={`badge ${w.is_active ? 'badge-resolved' : 'badge-rejected'}`}>
                        {w.is_active ? '● Active' : '● Inactive'}
                      </span>
                    </td>
                    <td>
                      <div className="flex gap-2">
                        <button className="btn-icon" title="Edit" onClick={() => openEdit(w)}><MdEdit /></button>
                        <button className="btn btn-outline btn-sm" onClick={() => toggleActive(w)}>
                          {w.is_active ? 'Deactivate' : 'Activate'}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Add / Edit Modal */}
      {modal !== null && (
        <div className="modal-overlay" onClick={() => setModal(null)}>
          <div className="modal" onClick={e => e.stopPropagation()} style={{maxWidth:440}}>
            <div className="modal-header">
              <h3>{modal === 'add' ? 'Add New Worker' : 'Edit Worker'}</h3>
              <button className="modal-close" onClick={() => setModal(null)}><MdClose /></button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label className="form-label">Full Name</label>
                <input className="form-control" placeholder="Worker full name"
                  value={form.worker_name} onChange={e => setForm(f => ({...f, worker_name: e.target.value}))} />
              </div>
              <div className="form-group">
                <label className="form-label">Mobile Number</label>
                <input className="form-control" type="tel" placeholder="10-digit mobile"
                  value={form.mobile} onChange={e => setForm(f => ({...f, mobile: e.target.value}))} maxLength={10} />
              </div>
              <div className="form-group">
                <label className="form-label">Department</label>
                <select className="form-control" value={form.department}
                  onChange={e => setForm(f => ({...f, department: e.target.value}))}>
                  {DEPARTMENTS.map(d => <option key={d}>{d}</option>)}
                </select>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-outline" onClick={() => setModal(null)}>Cancel</button>
              <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
                {saving ? 'Saving…' : modal === 'add' ? 'Add Worker' : 'Save Changes'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
