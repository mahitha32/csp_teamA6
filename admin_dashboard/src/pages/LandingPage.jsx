import { Link } from 'react-router-dom'
import { MdPublic, MdSecurity, MdTrendingUp, MdPeople } from 'react-icons/md'

export default function LandingPage() {
  return (
    <div style={{ fontFamily: 'Inter, sans-serif', background: '#f8fafc', minHeight: '100vh' }}>
      {/* Navbar */}
      <nav style={{ padding: '20px 40px', background: '#fff', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #e2e8f0' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ background: 'var(--primary)', color: '#fff', padding: 8, borderRadius: 8 }}><MdPublic size={24} /></div>
          <h1 style={{ fontSize: 20, fontWeight: 800, color: '#0f172a' }}>Vemavaram Smart Village</h1>
        </div>
        <div>
          <Link to="/login" style={{ background: 'var(--primary)', color: '#fff', padding: '10px 20px', borderRadius: 6, fontWeight: 600, textDecoration: 'none' }}>Admin Login</Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section style={{ textAlign: 'center', padding: '100px 20px', background: 'linear-gradient(135deg, #0e2a5c 0%, #1a56db 100%)', color: '#fff' }}>
        <h2 style={{ fontSize: 48, fontWeight: 800, marginBottom: 16 }}>Transforming Vemavaram Village</h2>
        <p style={{ fontSize: 20, maxWidth: 600, margin: '0 auto', color: '#bfdbfe', marginBottom: 32 }}>A digital governance platform designed to bring transparency, efficiency, and rapid problem resolution to our community.</p>
        <Link to="/login" style={{ background: '#f59e0b', color: '#fff', padding: '14px 28px', borderRadius: 8, fontWeight: 700, textDecoration: 'none', fontSize: 18, display: 'inline-block' }}>Explore Dashboard</Link>
      </section>

      {/* Features */}
      <section style={{ padding: '80px 40px', maxWidth: 1200, margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: 60 }}>
          <h2 style={{ fontSize: 32, fontWeight: 800, color: '#0f172a' }}>Key Features</h2>
          <p style={{ color: '#64748b', fontSize: 16 }}>Built for Community Service Projects (CSP) & real-world deployment.</p>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 30 }}>
          <FeatureCard icon={<MdSecurity />} title="Secure Reporting" desc="Villagers can securely report issues with exact geo-locations and photo evidence via the mobile app." />
          <FeatureCard icon={<MdTrendingUp />} title="Data-Driven Insights" desc="Admins get access to a powerful analytics dashboard to track performance and complaint trends." />
          <FeatureCard icon={<MdPeople />} title="Worker Accountability" desc="Dedicated worker accounts ensure every complaint is tracked, assigned, and resolved efficiently." />
        </div>
      </section>

      {/* Footer */}
      <footer style={{ padding: '40px', textAlign: 'center', background: '#0f172a', color: '#64748b' }}>
        <p>Â© 2026 Vemavaram Village Community Service Project. All rights reserved.</p>
      </footer>
    </div>
  )
}

function FeatureCard({ icon, title, desc }) {
  return (
    <div style={{ background: '#fff', padding: 30, borderRadius: 12, border: '1px solid #e2e8f0', boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }}>
      <div style={{ fontSize: 40, color: 'var(--primary)', marginBottom: 16 }}>{icon}</div>
      <h3 style={{ fontSize: 20, fontWeight: 700, marginBottom: 12, color: '#0f172a' }}>{title}</h3>
      <p style={{ color: '#475569', lineHeight: 1.6 }}>{desc}</p>
    </div>
  )
}

