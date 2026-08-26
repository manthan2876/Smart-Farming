import {
  ArrowLeft,
  ArrowUpRight,
  Bug,
  Check,
  CloudSun,
  MessageSquare,
} from "lucide-react";
import type { Prediction } from "../api/types";
import { ResultCard } from "../components/ResultCard";
import { RecommendationPanel } from "../components/RecommendationPanel";
import { GradCamOverlay } from "../components/GradCamOverlay";
import { FeedbackPanel } from "../components/FeedbackPanel";
import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { getPrediction } from "../api/predictions";
import { useAuth } from "../context/AuthContext";

export function ResultPage({
  prediction,
  onBack,
}: {
  prediction: Prediction;
  onBack: () => void;
}) {
  const navigate = useNavigate();
  const { token } = useAuth();
  const { data: stored } = useQuery({
    queryKey: ["prediction", prediction.prediction_id, token],
    queryFn: () => getPrediction(String(prediction.prediction_id), token!),
    enabled: Boolean(token && prediction.prediction_id),
  });
  prediction = stored ?? prediction;
  const lowConfidence = prediction.status?.review === "pending_expert_review";
  return (
    <section className="result-page">
      <button className="back-link" onClick={onBack}>
        <ArrowLeft size={16} /> Back to history
      </button>
      <div className="section-head">
        <div>
          <p className="eyebrow">
            Scan #{prediction.prediction_id} · crop diagnosis
          </p>
          <h1>
            {lowConfidence ? "Diagnosis needs review" : "What Fieldnote saw"}
          </h1>
        </div>
        <span className={`result-status ${lowConfidence ? "review" : ""}`}>
          <span />{" "}
          {lowConfidence ? "expert review pending" : "analysis complete"}
        </span>
      </div>
      {lowConfidence ? (
        <div className="review-warning">
          <MessageSquare size={21} />
          <div>
            <h3>We are protecting your crop from uncertain advice.</h3>
            <p>
              The AI confidence is{" "}
              {Math.round((prediction.disease.confidence ?? 0) * 100)}%, so
              treatment advice is hidden until an agricultural expert reviews
              this case.
            </p>
            <button className="outline" onClick={() => navigate("/expert")}>
              Request expert review <ArrowUpRight size={15} />
            </button>
          </div>
        </div>
      ) : (
        <>
          <div className="result-detail-grid">
            <ResultCard prediction={prediction} />
            <RecommendationPanel
              prediction={prediction}
              onOpen={() => undefined}
            />
          </div>
          <GradCamOverlay />
          <div className="context-strip">
            <span>
              <CloudSun size={17} />{" "}
              {prediction.weather.temperature_celsius ?? "—"}°C ·{" "}
              {prediction.weather.humidity_percent ?? "—"}% humidity
            </span>
            <span>
              <Bug size={17} />{" "}
              {prediction.pests?.length
                ? `${prediction.pests.length} pest signal(s)`
                : "No pest detected"}
            </span>
            <span>
              <Check size={17} /> Crop: {prediction.crop.label ?? "Unknown"}
            </span>
          </div>
          <div className="evidence-panel">
            <div>
              <p className="eyebrow">Evidence trail</p>
              <h3>Signals behind the reading</h3>
            </div>
            <ul>
              <li>Evidence is shown only when supplied by the AI service.</li>
              <li>
                Leaf quality and crop signals passed the configured checks.
              </li>
            </ul>
            <button
              className="outline"
              onClick={() =>
                document
                  .querySelector(".feedback-panel")
                  ?.scrollIntoView({ behavior: "smooth" })
              }
            >
              <MessageSquare size={15} /> Give feedback{" "}
              <ArrowUpRight size={15} />
            </button>
          </div>
          <FeedbackPanel predictionId={prediction.prediction_id} />
        </>
      )}
    </section>
  );
}
