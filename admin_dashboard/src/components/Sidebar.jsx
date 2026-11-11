// src/components/Sidebar.jsx
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import {
  MdDashboard, MdReportProblem, MdPeople,
  MdBarChart, MdFeedback, MdInsights, MdLogout, MdMap, MdPublic, MdLocationCity, MdCategory
} from 'react-icons/md'

const nav = [
  { to: '/dashboard',            icon: <MdDashboard />,     label: 'Dashboard' },
  { to: '/map',         icon: <MdMap />,           label: 'Village Map' },
  { to: '/complaints',  icon: <MdReportProblem />,  label: 'Complaints' },
  { to: '/workers',     icon: <MdPeople />,         label: 'Workers' },
  { to: '/reports',     icon: <MdBarChart />,        label: 'Reports' },
  { to: '/wards',       icon: <MdLocationCity />,    label: 'Ward Analytics' },
  { to: '/assets',      icon: <MdCategory />,        label: 'Assets Registry' },
  { to: '/feedback',    icon: <MdFeedback />,        label: 'Feedback' },
  { to: '/survey',      icon: <MdInsights />,        label: 'Survey Insights' },
  { to: '/impact',      icon: <MdPublic />,          label: 'Community Impact' },
]

export default function Sidebar() {
  const { logout } = useAuth()
  const navigate   = useNavigate()

  const handleLogout = () => { logout(); navigate('/login') }

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="village-badge">
          <div className="icon">🏘️</div>
          <div>
            <h2>Vemavaram Village</h2>
            <p>CSP Admin Panel</p>
          </div>
        </div>
      </div>

      <nav className="sidebar-nav">
        <div className="nav-section-label">Main Menu</div>
        {nav.map(item => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/dashboard'}
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            {item.icon}
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <button className="logout-btn" onClick={handleLogout}>
          <MdLogout /> Logout
        </button>
      </div>
    </aside>
  )
}
