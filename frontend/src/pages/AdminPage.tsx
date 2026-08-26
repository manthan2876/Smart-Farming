import { AlertTriangle, BarChart3, RefreshCw, ShieldCheck } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { request } from "../api/client";
import { useAuth } from "../context/AuthContext";

export function AdminPage() {
  const { token } = useAuth();
  const metrics = useQuery({
    queryKey: ["admin-metrics"],
    queryFn: () => request("/admin/metrics", {}, token),
    enabled: Boolean(token),
    retry: false,
  });
  return (
    <section className="admin-page">
      <div className="section-head">
        <div>
          <p className="eyebrow">Operations room</p>
          <h1>Field intelligence</h1>
        </div>
        <span className="admin-badge">
          <ShieldCheck size={14} /> Admin view
        </span>
      </div>
      {metrics.isError ? (
        <div className="stage-notice">
          <AlertTriangle size={21} />
          <div>
            <b>Metrics are waiting for Stage 16.</b>
            <p>
              The dashboard is ready for accuracy, confidence, and drift data
              when the monitoring endpoint is enabled.
            </p>
          </div>
        </div>
      ) : (
        <div className="admin-metrics">
          <Metric icon={<BarChart3 />} label="Rolling accuracy" value="--" />
          <Metric icon={<RefreshCw />} label="Confidence drift" value="--" />
          <Metric icon={<AlertTriangle />} label="Open flags" value="--" />
        </div>
      )}
      <div className="empty-chart">
        <div>
          <p className="eyebrow">Accuracy over time</p>
          <h3>Monitoring will appear here</h3>
          <p>
            Feedback from farmers will power this view once `/admin/metrics` is
            implemented.
          </p>
        </div>
        <div className="chart-line" />
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
