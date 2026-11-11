// src/pages/AssetRegistry.jsx
import { useState, useEffect } from 'react'
import { assetsApi } from '../api/api'
import toast from 'react-hot-toast'
import { MdAdd, MdLocationOn, MdClose, MdRefresh } from 'react-icons/md'

export default function AssetRegistry() {
  const [assets, setAssets]   = useState([])
  const [loading, setLoading] = useState(true)
  const [modal, setModal]     = useState(false)
  const [saving, setSaving]   = useState(false)
  const [form, setForm]       = useState({
    asset_id: '',
    type: 'Streetlight',
    ward_id: 1,
    location_lat: 16.4866,
    location_lng: 80.6433,
    status: 'Active'
  })

  const fetchAssets = () => {
    setLoading(true)
    assetsApi.getAll()
      .then(r => setAssets(r.data?.data?.assets || []))
      .catch(() => toast.error('Failed to load asset registry'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    fetchAssets()
  }, [])

  const handleAdd = async (e) => {
    e.preventDefault()
    if (!form.asset_id.trim()) {
      toast.error('Asset ID is required (e.g. AST-VEM-01)')
      return
    }
    setSaving(true)
    try {
      await assetsApi.create(form)
      toast.success('Asset registered successfully!')
      setModal(false)
      setForm({ asset_id: '', type: 'Streetlight', ward_id: 1, location_lat: 16.4866, location_lng: 80.6433, status: 'Active' })
      fetchAssets()
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to register asset')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div>
      <div className="page-header">
        <div className="page-title">
          <h2>Village Asset Registry — Vemavaram</h2>
          <p>Verified public infrastructure inventory tracked in MySQL</p>
        </div>
        <div className="flex gap-2">
          <button className="btn btn-outline" onClick={fetchAssets}><MdRefresh /> Refresh</button>
          <button className="btn btn-primary" onClick={() => setModal(true)}><MdAdd /> Add New Asset</button>
        </div>
      </div>

      <div className="card">
        {loading ? (
          <div className="spinner-wrap"><div className="spinner" /></div>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Asset ID</th>
                  <th>Type</th>
                  <th>Ward</th>
                  <th>Status</th>
                  <th>Coordinates</th>
                  <th>Installed Date</th>
                </tr>
              </thead>
              <tbody>
                {assets.length === 0 ? (
                  <tr>
                    <td colSpan={6}>
                      <div className="empty-state">
                        <div className="empty-icon">🏗️</div>
                        <h3>No assets registered yet</h3>
                        <p>Tracked village infrastructure will appear here.</p>
                      </div>
                    </td>
                  </tr>
                ) : (
                  assets.map(a => (
                    <tr key={a.asset_id || a.id}>
                      <td><code style={{ background: '#f1f5f9', padding: '2px 6px', borderRadius: 4 }}>{a.asset_id}</code></td>
                      <td style={{ fontWeight: 600 }}>{a.type}</td>
                      <td>Ward {a.ward_id || 1} {a.ward_name ? `(${a.ward_name})` : ''}</td>
                      <td>
                        <span className={`badge ${a.status === 'Active' ? 'badge-low' : a.status === 'Broken' ? 'badge-urgent' : 'badge-medium'}`}>
                          {a.status}
                        </span>
                      </td>
                      <td style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                        {a.location_lat && a.location_lng ? `${parseFloat(a.location_lat).toFixed(4)}, ${parseFloat(a.location_lng).toFixed(4)}` : 'N/A'}
                      </td>
                      <td style={{ fontSize: 12 }}>{a.created_at ? new Date(a.created_at).toLocaleDateString() : 'N/A'}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add Asset Modal */}
      {modal && (
        <div className="modal-overlay" onClick={() => setModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()} style={{ maxWidth: 440 }}>
            <div className="modal-header">
              <h3>Register Infrastructure Asset</h3>
              <button className="modal-close" onClick={() => setModal(false)}><MdClose /></button>
            </div>
            <form onSubmit={handleAdd}>
              <div className="modal-body">
                <div className="form-group">
                  <label className="form-label">Asset ID *</label>
                  <input
                    className="form-control"
                    placeholder="e.g. AST-VEM-001"
                    required
                    value={form.asset_id}
                    onChange={e => setForm({ ...form, asset_id: e.target.value.toUpperCase() })}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Infrastructure Type</label>
                  <select
                    className="form-control"
                    value={form.type}
                    onChange={e => setForm({ ...form, type: e.target.value })}
                  >
                    <option value="Streetlight">Streetlight</option>
                    <option value="Water Tank">Water Tank / Borewell</option>
                    <option value="Drainage Line">Drainage Line</option>
                    <option value="Road Segment">Road Segment</option>
                    <option value="Public Toilet">Public Toilet</option>
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Ward Number</label>
                  <select
                    className="form-control"
                    value={form.ward_id}
                    onChange={e => setForm({ ...form, ward_id: parseInt(e.target.value) })}
                  >
                    {[1, 2, 3, 4, 5].map(w => (
                      <option key={w} value={w}>Ward {w} (Vemavaram)</option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Status</label>
                  <select
                    className="form-control"
                    value={form.status}
                    onChange={e => setForm({ ...form, status: e.target.value })}
                  >
                    <option value="Active">Active / Operational</option>
                    <option value="Maintenance Required">Maintenance Required</option>
                    <option value="Under Repair">Under Repair</option>
                    <option value="Broken">Broken</option>
                  </select>
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-outline" onClick={() => setModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={saving}>
                  {saving ? 'Registering…' : 'Save Asset'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
