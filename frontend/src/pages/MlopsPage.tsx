import { GitBranch, Play, Radar, TrendingUp } from "lucide-react";
import { useState } from "react";

export function MlopsPage() {
  const [started, setStarted] = useState(false);
  return (
    <section className="admin-page">
      <div className="section-head">
        <div>
          <p className="eyebrow">Admin / MLOps</p>
          <h1>Model health loop</h1>
        </div>
        <button className="primary" onClick={() => setStarted(true)}>
          <Play size={15} />{" "}
          {started ? "Retraining started" : "Trigger retraining"}
        </button>
      </div>
      <div className="admin-metrics">
        <Metric icon={<TrendingUp />} label="Prediction volume" value="--" />
        <Metric icon={<Radar />} label="Confidence drift" value="--" />
        <Metric icon={<GitBranch />} label="Feedback samples" value="--" />
      </div>
      <div className="model-health">
        <p className="eyebrow">Drift monitoring</p>
        {[
          "Crop identifier",
          "Tomato disease",
          "Potato disease",
          "Cotton disease",
        ].map((model, index) => (
          <div key={model}>
            <span>{model}</span>
            <b
              className={
                index === 3 ? "drift" : index === 2 ? "monitor" : "stable"
              }
            >
              {index === 3
                ? "Drift detected"
                : index === 2
                  ? "Monitor"
                  : "Stable"}
            </b>
          </div>
        ))}
      </div>
    </section>
  );
}
function Metric({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="admin-metric">
      <span>{icon}</span>
      <p>{label}</p>
      <strong>{value}</strong>
    </div>
  );
}
