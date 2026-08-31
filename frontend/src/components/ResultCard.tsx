import { Check } from "lucide-react";
import type { Prediction } from "../api/types";
import { confidence, severityTone } from "../lib/format";
import { SeverityGauge } from "./SeverityGauge";

export function ResultCard({ prediction }: { prediction: Prediction }) {
  const api_url = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";  
  const rawPath = prediction.image.processed_path || "";
  const cleanPath = rawPath.replace(/^\/+/, "").replace(/^data\//, "");
  const imageSrc = `${api_url}/data/${cleanPath}`;
  const severity = prediction.severity.percent ?? 0;
  return (
    <div className="result-card">
      <div className="result-image">
        <img src={imageSrc} alt="Latest Prediction Image" />
        <span className={`severity-badge ${severityTone(severity)}`}>
          {severity}% affected
        </span>
      </div>
      <div className="result-body">
        <div className="result-heading">
          <div>
            <span className="eyebrow">
              {prediction.crop.label ?? "Crop"} · leaf scan
            </span>
            <h3>{prediction.disease.label}</h3>
          </div>
          <span className="confidence-ring">
            {confidence(prediction.disease.confidence)}
          </span>
        </div>
        <SeverityGauge value={severity} bucket={prediction.severity.bucket} />
        <p className="evidence">
          <Check size={15} /> Brown speckling and curled new growth detected
        </p>
      </div>
    </div>
  );
}
