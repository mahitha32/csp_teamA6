// src/api/api.js — Axios API client for Vemavaram Village CSP Admin Dashboard
import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({ baseURL: BASE_URL, timeout: 30000 })

// Attach JWT from localStorage
api.interceptors.request.use(cfg => {
  const token = localStorage.getItem('access_token')
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})

// Auto-refresh on 401
api.interceptors.response.use(
  res => res,
  async err => {
    if (err.response?.status === 401) {
      const refresh = localStorage.getItem('refresh_token')
      if (refresh) {
        try {
          const { data } = await axios.post(`${BASE_URL}/auth/refresh`,
            {}, { headers: { Authorization: `Bearer ${refresh}` } })
          localStorage.setItem('access_token', data.data.access_token)
          err.config.headers.Authorization = `Bearer ${data.data.access_token}`
          return api.request(err.config)
        } catch {
          localStorage.clear()
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(err)
  }
)

export const authApi = {
  adminLogin: (mobile, password) =>
    api.post('/auth/admin-login', { mobile, password }),
  getMe: () => api.get('/auth/me'),
  updateProfile: (data) => api.put('/auth/profile', data),
}

export const complaintsApi = {
  getAll: (params) => api.get('/admin/complaints', { params }),
  getById: (id) => api.get(`/complaints/${id}`),
  updateStatus: (id, status, notes) =>
    api.put(`/admin/complaints/${id}/status`, { status, notes }),
  assign: (id, worker_id, notes, expected_date) =>
    api.post(`/admin/complaints/${id}/assign`, { worker_id, notes, expected_date }),
  getCategories: () => api.get('/complaints/categories'),
}

export const workersApi = {
  getAll: (params) => api.get('/workers', { params }),
  create: (data) => api.post('/workers', data),
  update: (id, d) => api.put(`/workers/${id}`, d),
}

export const analyticsApi = {
  getDashboard: () => api.get('/admin/analytics'),
  getSurvey: () => api.get('/admin/survey-insights'),
  getReport: (p) => api.get('/admin/reports', { params: p }),
  getWardStats: () => api.get('/analytics_v2/ward_stats'),
  getGisMap: () => api.get('/analytics_v2/gis_map'),
}

export const feedbackApi = {
  getSummary: () => api.get('/feedback/summary'),
}

export const assetsApi = {
  getAll: () => api.get('/assets'),
  create: (data) => api.post('/assets', data),
}

export const contactApi = {
  getAll: (params) => api.get('/contact', { params }),
}

export default api
