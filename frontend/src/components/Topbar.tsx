import { Menu, Search } from 'lucide-react'

type Page = 'overview' | 'scan' | 'history' | 'farm' | 'alerts' | 'profile' | 'settings' | 'admin' | 'expert'
export function Topbar({ active }: { active: Page }) {
  const label = active === 'scan' ? 'New scan' : active === 'history' ? 'Scan history' : active === 'farm' ? 'My farm' : active === 'alerts' ? 'Alerts' : active === 'profile' ? 'Farm profile' : active === 'settings' ? 'Settings' : active === 'expert' ? 'Expert queue' : active === 'admin' ? 'Admin metrics' : 'Field pulse'
  return <header className="topbar"><button className="mobile-menu"><Menu size={20} /></button><div className="crumb">Tuesday, 25 August 2026 <span>/</span> <b>{label}</b></div><div className="top-actions"><button className="icon-button" title="Search"><Search size={18} /></button><span className="online"><span className="pulse-dot" /> API ready</span></div></header>
}
