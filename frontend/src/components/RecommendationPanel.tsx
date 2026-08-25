import { ArrowUpRight, Droplets, ShieldCheck, Sprout } from 'lucide-react'
import type { Prediction } from '../api/types'

export function RecommendationPanel({ prediction, onOpen }: { prediction: Prediction; onOpen: () => void }) {
  return <div className="recommendation"><div className="recommendation-head"><span className="round-icon orange"><Sprout size={18} /></span><div><p className="eyebrow">Next best action</p><h3>Keep the canopy calm</h3></div></div><p>{prediction.recommendation.prevention_tips}</p><div className="recommendation-row"><span><Droplets size={15} /> Irrigation</span><b>Early morning</b></div><div className="recommendation-row"><span><ShieldCheck size={15} /> Treatment</span><b>Label-led only</b></div><button className="outline" onClick={onOpen}>Read recommendation <ArrowUpRight size={16} /></button></div>
}
