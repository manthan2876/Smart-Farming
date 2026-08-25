export type Prediction = {
  prediction_id?: number
  request_id: string
  image: { raw_path?: string; processed_path?: string; quality_score?: number; leaf_detected?: boolean }
  crop: { label?: string; confidence?: number }
  disease: { label?: string; confidence?: number; model_used?: string }
  severity: { percent?: number; bucket?: string }
  weather: { temperature_celsius?: number; humidity_percent?: number; condition?: string; status?: string }
  recommendation: { fertilizer?: string; pesticide?: string; irrigation?: string; prevention_tips?: string }
  status: Record<string, string>
  notes: string[]
}

export type Profile = { id: string; name?: string; email?: string; phone?: string; language: string; location?: string; crop_history: string[] }

export const demoPrediction: Prediction = {
  prediction_id: 204, request_id: 'fieldnote-demo', image: { raw_path: 'aphids_tomato.jpeg', quality_score: 82, leaf_detected: true }, crop: { label: 'Tomato', confidence: .94 }, disease: { label: 'Aphids', confidence: .88, model_used: 'tomato_disease_v1' }, severity: { percent: 37, bucket: 'moderate' }, weather: { temperature_celsius: 27, humidity_percent: 68, condition: 'Clear', status: 'success' }, recommendation: { fertilizer: 'Pause nitrogen for 7 days; keep potassium steady.', pesticide: 'Use a registered aphid treatment according to its label.', irrigation: 'Water at the soil line in the early morning.', prevention_tips: 'Inspect new growth every 48 hours and remove heavily affected leaves.' }, status: { preprocessing: 'completed', disease_classification: 'completed', recommendation: 'completed' }, notes: [],
}
