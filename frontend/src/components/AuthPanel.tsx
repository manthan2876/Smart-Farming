import { FormEvent, useState } from 'react'
import { ArrowUpRight, KeyRound, X } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

export function AuthPanel({ onClose, onLoggedIn }: { onClose: () => void; onLoggedIn: () => void }) {
  const { signIn } = useAuth()
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  async function submit(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError('')
    try { await signIn(identifier, password); onLoggedIn(); onClose() }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Could not connect to the farm account.') }
    finally { setBusy(false) }
  }
  return <div className="auth-backdrop" role="dialog" aria-modal="true"><form className="auth-panel" onSubmit={submit}><button className="auth-close" type="button" onClick={onClose}><X size={17} /></button><span className="round-icon"><KeyRound size={18} /></span><p className="eyebrow">Farmer access</p><h2>Return to your field.</h2><p className="auth-copy">Sign in to sync live scans, history, and recommendations.</p><label>Phone or email<input required value={identifier} onChange={event => setIdentifier(event.target.value)} placeholder="you@example.com" /></label><label>Password<input required type="password" value={password} onChange={event => setPassword(event.target.value)} placeholder="Your password" /></label>{error && <p className="auth-error">{error}</p>}<button className="primary auth-submit" disabled={busy}>{busy ? 'Connecting…' : <>Connect account <ArrowUpRight size={16} /></>}</button></form></div>
}
