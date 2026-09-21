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
      
      <div className="grid gap-5 sm:grid-cols-3">
        <Card><h3 className="text-xs font-bold uppercase tracking-wide text-muted">Total Users</h3><div className="mt-3 font-display text-3xl text-ink">{data.total_users}</div></Card>
        <Card><h3 className="text-xs font-bold uppercase tracking-wide text-muted">Total Scans</h3><div className="mt-3 font-display text-3xl text-ink">{data.total_scans}</div></Card>
        <Card><h3 className="text-xs font-bold uppercase tracking-wide text-muted">Model Accuracy</h3><div className={`mt-3 font-display text-3xl ${data.accuracy > 85 ? "text-farmer-700" : "text-danger"}`}>{data.accuracy.toFixed(1)}%</div></Card>
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
