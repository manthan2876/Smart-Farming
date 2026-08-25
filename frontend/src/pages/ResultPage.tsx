import { ArrowLeft, ArrowUpRight, MessageSquare } from 'lucide-react'
import type { Prediction } from '../api/types'
import { ResultCard } from '../components/ResultCard'
import { RecommendationPanel } from '../components/RecommendationPanel'
import { GradCamOverlay } from '../components/GradCamOverlay'

export function ResultPage({ prediction, onBack }: { prediction: Prediction; onBack: () => void }) {
  return <section className="result-page"><button className="back-link" onClick={onBack}><ArrowLeft size={16} /> Back to history</button><div className="section-head"><div><p className="eyebrow">Scan #{prediction.prediction_id} · explainable reading</p><h1>What Fieldnote saw</h1></div><span className="result-status"><span /> complete</span></div><div className="result-detail-grid"><ResultCard prediction={prediction} /><RecommendationPanel prediction={prediction} onOpen={() => undefined} /></div><GradCamOverlay /><div className="evidence-panel"><div><p className="eyebrow">Evidence trail</p><h3>Signals behind the reading</h3></div><ul><li>Brown lesions detected on leaf surface</li><li>Leaf discoloration pattern matches {prediction.disease.label}</li><li>Confidence threshold passed at {Math.round((prediction.disease.confidence ?? 0) * 100)}%</li></ul><button className="outline"><MessageSquare size={15} /> Give feedback <ArrowUpRight size={15} /></button></div></section>
}
