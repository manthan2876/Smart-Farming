import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { request } from "../api/client";
import { exportDataset } from "../api/admin";
import { useAuth } from "../context/AuthContext";
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell
} from "recharts";
import { Loader2, Download } from "lucide-react";
import { Card, Button } from "../components/ui";

const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6'];
const CROP_OPTIONS = ["All Crops", "Tomato", "Cotton", "Groundnut", "Pepper Bell", "Potato"];
const STATUS_OPTIONS = ["Any", "pending_review", "added_to_dataset", "rejected"];

export default function AdminMetricsPage() {
  const { token } = useAuth();

  // Export filter state
  const [exportCrop, setExportCrop] = useState("All Crops");
  const [exportStatus, setExportStatus] = useState("Any");
  const [exportImageTarget, setExportImageTarget] = useState<"preprocessed" | "raw">("preprocessed");
  const [exportFormat, setExportFormat] = useState<"PyTorch Folder" | "JSON Manifest">("PyTorch Folder");
  const [exportTrain, setExportTrain] = useState(70);
  const [exportVal, setExportVal] = useState(15);
  const [exportTest, setExportTest] = useState(15);
  const [exporting, setExporting] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ["admin_metrics"],
    queryFn: () => request<any>("/admin/metrics", {}, token!),
    enabled: !!token
  });

  const { data: datasetSummary } = useQuery({
    queryKey: ["dataset_summary"],
    queryFn: () => request<any>("/admin/dataset/summary", {}, token!),
    enabled: !!token,
  });

  const { data: modelHealth } = useQuery({
    queryKey: ["model_health"],
    queryFn: () => request<any>("/admin/models/health", {}, token!),
    enabled: !!token,
    staleTime: 60_000,
  });

  const handleExportMLOps = async () => {
    if (exportTrain + exportVal + exportTest !== 100) {
      alert("Split percentages must total 100");
      return;
    }
    setExporting(true);
    try {
      const blob = await exportDataset(token!, {
        filters: {
          expert: true,
          farmer: true,
          crop: exportCrop === "All Crops" ? undefined : exportCrop,
          status: exportStatus === "Any" ? undefined : exportStatus,
        },
        split: { train: exportTrain, val: exportVal, test: exportTest },
        format: exportFormat,
        imageTarget: exportImageTarget,
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "dataset_export.zip";
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (e) {
      console.error(e);
      alert("Export failed. No candidates may match the selected filters.");
    } finally {
      setExporting(false);
    }
  };

  if (isLoading) return <div className="flex min-h-[40vh] items-center justify-center"><Loader2 className="animate-spin text-admin-500" /></div>;
  if (!data) return <div className="rounded-md border border-red-100 bg-red-50 p-6 text-danger">Failed to load metrics.</div>;

  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="font-display text-3xl text-ink sm:text-4xl">System Metrics & ML Ops</h1>
          <p className="mt-2 text-sm text-muted">Operational health and model validation signals.</p>
        </div>
      </div>

      {/* ── Key metrics row 1 ── */}
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <h3 className="text-xs font-bold uppercase tracking-wide text-muted">Total Users</h3>
          <div className="mt-3 font-display text-3xl text-ink">{data.total_users}</div>
        </Card>
        <Card>
          <h3 className="text-xs font-bold uppercase tracking-wide text-muted">Total Scans</h3>
          <div className="mt-3 font-display text-3xl text-ink">{data.total_scans}</div>
          <p className="mt-1 text-xs text-muted">{data.completed_scans || 0} completed</p>
        </Card>
        <Card>
          <h3 className="text-xs font-bold uppercase tracking-wide text-muted">Active Queue Depth</h3>
          <div className={`mt-3 font-display text-3xl ${(data.queue_depth || 0) > 5 ? "text-amber-600" : "text-ink"}`}>{data.queue_depth || 0}</div>
          <p className="mt-1 text-xs text-muted">Predictions currently processing</p>
        </Card>
        <Card>
          <h3 className="text-xs font-bold uppercase tracking-wide text-muted">Pipeline Latency</h3>
          <div className="mt-3 font-display text-3xl text-ink">{data.processing_duration?.avg_ms || 0}<span className="text-sm font-normal text-muted"> ms avg</span></div>
          <p className="mt-1 text-xs text-muted">P95: {data.processing_duration?.p95_ms || 0} ms</p>
        </Card>
      </div>

      {/* ── Key metrics row 2 ── */}
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <h3 className="text-xs font-bold uppercase tracking-wide text-muted">Farmer Field Accuracy</h3>
          <div className={`mt-3 font-display text-3xl ${data.accuracy > 85 ? "text-farmer-700" : "text-danger"}`}>
            {typeof data.accuracy === "number" ? data.accuracy.toFixed(1) : data.accuracy}%
          </div>
          <p className="mt-1 text-xs text-muted">Farmer field validation signals</p>
        </Card>
        <Card>
          <h3 className="text-xs font-bold uppercase tracking-wide text-muted">Specialist Validated Accuracy</h3>
          <div className="mt-3 font-display text-3xl text-expert-700">
            {data.expert_metrics?.validated_accuracy != null ? `${data.expert_metrics.validated_accuracy}%` : "Pending Data"}
          </div>
          <p className="mt-1 text-xs text-muted">{data.expert_metrics?.overrides || 0} agronomist overrides</p>
        </Card>
        <Card>
          <h3 className="text-xs font-bold uppercase tracking-wide text-muted">Pipeline Failure Rate</h3>
          <div className={`mt-3 font-display text-3xl ${(data.failures?.failure_rate || 0) > 5 ? "text-danger" : "text-farmer-700"}`}>
            {data.failures?.failure_rate !== undefined ? `${data.failures.failure_rate.toFixed(1)}%` : "0.0%"}
          </div>
          <p className="mt-1 text-xs text-muted">{data.failures?.total_failed || 0} failed scans</p>
        </Card>
        <Card>
          <h3 className="text-xs font-bold uppercase tracking-wide text-muted">Degraded / Fallback Signals</h3>
          <div className="mt-3 font-display text-3xl text-amber-600">
            {(data.fallbacks?.recommendation_fallbacks || 0) + (data.fallbacks?.weather_fallbacks || 0)}
          </div>
          <p className="mt-1 text-xs text-muted">{data.fallbacks?.recommendation_fallbacks || 0} AI fallbacks, {data.fallbacks?.weather_fallbacks || 0} weather offline</p>
        </Card>
      </div>

      {/* ── Drift & Retraining row ── */}
      {data.drift && (
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <Card>
            <h3 className="text-xs font-bold uppercase tracking-wide text-muted">Avg Confidence (7d)</h3>
            <div className={`mt-3 font-display text-3xl ${(data.drift.avg_disease_confidence_7d || 1) < 0.7 ? "text-amber-600" : "text-farmer-700"}`}>
              {data.drift.avg_disease_confidence_7d != null ? `${(data.drift.avg_disease_confidence_7d * 100).toFixed(1)}%` : "N/A"}
            </div>
            <p className="mt-1 text-xs text-muted">30d avg: {data.drift.avg_disease_confidence_30d != null ? `${(data.drift.avg_disease_confidence_30d * 100).toFixed(1)}%` : "N/A"}</p>
          </Card>
          <Card>
            <h3 className="text-xs font-bold uppercase tracking-wide text-muted">Low Confidence Rate (7d)</h3>
            <div className={`mt-3 font-display text-3xl ${(data.drift.low_confidence_rate_7d || 0) > 20 ? "text-danger" : "text-ink"}`}>
              {data.drift.low_confidence_rate_7d != null ? `${data.drift.low_confidence_rate_7d.toFixed(1)}%` : "N/A"}
            </div>
            <p className="mt-1 text-xs text-muted">% of predictions below confidence threshold</p>
          </Card>
          <Card>
            <h3 className="text-xs font-bold uppercase tracking-wide text-muted">Retraining Candidates</h3>
            <div className={`mt-3 font-display text-3xl ${(data.drift.retraining_candidates || 0) > 50 ? "text-amber-600" : "text-ink"}`}>
              {data.drift.retraining_candidates ?? 0}
            </div>
            <p className="mt-1 text-xs text-muted">Pending dataset candidates</p>
          </Card>
          <Card>
            <h3 className="text-xs font-bold uppercase tracking-wide text-muted">Expert Correction Rate</h3>
            <div className={`mt-3 font-display text-3xl ${(data.drift.expert_correction_rate || 0) > 30 ? "text-danger" : "text-farmer-700"}`}>
              {data.drift.expert_correction_rate != null ? `${data.drift.expert_correction_rate.toFixed(1)}%` : "N/A"}
            </div>
            <p className="mt-1 text-xs text-muted">Reviews that were corrections</p>
          </Card>
        </div>
      )}

      {/* ── Charts ── */}
      <div className="grid gap-5 lg:grid-cols-2">
        <Card>
          <h3 className="font-display text-xl text-ink">Disease Distribution</h3>
          <div className="mt-5 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={data.disease_distribution} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label>
                  {data.disease_distribution.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card>
          <h3 className="font-display text-xl text-ink">AI Confidence Histogram</h3>
          <div className="mt-5 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.confidence_histogram}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#52772d" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* ── Model Health Panel ── */}
      {modelHealth && (
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-display text-xl text-ink">Model Registry Health</h3>
              <p className="mt-1 text-sm text-muted">
                {modelHealth.overall_status === "healthy"
                  ? "✓ All models loaded"
                  : "⚠ Some models are missing from disk"}
              </p>
            </div>
            <span className={`rounded-full px-3 py-1 text-xs font-semibold ${
              modelHealth.overall_status === "healthy"
                ? "bg-green-100 text-green-700"
                : "bg-amber-100 text-amber-700"
            }`}>
              {modelHealth.overall_status}
            </span>
          </div>
          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-xs font-semibold uppercase tracking-wide text-muted">
                  <th className="pb-2 pr-4">Model</th>
                  <th className="pb-2 pr-4">Version</th>
                  <th className="pb-2 pr-4">Status</th>
                  <th className="pb-2 pr-4">Val Acc</th>
                  <th className="pb-2">Test Acc</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(modelHealth.models as Record<string, any>).map(([key, m]) => (
                  <tr key={key} className="border-b last:border-0">
                    <td className="py-2 pr-4 font-medium text-ink">{key.replace(/_/g, " ")}</td>
                    <td className="py-2 pr-4 text-muted">{m.active_version ?? "—"}</td>
                    <td className="py-2 pr-4">
                      <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
                        m.status === "ok" ? "bg-green-50 text-green-700" : "bg-red-50 text-red-700"
                      }`}>
                        {m.status === "ok" ? "✓ OK" : "✗ Missing"}
                      </span>
                    </td>
                    <td className="py-2 pr-4 text-muted">{m.val_acc != null ? `${(m.val_acc * 100).toFixed(1)}%` : "—"}</td>
                    <td className="py-2 text-muted">{m.test_acc != null ? `${(m.test_acc * 100).toFixed(1)}%` : "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* ── Dataset Export Panel ── */}
      <Card>
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h3 className="font-display text-xl text-ink">MLOps Dataset Export</h3>
            <p className="mt-1 text-sm text-muted">
              {datasetSummary ? `${datasetSummary.total} total candidates · ${datasetSummary.by_status?.pending_review ?? 0} pending review` : "Loading…"}
            </p>
          </div>
        </div>

        <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wide text-muted mb-1">Crop Filter</label>
            <select className="w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm" value={exportCrop} onChange={e => setExportCrop(e.target.value)}>
              {CROP_OPTIONS.map(c => <option key={c}>{c}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wide text-muted mb-1">Status Filter</label>
            <select className="w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm" value={exportStatus} onChange={e => setExportStatus(e.target.value)}>
              {STATUS_OPTIONS.map(s => <option key={s}>{s}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wide text-muted mb-1">Image Target</label>
            <select className="w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm" value={exportImageTarget} onChange={e => setExportImageTarget(e.target.value as any)}>
              <option value="preprocessed">Preprocessed</option>
              <option value="raw">Raw Original</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wide text-muted mb-1">Format</label>
            <select className="w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm" value={exportFormat} onChange={e => setExportFormat(e.target.value as any)}>
              <option>PyTorch Folder</option>
              <option>JSON Manifest</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wide text-muted mb-1">Train / Val / Test Split (%)</label>
            <div className="flex gap-2">
              <input type="number" min={0} max={100} className="w-full rounded-md border border-gray-200 px-2 py-2 text-sm" placeholder="Train" value={exportTrain} onChange={e => setExportTrain(Number(e.target.value))} />
              <input type="number" min={0} max={100} className="w-full rounded-md border border-gray-200 px-2 py-2 text-sm" placeholder="Val" value={exportVal} onChange={e => setExportVal(Number(e.target.value))} />
              <input type="number" min={0} max={100} className="w-full rounded-md border border-gray-200 px-2 py-2 text-sm" placeholder="Test" value={exportTest} onChange={e => setExportTest(Number(e.target.value))} />
            </div>
            <p className="mt-1 text-xs text-muted">Must sum to 100. Current: {exportTrain + exportVal + exportTest}</p>
          </div>
        </div>

        <div className="mt-5">
          <Button variant="secondary" onClick={handleExportMLOps} disabled={exporting} className="flex items-center gap-2">
            {exporting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Download className="h-4 w-4" />}
            {exporting ? "Exporting…" : "Export MLOps Dataset"}
          </Button>
        </div>
      </Card>
    </div>
  );
}
