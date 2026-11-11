// src/App.jsx — Admin Dashboard Routing & Authentication Barrier
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider, useAuth } from './context/AuthContext'
import Sidebar  from './components/Sidebar'
import Header   from './components/Header'
import Login    from './pages/Login'
import Dashboard    from './pages/Dashboard'
import Complaints   from './pages/Complaints'
import Workers      from './pages/Workers'
import Reports      from './pages/Reports'
import FeedbackPage from './pages/FeedbackPage'
import SurveyInsights from './pages/SurveyInsights'
import CommunityImpact from './pages/CommunityImpact'
import VillageMapComponent from './components/VillageMap'
import LandingPage from './pages/LandingPage'
import WardAnalytics from './pages/WardAnalytics'
import AssetRegistry from './pages/AssetRegistry'

function VillageMapPage() {
  return (
    <div>
      <div className="page-header">
        <div className="page-title">
          <h2>Interactive Village Map — Vemavaram</h2>
          <p>Geospatial distribution of reported village complaints</p>
        </div>
      </div>
      <div className="card" style={{ padding: 20 }}>
        <VillageMapComponent />
      </div>
    </div>
  )
}

function PrivateLayout() {
  const { user, loading } = useAuth()
  if (loading) return (
    <div className="spinner-wrap" style={{ height: '100vh' }}>
      <div className="spinner" />
    </div>
  )
  if (!user || user.role !== 'admin') {
    return <Navigate to="/login" replace />
  }

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-content">
        <Header />
        <div className="page-body">
          <Routes>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/complaints" element={<Complaints />} />
            <Route path="/workers"    element={<Workers />} />
            <Route path="/reports"    element={<Reports />} />
            <Route path="/feedback"   element={<FeedbackPage />} />
            <Route path="/survey"     element={<SurveyInsights />} />
            <Route path="/impact"     element={<CommunityImpact />} />
            <Route path="/map"        element={<VillageMapPage />} />
            <Route path="/wards"      element={<WardAnalytics />} />
            <Route path="/assets"     element={<AssetRegistry />} />
            <Route path="*"           element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </div>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Toaster position="top-right" toastOptions={{ style: { fontFamily: 'Inter, sans-serif', fontSize: 14 } }} />
        <Routes>
          <Route path="/"      element={<LandingPage />} />
          <Route path="/login" element={<Login />} />
          <Route path="/*"     element={<PrivateLayout />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
