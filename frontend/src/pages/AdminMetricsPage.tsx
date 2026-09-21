import { useQuery } from "@tanstack/react-query";
import { request } from "../api/client";
import { exportDataset } from "../api/admin";
import { useAuth } from "../context/AuthContext";
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line
} from "recharts";
import { Loader2 } from "lucide-react";
import { Card, Button } from "../components/ui";

const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6'];

export default function AdminMetricsPage() {

  const handleExportMLOps = async () => {
    try {
      const blob = await exportDataset(token!, {
        filters: { expert: true, farmer: true },
        split: { train: 70, val: 15, test: 15 },
        format: "PyTorch Folder",
        imageTarget: "preprocessed",
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = "dataset_export.zip";
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (e) {
      console.error(e);
      alert("Export failed");
    }
  };

  const { token } = useAuth();
  const { data, isLoading } = useQuery({
    queryKey: ["admin_metrics"],
    queryFn: () => request<any>("/admin/metrics", {}, token!),
    enabled: !!token
  });

  if (isLoading) return <div className="flex min-h-[40vh] items-center justify-center"><Loader2 className="animate-spin text-admin-500" /></div>;
  if (!data) return <div className="rounded-md border border-red-100 bg-red-50 p-6 text-danger">Failed to load metrics.</div>;

  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="font-display text-3xl text-ink sm:text-4xl">System Metrics & ML Ops</h1>
          <p className="mt-2 text-sm text-muted">Operational health and model validation signals.</p>
        </div>
        <Button variant="secondary" onClick={handleExportMLOps}>Export MLOps Dataset</Button>
      </div>
      
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <h3 className="text-xs font-bold uppercase tracking-wide text-muted">Total Users & Workspaces</h3>
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
          <p className="mt-1 text-xs text-muted">Predictions currently in worker processing</p>
        </Card>
        <Card>
          <h3 className="text-xs font-bold uppercase tracking-wide text-muted">Pipeline Latency</h3>
          <div className="mt-3 font-display text-3xl text-ink">{data.processing_duration?.avg_ms || 0}<span className="text-sm font-normal text-muted"> ms avg</span></div>
          <p className="mt-1 text-xs text-muted">P95: {data.processing_duration?.p95_ms || 0} ms</p>
        </Card>
      </div>

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
            {data.expert_metrics?.validated_accuracy !== null && data.expert_metrics?.validated_accuracy !== undefined ? `${data.expert_metrics.validated_accuracy}%` : "Pending Data"}
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

      <div className="grid gap-5 lg:grid-cols-2">
        <Card><h3 className="font-display text-xl text-ink">Disease Distribution</h3>
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

        <Card><h3 className="font-display text-xl text-ink">AI Confidence Histogram</h3>
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
    </div>
  );
}
