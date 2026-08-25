import { useState } from 'react'
import { Check, MapPin, Sprout, Volume2 } from 'lucide-react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { profile, updateProfile } from '../api/auth'
import { useAuth } from '../context/AuthContext'

export function ProfilePage() {
  const { token } = useAuth(); const client = useQueryClient(); const query = useQuery({ queryKey: ['profile', token], queryFn: () => profile(token!), enabled: Boolean(token) }); const [language, setLanguage] = useState('English')
  const mutation = useMutation({ mutationFn: () => updateProfile({ language }, token!), onSuccess: data => client.setQueryData(['profile', token], data) })
  const farmer = query.data
  return <section className="profile-page"><div className="profile-hero"><div className="avatar profile-avatar">{farmer?.name?.slice(0, 2).toUpperCase() ?? 'MP'}</div><div><p className="eyebrow">Farmer profile</p><h1>{farmer?.name ?? 'Your farm profile'}</h1><p>{farmer?.email ?? 'Connect an account to load your profile.'}</p></div></div><div className="profile-grid"><div className="profile-panel"><div className="panel-heading"><MapPin size={18} /><div><p className="eyebrow">Home ground</p><h3>Farm details</h3></div></div><div className="profile-detail"><span>Location</span><b>{farmer?.location ?? 'Not set'}</b></div><div className="profile-detail"><span>Preferred advice</span><select value={language === 'English' && farmer?.language ? farmer.language : language} onChange={e => setLanguage(e.target.value)}><option>English</option><option>Hindi</option><option>Gujarati</option></select></div><button className="primary" onClick={() => mutation.mutate()} disabled={mutation.isPending}>Save preferences {mutation.isSuccess ? <Check size={16} /> : null}</button></div><div className="profile-panel crop-panel"><div className="panel-heading"><Sprout size={18} /><div><p className="eyebrow">In rotation</p><h3>Your crops</h3></div></div><div className="crop-chips">{(farmer?.crop_history?.length ? farmer.crop_history : ['Tomato', 'Cotton']).map(crop => <span key={crop}>{crop}</span>)}</div><div className="voice-note"><Volume2 size={17} /><span>Recommendations can be read aloud in the mobile app.</span></div></div></div></section>
}
