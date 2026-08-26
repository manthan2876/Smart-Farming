import { ArrowUpRight, ChevronDown, Filter } from "lucide-react";
import { useState } from "react";
import type { Prediction } from "../api/types";
import { confidence, imagePath, severityTone } from "../lib/format";

export function HistoryPage({
  history,
  onSelect,
}: {
  history: Prediction[];
  onSelect: (item: Prediction) => void;
}) {
  const [crop, setCrop] = useState("All crops");
  const [disease, setDisease] = useState("All conditions");
  const crops = [
    ...new Set(history.map((item) => item.crop.label).filter(Boolean)),
  ] as string[];
  const diseases = [
    ...new Set(history.map((item) => item.disease.label).filter(Boolean)),
  ] as string[];
  const filtered = history.filter(
    (item) =>
      (crop === "All crops" || item.crop.label === crop) &&
      (disease === "All conditions" || item.disease.label === disease),
  );
  return (
    <section className="history-page">
      <div className="section-head">
        <div>
          <p className="eyebrow">Field archive</p>
          <h1>Scan history</h1>
        </div>
        <div className="filters">
          <Filter size={15} />
          <select value={crop} onChange={(e) => setCrop(e.target.value)}>
            <option>All crops</option>
            {crops.map((item) => (
              <option key={item}>{item}</option>
            ))}
          </select>
          <select value={disease} onChange={(e) => setDisease(e.target.value)}>
            <option>All conditions</option>
            {diseases.map((item) => (
              <option key={item}>{item}</option>
            ))}
          </select>
          <ChevronDown size={15} />
        </div>
      </div>
      <div className="history-table">
        <div className="table-head">
          <span>Reading</span>
          <span>Crop</span>
          <span>Confidence</span>
          <span>Severity</span>
          <span>Date</span>
          <span />
        </div>
        {filtered.map((item) => (
          <button
            className="table-row"
            key={item.prediction_id}
            onClick={() => onSelect(item)}
          >
            <span className="reading-cell">
              <img src={imagePath} alt="" />
              <b>{item.disease.label}</b>
            </span>
            <span>{item.crop.label}</span>
            <span>{confidence(item.disease.confidence)}</span>
            <span>
              <i className={`dot ${severityTone(item.severity.percent)}`} />
              {item.severity.percent}%
            </span>
            <span>25 Aug 2026</span>
            <ArrowUpRight size={16} />
          </button>
        ))}
      </div>
    </section>
  );
}
