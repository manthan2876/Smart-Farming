import { imagePath } from "../lib/format";

export function GradCamOverlay() {
  return (
    <div className="gradcam-panel">
      <div className="gradcam-image">
        <img src={imagePath} alt="Leaf evidence preview" />
        <span className="heat-spot heat-one" />
        <span className="heat-spot heat-two" />
        <span className="gradcam-label">evidence preview</span>
      </div>
      <div>
        <p className="eyebrow">Explainable AI</p>
        <h3>Where the signal gathers</h3>
        <p>
          Live Grad-CAM output will replace this preview when the model endpoint
          exposes its heatmap.
        </p>
      </div>
    </div>
  );
}
