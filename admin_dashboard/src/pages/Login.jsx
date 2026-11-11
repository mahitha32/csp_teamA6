// src/pages/Login.jsx
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { authApi } from '../api/api'
import toast from 'react-hot-toast'

export default function Login() {
  const [mobile,   setMobile]   = useState('')
  const [password, setPassword] = useState('')
  const [loading,  setLoading]  = useState(false)
  const { login } = useAuth()
  const navigate  = useNavigate()

  const handleSubmit = async e => {
    e.preventDefault()
    const cleanMobile = mobile.trim().replace(/\D/g, '')
    if (!cleanMobile || !password) {
      toast.error('Please enter your mobile number and password')
      return
    }
    setLoading(true)
    try {
      const { data } = await authApi.adminLogin(cleanMobile, password)
      const payload = data.data
      if (payload?.user?.role !== 'admin') {
        toast.error('Access denied. Administrator privileges required.')
        return
      }
      login(payload, payload.user)
      toast.success(`Welcome back, ${payload.user.name || 'Admin'}!`)
      navigate('/dashboard')
    } catch (err) {
      const msg = err.response?.data?.message || err.message || 'Login failed'
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-logo">🏛️</div>
        <h1>Vemavaram Village CSP</h1>
        <p className="subtitle">Complaint Redressal System — Admin Portal</p>
        <form className="login-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Admin Mobile Number</label>
            <input
              className="form-control"
              type="tel"
              placeholder="9999900000"
              value={mobile}
              onChange={e => setMobile(e.target.value)}
              maxLength={10}
              disabled={loading}
              required
            />
          </div>
          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              className="form-control"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={e => setPassword(e.target.value)}
              disabled={loading}
              required
            />
          </div>
          <button className="login-btn" type="submit" disabled={loading}>
            {loading ? 'Authenticating…' : 'Sign In to Admin Portal'}
          </button>
        </form>
        <p style={{ marginTop: 24, fontSize: 12, color: '#94a3b8' }}>
          Official Vemavaram Panchayat Administration Portal
        </p>
      </div>
    </div>
  )
}
