import {
  ArrowUpRight,
  Droplets,
  FlaskConical,
  ShieldCheck,
  Sprout,
  Zap,
} from "lucide-react";
import type { Prediction } from "../api/types";

export function RecommendationPanel({
  prediction,
  onOpen,
}: {
  prediction: Prediction;
  onOpen: () => void;
}) {
  const advice = prediction.recommendation;
  return (
    <div className="recommendation recommendation-stack">
      <div className="recommendation-head">
        <span className="round-icon orange">
          <Sprout size={18} />
        </span>
        <div>
          <p className="eyebrow">Recommended actions</p>
          <h3>Protect the crop early</h3>
        </div>
      </div>
      <div className="action-card immediate">
        <Zap size={16} />
        <div>
          <b>Immediate action</b>
          <p>
            {advice.prevention_tips ??
              "Inspect nearby plants and remove heavily affected leaves."}
          </p>
        </div>
      </div>
      <div className="action-card">
        <Sprout size={16} />
        <div>
          <b>Fertilizer</b>
          <p>
            {advice.fertilizer ?? "Follow soil-test guidance for your crop."}
          </p>
        </div>
      </div>
      <div className="action-card">
        <FlaskConical size={16} />
        <div>
          <b>Disease treatment</b>
          <p>
            {advice.pesticide ??
              "Use a registered treatment and follow the product label."}
          </p>
        </div>
      </div>
      <div className="action-card">
        <Droplets size={16} />
        <div>
          <b>Irrigation</b>
          <p>
            {advice.irrigation ??
              "Water at the soil line and avoid wetting leaves."}
          </p>
        </div>
      </div>
      <div className="safety-note">
        <ShieldCheck size={15} /> Follow locally approved product labels and
        agricultural guidance.
      </div>
      <button className="outline" onClick={onOpen}>
        Read full recommendation <ArrowUpRight size={16} />
      </button>
    </div>
  );
}
