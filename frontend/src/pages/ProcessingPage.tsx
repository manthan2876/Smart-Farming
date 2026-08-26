import { Activity, Check, Circle, RotateCw } from "lucide-react";
import { useNavigate, useParams } from "react-router-dom";

const stages = [
  "Image Quality Check",
  "Leaf Processing",
  "Crop Identification",
  "Disease Analysis",
  "Severity Analysis",
  "Pest Analysis",
  "Recommendation",
];
export function ProcessingPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  return (
    <section className="processing-page">
      <div className="processing-intro">
        <span className="processing-orbit">
          <Activity size={25} />
        </span>
        <p className="eyebrow">Analysis in progress · {id ?? "new scan"}</p>
        <h1>
          Reading your
          <br />
          <em>crop story.</em>
        </h1>
        <p>
          Your image is moving through the Smart Farming AI pipeline. Each check
          helps keep the final advice grounded.
        </p>
      </div>
      <div className="pipeline-card">
        {stages.map((stage, index) => (
          <div
            className={`pipeline-stage ${index < 3 ? "done" : index === 3 ? "active" : ""}`}
            key={stage}
          >
            <span>
              {index < 3 ? (
                <Check size={14} />
              ) : index === 3 ? (
                <RotateCw className="spin" size={14} />
              ) : (
                <Circle size={10} />
              )}
            </span>
            <b>{stage}</b>
            <small>
              {index < 3 ? "complete" : index === 3 ? "working now" : "waiting"}
            </small>
          </div>
        ))}
        <button
          className="text-button processing-demo"
          onClick={() => navigate("/result/204")}
        >
          Open demo result <Activity size={15} />
        </button>
      </div>
      <div className="processing-foot">
        <span>Smart Farming AI</span>
        <span>Image → insight</span>
      </div>
    </section>
  );
}
