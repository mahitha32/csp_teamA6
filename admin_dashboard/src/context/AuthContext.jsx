// src/context/AuthContext.jsx
import { createContext, useContext, useState, useEffect } from 'react'
import { authApi } from '../api/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser]       = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token) {
      authApi.getMe()
        .then(r => {
          const u = r.data?.data
          if (u && u.role === 'admin') {
            setUser(u)
          } else {
            localStorage.clear()
            setUser(null)
          }
        })
        .catch(() => {
          localStorage.clear()
          setUser(null)
        })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const login = (tokens, userData) => {
    if (!userData || userData.role !== 'admin') {
      throw new Error('Access denied. Administrator privileges required.')
    }
    localStorage.setItem('access_token',  tokens.access_token)
    localStorage.setItem('refresh_token', tokens.refresh_token)
    setUser(userData)
  }

  const logout = () => {
    localStorage.clear()
    setUser(null)
    window.location.href = '/login'
  }

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
