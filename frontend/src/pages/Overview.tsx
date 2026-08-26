import { ArrowUpRight, Camera, Droplets } from "lucide-react";
import type { Prediction } from "../api/types";
import { confidence, imagePath, severityTone } from "../lib/format";
import { RecommendationPanel } from "../components/RecommendationPanel";
import { ResultCard } from "../components/ResultCard";

type Props = {
  prediction: Prediction;
  history: Prediction[];
  onScan: () => void;
  onSelect: (item: Prediction) => void;
  onHistory: () => void;
};

export function Overview({
  prediction,
  history,
  onScan,
  onSelect,
  onHistory,
}: Props) {
  return (
    <>
      <section className="hero-grid">
        <div className="scan-cta">
          <div className="cta-copy">
            <span className="round-icon">
              <Camera size={18} />
            </span>
            <p className="eyebrow">Field check</p>
            <h2>What is your leaf saying today?</h2>
            <p>
              Capture a close-up. Fieldnote checks the crop, disease signals,
              severity, pests, and local weather together.
            </p>
            <button className="primary" onClick={onScan}>
              Start a scan <ArrowUpRight size={17} />
            </button>
          </div>
          <div className="leaf-art">
            <img src={imagePath} alt="Tomato leaf sample" />
            <span className="scan-ring" />
          </div>
        </div>
        <div className="metric-stack">
          <div className="metric-card">
            <div className="metric-top">
              <span>Last reading</span>
              <ArrowUpRight size={16} />
            </div>
            <strong>{prediction.disease.label ?? "Awaiting scan"}</strong>
            <div className="metric-foot">
              <span className="status-pill">
                {confidence(prediction.disease.confidence)} confidence
              </span>
              <span>scan #{prediction.prediction_id}</span>
            </div>
          </div>
          <div className="metric-card dark-card">
            <Droplets size={18} />
            <span>Soil watch</span>
            <strong>Good moisture</strong>
            <p>Water at the soil line tomorrow morning.</p>
          </div>
        </div>
      </section>
      <section className="section-head">
        <div>
          <p className="eyebrow">Latest intelligence</p>
          <h2>Crop health, in one glance</h2>
        </div>
        <button className="text-button" onClick={() => onSelect(prediction)}>
          Open full reading <ArrowUpRight size={16} />
        </button>
      </section>
      <section className="insight-grid">
        <ResultCard prediction={prediction} />
        <RecommendationPanel
          prediction={prediction}
          onOpen={() => onSelect(prediction)}
        />
      </section>
      <section className="section-head compact">
        <div>
          <p className="eyebrow">Recent scans</p>
          <h2>Your field’s trail</h2>
        </div>
        <button className="text-button" onClick={onHistory}>
          View all <ArrowUpRight size={16} />
        </button>
      </section>
      <div className="scan-list">
        {history.slice(0, 3).map((item) => (
          <button
            className="scan-row"
            key={item.prediction_id}
            onClick={() => onSelect(item)}
          >
            <img src={imagePath} alt="" />
            <span>
              <b>{item.disease.label}</b>
              <small>
                {item.crop.label} · scan #{item.prediction_id}
              </small>
            </span>
            <strong>{confidence(item.disease.confidence)}</strong>
            <span
              className={`mini-severity ${severityTone(item.severity.percent)}`}
            >
              {item.severity.percent}%
            </span>
            <ArrowUpRight size={16} />
          </button>
        ))}
      </div>
    </>
  );
}
