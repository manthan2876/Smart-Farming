import { Check } from 'lucide-react'
import type { Prediction } from '../api/types'
import { confidence, imagePath, severityTone } from '../lib/format'
import { SeverityGauge } from './SeverityGauge'

export function ResultCard({ prediction }: { prediction: Prediction }) {
  const severity = prediction.severity.percent ?? 0
  return <div className="result-card"><div className="result-image"><img src={imagePath} alt="Latest crop reading" /><span className={`severity-badge ${severityTone(severity)}`}>{severity}% affected</span></div><div className="result-body"><div className="result-heading"><div><span className="eyebrow">{prediction.crop.label ?? 'Crop'} · leaf scan</span><h3>{prediction.disease.label}</h3></div><span className="confidence-ring">{confidence(prediction.disease.confidence)}</span></div><SeverityGauge value={severity} bucket={prediction.severity.bucket} /><p className="evidence"><Check size={15} /> Brown speckling and curled new growth detected</p></div></div>
}
