import { useQuery } from "@tanstack/react-query";
import { request } from "../api/client";
import { useAuth } from "../context/AuthContext";
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line
} from "recharts";
import { Loader2 } from "lucide-react";

const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6'];

export default function AdminMetricsPage() {

  const handleExportMLOps = async () => {
    try {
      const res = await fetch("http://localhost:8000/admin/mlops/export", {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = "dataset_export.zip";
        a.click();
      } else {
        alert("Export failed");
      }
    } catch (e) {
      console.error(e);
    }
  };

  const { token } = useAuth();
  const { data, isLoading } = useQuery({
    queryKey: ["admin_metrics"],
    queryFn: () => request<any>("/admin/metrics", {}, token!),
    enabled: !!token
  });

  if (isLoading) return <div style={{ display: "flex", justifyContent: "center", padding: "4rem" }}><Loader2 className="animate-spin" /></div>;
  if (!data) return <div>Failed to load metrics.</div>;

  return (
    <div style={{ padding: "2rem" }}>
      <h1 style={{ marginBottom: "2rem", color: "var(--ink)" }}>System Metrics & ML Ops</h1>
      
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1.5rem", marginBottom: "2rem" }}>
        <div style={{ background: "#fff", padding: "1.5rem", borderRadius: "12px", border: "1px solid var(--line)" }}>
          <h3 style={{ margin: "0 0 0.5rem 0", color: "var(--muted)" }}>Total Users</h3>
          <div style={{ fontSize: "2rem", fontWeight: "bold" }}>{data.total_users}</div>
        </div>
        <div style={{ background: "#fff", padding: "1.5rem", borderRadius: "12px", border: "1px solid var(--line)" }}>
          <h3 style={{ margin: "0 0 0.5rem 0", color: "var(--muted)" }}>Total Scans</h3>
          <div style={{ fontSize: "2rem", fontWeight: "bold" }}>{data.total_scans}</div>
        </div>
        <div style={{ background: "#fff", padding: "1.5rem", borderRadius: "12px", border: "1px solid var(--line)" }}>
          <h3 style={{ margin: "0 0 0.5rem 0", color: "var(--muted)" }}>Model Accuracy (User Validation)</h3>
          <div style={{ fontSize: "2rem", fontWeight: "bold", color: data.accuracy > 85 ? "var(--green)" : "#ef4444" }}>{data.accuracy.toFixed(1)}%</div>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "2rem" }}>
        <div style={{ background: "#fff", padding: "1.5rem", borderRadius: "12px", border: "1px solid var(--line)" }}>
          <h3>Disease Distribution</h3>
          <div style={{ height: 300 }}>
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
        </div>

        <div style={{ background: "#fff", padding: "1.5rem", borderRadius: "12px", border: "1px solid var(--line)" }}>
          <h3>AI Confidence Histogram</h3>
          <div style={{ height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.confidence_histogram}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="var(--green)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
