// src/components/Header.jsx
import { useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const titles = {
  '/dashboard':  { title: 'Dashboard', sub: 'Overview of village complaints and metrics' },
  '/map':        { title: 'Interactive Village Map', sub: 'Geospatial analysis of infrastructure complaints' },
  '/complaints': { title: 'Complaints Management', sub: 'Manage, assign and resolve village complaints' },
  '/workers':    { title: 'Workers Management', sub: 'Assign tasks and monitor field staff' },
  '/reports':    { title: 'Reports & Export', sub: 'Generate and export CSV complaint reports' },
  '/wards':      { title: 'Ward Analytics', sub: 'Performance metrics across Wards 1 to 5' },
  '/assets':     { title: 'Asset Registry', sub: 'Public infrastructure tracking' },
  '/feedback':   { title: 'Citizen Feedback', sub: 'Post-resolution ratings and reviews' },
  '/survey':     { title: 'Survey Insights', sub: 'Vemavaram Village field survey results' },
  '/impact':     { title: 'Community Impact', sub: 'Civic performance and infrastructure health index' },
}

export default function Header() {
  const { pathname } = useLocation()
  const { user }     = useAuth()
  const meta = titles[pathname] || { title: 'Panchayat Administration', sub: 'Vemavaram Village Digital Governance' }

  return (
    <header className="header">
      <div className="header-left">
        <h1>{meta.title}</h1>
        <p>{meta.sub}</p>
      </div>
      <div className="header-right">
        <div className="header-admin">
          <div className="admin-info">
            <strong>{user?.name || 'Village Administrator'}</strong>
            <span>Panchayat Officer • Vemavaram</span>
          </div>
          <div className="admin-avatar">
            {(user?.name || 'A')[0].toUpperCase()}
          </div>
        </div>
      </div>
    </header>
  )
}
