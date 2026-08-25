import { Activity, Bell, Camera, ChevronDown, Leaf, LogOut, Settings, ShieldCheck, Sprout, UserRound, BarChart3, Tractor } from 'lucide-react'

type Page = 'overview' | 'scan' | 'history' | 'farm' | 'alerts' | 'profile' | 'settings' | 'admin' | 'expert'
type Props = { active: Page; onNavigate: (page: Page) => void }

export function Sidebar({ active, onNavigate }: Props) {
  return <aside className="sidebar">
    <div className="brand"><span className="brand-mark"><Leaf size={18} /></span><span>fieldnote<small>smart farming</small></span></div>
    <div className="season-tag"><span className="pulse-dot" /> Kharif season <b>•</b> 2026</div>
    <nav>
      <button className={active === 'overview' ? 'nav-active' : ''} onClick={() => onNavigate('overview')}><Activity size={18} /> Field pulse</button>
      <button className={active === 'scan' ? 'nav-active' : ''} onClick={() => onNavigate('scan')}><Camera size={18} /> New scan <span className="nav-key">N</span></button>
      <button className={active === 'history' ? 'nav-active' : ''} onClick={() => onNavigate('history')}><Sprout size={18} /> Scan history</button>
      <button className={active === 'farm' ? 'nav-active' : ''} onClick={() => onNavigate('farm')}><Tractor size={18} /> My farm</button>
      <button className={active === 'alerts' ? 'nav-active' : ''} onClick={() => onNavigate('alerts')}><Bell size={18} /> Alerts</button>
      <button className={active === 'profile' ? 'nav-active' : ''} onClick={() => onNavigate('profile')}><UserRound size={18} /> Farm profile</button>
      <button className={active === 'settings' ? 'nav-active' : ''} onClick={() => onNavigate('settings')}><Settings size={18} /> Settings</button>
      <button className={active === 'expert' ? 'nav-active' : ''} onClick={() => onNavigate('expert')}><ShieldCheck size={18} /> Expert queue</button>
      <button className={active === 'admin' ? 'nav-active' : ''} onClick={() => onNavigate('admin')}><BarChart3 size={18} /> Admin metrics</button>
    </nav>
    <div className="sidebar-note"><ShieldCheck size={20} /><p>Your crop data stays linked to your farm profile.</p></div>
    <div className="profile-mini"><div className="avatar">MP</div><div><strong>Manthan Patel</strong><span>North plot · Gujarat</span></div><ChevronDown size={15} /></div>
  </aside>
}
