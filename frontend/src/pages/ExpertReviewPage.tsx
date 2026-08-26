import { ArrowLeft, Check, Save } from "lucide-react";
import { useNavigate, useParams } from "react-router-dom";

export function ExpertReviewPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  return (
    <section className="expert-review-page">
      <button className="back-link" onClick={() => navigate("/expert")}>
        <ArrowLeft size={16} /> Back to queue
      </button>
      <div className="section-head">
        <div>
          <p className="eyebrow">Expert case · {id}</p>
          <h1>Review diagnosis</h1>
        </div>
        <span className="review-status">Pending review</span>
      </div>
      <div className="expert-review-grid">
        <div className="review-image">
          <img src="/aphids_tomato.jpeg" alt="Uploaded tomato leaf" />
          <span>Original image</span>
        </div>
        <div className="review-form">
          <p className="eyebrow">AI suggestion</p>
          <h2>Tomato · Aphids</h2>
          <p className="review-muted">Confidence: 58% · Severity: 32%</p>
          <label>
            Expert diagnosis
            <select>
              <option>Aphids</option>
              <option>Early blight</option>
              <option>Healthy</option>
            </select>
          </label>
          <label>
            Expert severity
            <input type="number" defaultValue="32" min="0" max="100" />
          </label>
          <label>
            Expert notes
            <textarea placeholder="Add context for the farmer…" />
          </label>
          <div className="review-actions">
            <button className="outline" onClick={() => navigate("/expert")}>
              <Save size={15} /> Save review
            </button>
            <button className="primary" onClick={() => navigate("/expert")}>
              <Check size={15} /> Approve diagnosis
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
