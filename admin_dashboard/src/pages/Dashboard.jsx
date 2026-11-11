// src/pages/Dashboard.jsx
import { useEffect, useState } from 'react'
import { analyticsApi } from '../api/api'
import { Bar, Pie, Line } from 'react-chartjs-2'
import {
  Chart as ChartJS, CategoryScale, LinearScale, BarElement,
  PointElement, LineElement, ArcElement, Title, Tooltip, Legend, Filler
} from 'chart.js'
import { MdTrendingUp, MdCheckCircle, MdHourglassEmpty,
         MdEngineering, MdStar, MdPeople } from 'react-icons/md'
import SLAWarnings from '../components/SLAWarnings'

ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement,
  LineElement, ArcElement, Title, Tooltip, Legend, Filler)

const CATEGORY_COLORS = [
  '#ef4444','#3b82f6','#f59e0b','#06b6d4','#22c55e','#a855f7'
]

export default function Dashboard() {
  const [data,    setData]    = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    analyticsApi.getDashboard()
      .then(r => setData(r.data.data))
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="spinner-wrap"><div className="spinner" /></div>
  if (!data)   return <div className="empty-state"><p>Failed to load analytics.</p></div>

  const { summary, category_breakdown, monthly_trend, worker_performance } = data

  const categoryChart = {
    labels: category_breakdown.map(c => c.category.replace(' Issues','').replace(' Problems','')),
    datasets: [{
      data: category_breakdown.map(c => c.count),
      backgroundColor: CATEGORY_COLORS,
      borderWidth: 0,
    }]
  }

  const monthlyChart = {
    labels: monthly_trend.map(m => m.month),
    datasets: [{
      label: 'Complaints',
      data: monthly_trend.map(m => m.count),
      fill: true,
      backgroundColor: 'rgba(26, 86, 219, 0.1)',
      borderColor: '#1a56db',
      tension: 0.4,
      pointBackgroundColor: '#1a56db',
      pointRadius: 4,
    }]
  }

  const workerChart = {
    labels: worker_performance.slice(0,6).map(w => w.worker_name),
    datasets: [
      {
        label: 'Assigned',
        data: worker_performance.slice(0,6).map(w => w.total_assigned),
        backgroundColor: '#3b82f6',
        borderRadius: 6,
      },
      {
        label: 'Resolved',
        data: worker_performance.slice(0,6).map(w => w.resolved),
        backgroundColor: '#22c55e',
        borderRadius: 6,
      }
    ]
  }

  const chartOpts = (title) => ({
    responsive: true, maintainAspectRatio: false,
    plugins: { legend: { position:'bottom', labels:{ font:{size:11}, padding:16 } },
               title: { display: false } },
    scales: title !== 'pie' ? {
      x: { grid:{ display:false }, ticks:{ font:{size:11} } },
      y: { beginAtZero:true, grid:{ color:'#f1f5f9' }, ticks:{ font:{size:11} } }
    } : undefined
  })

  return (
    <div>
      <SLAWarnings />
      {/* Stat Cards */}
      <div className="stats-grid">
        <div className="stat-card stat-total">
          <div className="stat-icon"><MdTrendingUp /></div>
          <div className="stat-info">
            <div className="stat-value">{summary.total}</div>
            <div className="stat-label">Total Complaints</div>
            <div className="stat-sub">All time registered</div>
          </div>
        </div>
        <div className="stat-card stat-pending">
          <div className="stat-icon"><MdHourglassEmpty /></div>
          <div className="stat-info">
            <div className="stat-value">{summary.submitted + summary.under_review}</div>
            <div className="stat-label">Pending Review</div>
            <div className="stat-sub">{summary.submitted} new · {summary.under_review} reviewing</div>
          </div>
        </div>
        <div className="stat-card stat-progress">
          <div className="stat-icon"><MdEngineering /></div>
          <div className="stat-info">
            <div className="stat-value">{summary.assigned + summary.in_progress}</div>
            <div className="stat-label">In Progress</div>
            <div className="stat-sub">{summary.assigned} assigned · {summary.in_progress} active</div>
          </div>
        </div>
        <div className="stat-card stat-resolved">
          <div className="stat-icon"><MdCheckCircle /></div>
          <div className="stat-info">
            <div className="stat-value">{summary.resolved}</div>
            <div className="stat-label">Resolved</div>
            <div className="stat-sub">
              {summary.total ? Math.round(summary.resolved/summary.total*100) : 0}% resolution rate
            </div>
          </div>
        </div>
        <div className="stat-card stat-rating">
          <div className="stat-icon"><MdStar /></div>
          <div className="stat-info">
            <div className="stat-value">{summary.avg_rating || '—'}</div>
            <div className="stat-label">Avg Rating</div>
            <div className="stat-sub">Villager satisfaction</div>
          </div>
        </div>
        <div className="stat-card stat-workers">
          <div className="stat-icon"><MdPeople /></div>
          <div className="stat-info">
            <div className="stat-value">{worker_performance.length}</div>
            <div className="stat-label">Active Workers</div>
            <div className="stat-sub">Avg {summary.avg_resolution_days}d resolution</div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="charts-grid">
        <div className="card">
          <div className="card-header">
            <div><h3>Monthly Complaint Trend</h3><p>Last 12 months</p></div>
          </div>
          <div className="card-body" style={{ height: 260 }}>
            <Line data={monthlyChart} options={chartOpts('line')} />
          </div>
        </div>
        <div className="card">
          <div className="card-header">
            <div><h3>By Category</h3><p>Complaint distribution</p></div>
          </div>
          <div className="card-body" style={{ height: 260 }}>
            <Pie data={categoryChart} options={chartOpts('pie')} />
          </div>
        </div>
      </div>

      {/* Worker Performance */}
      <div className="card">
        <div className="card-header">
          <div><h3>Worker Performance</h3><p>Assigned vs Resolved complaints</p></div>
        </div>
        <div className="card-body" style={{ height: 240 }}>
          <Bar data={workerChart} options={chartOpts('bar')} />
        </div>
      </div>
    </div>
  )
}
