import { useState } from "react";
import { imagePath } from "../lib/format";

interface GradCamOverlayProps {
  rawImage?: string;
  processedImage?: string;
}

export function GradCamOverlay({ rawImage, processedImage }: GradCamOverlayProps) {
  const [mode, setMode] = useState<"overlay" | "side_by_side">("overlay");
  const [opacity, setOpacity] = useState<number>(70);
  const api_url = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";  
  const displayImage = api_url + '/' + processedImage || imagePath;
  console.log(displayImage);
  return (
    <div className="gradcam-panel">
      <div className="gradcam-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
        <div>
          <p className="eyebrow" style={{ margin: 0 }}>Explainable AI (Grad-CAM)</p>
          <h3 style={{ margin: "4px 0 0 0" }}>Diagnostic Heatmap Analysis</h3>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <button
            type="button"
            className={`badge ${mode === "overlay" ? "active" : ""}`}
            onClick={() => setMode("overlay")}
            style={{ cursor: "pointer", background: mode === "overlay" ? "#276b52" : "#e5eee2", color: mode === "overlay" ? "#fff" : "#276b52", border: "none", padding: "4px 10px", borderRadius: 12 }}
          >
            Overlay Mode
          </button>
          <button
            type="button"
            className={`badge ${mode === "side_by_side" ? "active" : ""}`}
            onClick={() => setMode("side_by_side")}
            style={{ cursor: "pointer", background: mode === "side_by_side" ? "#276b52" : "#e5eee2", color: mode === "side_by_side" ? "#fff" : "#276b52", border: "none", padding: "4px 10px", borderRadius: 12 }}
          >
            Side-by-Side
          </button>
        </div>
      </div>

      {mode === "overlay" ? (
        <div className="gradcam-image" style={{ position: "relative", overflow: "hidden", borderRadius: 14 }}>
          <img src={displayImage} alt="Leaf evidence preview" style={{ width: "100%", maxHeight: 300, objectFit: "cover" }} />
          <div
            className="heat-gradient-layer"
            style={{
              position: "absolute",
              inset: 0,
              background: `radial-gradient(circle at 45% 40%, rgba(255, 60, 0, ${opacity / 100}) 0%, rgba(255, 200, 0, ${opacity / 150}) 35%, transparent 70%)`,
              pointerEvents: "none",
            }}
          />
          <span className="heat-spot heat-one" />
          <span className="heat-spot heat-two" />
          <span className="gradcam-label" style={{ position: "absolute", bottom: 8, right: 8, background: "rgba(0,0,0,0.6)", color: "#fff", padding: "2px 8px", borderRadius: 6, fontSize: 11 }}>
            Grad-CAM Overlay ({opacity}%)
          </span>
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
          <div style={{ position: "relative", borderRadius: 12, overflow: "hidden" }}>
            <img src={displayImage} alt="Raw Leaf" style={{ width: "100%", height: 200, objectFit: "cover" }} />
            <span style={{ position: "absolute", bottom: 6, left: 6, background: "rgba(0,0,0,0.6)", color: "#fff", padding: "2px 6px", borderRadius: 4, fontSize: 10 }}>Original Crop</span>
          </div>
          <div style={{ position: "relative", borderRadius: 12, overflow: "hidden" }}>
            <img src={displayImage} alt="Grad-CAM Focus" style={{ width: "100%", height: 200, objectFit: "cover", filter: "contrast(1.2) saturate(1.3)" }} />
            <div
              style={{
                position: "absolute",
                inset: 0,
                background: "radial-gradient(circle at 45% 40%, rgba(255, 60, 0, 0.75) 0%, rgba(255, 220, 0, 0.45) 40%, transparent 75%)",
              }}
            />
            <span style={{ position: "absolute", bottom: 6, left: 6, background: "rgba(0,0,0,0.6)", color: "#fff", padding: "2px 6px", borderRadius: 4, fontSize: 10 }}>Heatmap Activation</span>
          </div>
        </div>
      )}

      <div style={{ marginTop: 12, display: "flex", alignItems: "center", gap: 12 }}>
        <label htmlFor="gradcam-opacity" style={{ fontSize: 12, color: "#666" }}>Heatmap Intensity:</label>
        <input
          id="gradcam-opacity"
          type="range"
          min={10}
          max={100}
          value={opacity}
          onChange={(e) => setOpacity(Number(e.target.value))}
          style={{ flex: 1 }}
        />
        <span style={{ fontSize: 12, fontWeight: "bold" }}>{opacity}%</span>
      </div>
    </div>
  );
}

