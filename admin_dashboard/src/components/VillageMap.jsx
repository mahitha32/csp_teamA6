// src/components/VillageMap.jsx
import { useEffect, useState } from 'react'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'
import { complaintsApi, analyticsApi } from '../api/api'
import { MdFilterList, MdLocationOff } from 'react-icons/md'

// Fix default icon issue with React-Leaflet
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

// Vemavaram Village center coordinates (Krishna District, AP)
const VEMAVARAM_CENTER = [16.4866, 80.6433]

const CATEGORIES = [
  'All',
  'Road Issues',
  'Streetlight Issues',
  'Water Supply Problems',
  'Drainage Problems',
  'Garbage Collection Issues',
  'Sanitation Issues'
]

const WARDS = ['All', '1', '2', '3', '4', '5']

// Custom colored pin creator
const createStatusIcon = (status) => {
  const color =
    status === 'Resolved' ? '#10b981' :
    status === 'In Progress' ? '#3b82f6' :
    status === 'Assigned' ? '#8b5cf6' :
    status === 'Rejected' ? '#ef4444' : '#f59e0b'

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="30" height="30">
    <path fill="${color}" stroke="#ffffff" stroke-width="1.5" d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5a2.5 2.5 0 0 1 0-5 2.5 2.5 0 0 1 0 5z"/>
  </svg>`

  return L.divIcon({
    className: 'custom-map-pin',
    html: svg,
    iconSize: [30, 30],
    iconAnchor: [15, 30],
    popupAnchor: [0, -28]
  })
}

export default function VillageMap() {
  const [complaints, setComplaints] = useState([])
  const [loading, setLoading]       = useState(true)
  const [categoryFilter, setCategoryFilter] = useState('All')
  const [wardFilter, setWardFilter]         = useState('All')

  useEffect(() => {
    setLoading(true)
    // Fetch all complaints from backend
    complaintsApi.getAll({ per_page: 100 })
      .then(r => {
        const list = r.data?.data?.complaints || []
        setComplaints(list)
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  // Filter complaints that possess valid geographic coordinates
  const validMarkers = complaints.filter(c => {
    const lat = parseFloat(c.latitude)
    const lng = parseFloat(c.longitude)
    if (isNaN(lat) || isNaN(lng)) return false

    if (categoryFilter !== 'All' && c.category !== categoryFilter) return false
    if (wardFilter !== 'All' && String(c.ward_id) !== wardFilter) return false

    return true
  })

  return (
    <div>
      {/* Map Filter Controls */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, marginBottom: 16, alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 13, fontWeight: 600 }}>
          <MdFilterList /> Filter Map:
        </div>

        <select
          className="form-control"
          style={{ width: 180, fontSize: 13 }}
          value={categoryFilter}
          onChange={e => setCategoryFilter(e.target.value)}
        >
          {CATEGORIES.map(cat => (
            <option key={cat} value={cat}>{cat === 'All' ? 'All Categories' : cat}</option>
          ))}
        </select>

        <select
          className="form-control"
          style={{ width: 140, fontSize: 13 }}
          value={wardFilter}
          onChange={e => setWardFilter(e.target.value)}
        >
          {WARDS.map(w => (
            <option key={w} value={w}>{w === 'All' ? 'All Wards' : `Ward ${w}`}</option>
          ))}
        </select>

        <span style={{ fontSize: 12, color: 'var(--text-muted)', marginLeft: 'auto' }}>
          Showing {validMarkers.length} mapped issues in Vemavaram
        </span>
      </div>

      {/* Map Container */}
      <div className="map-wrapper" style={{ height: '480px', width: '100%', borderRadius: '12px', overflow: 'hidden', border: '1px solid var(--border)', position: 'relative' }}>
        {loading ? (
          <div className="spinner-wrap" style={{ height: '100%' }}><div className="spinner" /></div>
        ) : (
          <MapContainer center={VEMAVARAM_CENTER} zoom={14} style={{ height: '100%', width: '100%' }}>
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            />

            {validMarkers.map(c => {
              const lat = parseFloat(c.latitude)
              const lng = parseFloat(c.longitude)
              const icon = createStatusIcon(c.status)

              return (
                <Marker key={c.complaint_id} position={[lat, lng]} icon={icon}>
                  <Popup>
                    <div style={{ minWidth: 200, padding: 4 }}>
                      <div style={{ fontSize: 11, fontWeight: 700, color: '#64748b' }}>{c.complaint_id}</div>
                      <strong style={{ display: 'block', fontSize: 13, margin: '2px 0 4px', color: '#0f172a' }}>{c.title}</strong>
                      <div style={{ fontSize: 12, color: '#334155', marginBottom: 6 }}>{c.category} • Ward {c.ward_id || 'General'}</div>
                      <div style={{ fontSize: 11, color: '#64748b', marginBottom: 8 }}>📍 {c.location}</div>
                      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                        <span className={`badge badge-${c.status?.toLowerCase()?.replace(' ', '-')}`}>{c.status}</span>
                        <span className={`badge badge-${c.priority?.toLowerCase()}`}>{c.priority} Priority</span>
                      </div>
                    </div>
                  </Popup>
                </Marker>
              )
            })}
          </MapContainer>
        )}

        {/* Empty state overlay if zero markers have GPS data */}
        {!loading && validMarkers.length === 0 && (
          <div style={{
            position: 'absolute', bottom: 16, left: 16, right: 16, zIndex: 1000,
            background: 'rgba(255, 255, 255, 0.95)', padding: '12px 16px', borderRadius: 8,
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)', display: 'flex', alignItems: 'center', gap: 10,
            fontSize: 12, color: '#475569', border: '1px solid #e2e8f0'
          }}>
            <MdLocationOff size={20} color="#f59e0b" style={{ flexShrink: 0 }} />
            <span>
              No complaints with GPS coordinates found for the selected filter. Geotagged complaints registered from the mobile app or citizen portal will automatically appear here.
            </span>
          </div>
        )}
      </div>

      {/* Legend */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16, marginTop: 12, fontSize: 12, color: 'var(--text-secondary)' }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#f59e0b', display: 'inline-block' }} /> Submitted / Pending
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#3b82f6', display: 'inline-block' }} /> In Progress
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#8b5cf6', display: 'inline-block' }} /> Assigned
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#10b981', display: 'inline-block' }} /> Resolved
        </span>
      </div>
    </div>
  )
}
