import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { AlertCircle, CheckCircle, ArrowRight } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { getExpertQueue } from "../api/expert";
import { motion } from "motion/react";
import { Badge, Card, Table } from "../components/ui";

export default function ExpertQueuePage() {
  const { token } = useAuth();

  const { data: queue = [], isLoading, error } = useQuery({
    queryKey: ["expertQueue"],
    queryFn: () => getExpertQueue(token!),
    enabled: !!token,
  });

  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col gap-5 rounded-lg bg-expert-700 p-7 text-white shadow-card sm:flex-row sm:items-center sm:justify-between sm:p-10">
        <div>
          <h1 className="font-display text-3xl text-white sm:text-4xl">Expert Triage Queue</h1>
          <p className="mt-3 text-white/70">Review and verify uncertain diagnoses escalated by the AI system.</p>
        </div>
        <AlertCircle className="text-expert-100" size={48} />
      </div>

      <motion.div
        className="rounded-md border border-line bg-surface p-5 shadow-soft sm:p-6"
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div>
          <h3 className="font-display text-xl text-ink">Pending Reviews ({queue.length})</h3>
        </div>

        {isLoading ? (
          <p className="mt-5 text-sm text-muted">Loading queue...</p>
        ) : error ? (
          <p className="mt-5 text-sm text-danger">Failed to load queue.</p>
        ) : queue.length === 0 ? (
          <div className="mt-5 flex flex-col items-center rounded-sm bg-farmer-50 p-8 text-center text-sm text-muted">
            <CheckCircle className="text-farmer-700" size={40} />
            <p className="mt-3">The queue is completely empty. Great job!</p>
          </div>
        ) : (
          <Table className="mt-5">
              <thead>
                <tr className="bg-canvas text-xs uppercase tracking-wide text-muted">
                  {['Date', 'Crop', 'AI Diagnosis', 'Confidence', 'Severity', 'Action'].map((heading) => <th key={heading} className="px-5 py-4 font-semibold">{heading}</th>)}
                </tr>
              </thead>
              <tbody>
                {queue.map((item) => (
                  <tr className="border-t border-line text-sm text-ink" key={item.review_id}>
                    <td className="px-5 py-4 text-muted">{item.created_at ? new Date(item.created_at).toLocaleDateString() : "N/A"}</td>
                    <td className="px-5 py-4"><Badge>{item.crop || "Unknown"}</Badge></td>
                    <td className="px-5 py-4 font-semibold">{item.disease || "Unknown"}</td>
                    <td className="px-5 py-4">{(item.disease_conf * 100).toFixed(1)}%</td>
                    <td className="px-5 py-4">
                      <Badge tone={item.severity_pct > 60 ? "danger" : item.severity_pct > 25 ? "warning" : "success"}>
                        {item.severity_pct > 60 ? 'Severe' : item.severity_pct > 25 ? 'Moderate' : 'Low'}
                      </Badge>
                    </td>
                    <td>
                      <Link to={`/admin/expert/${item.review_id}`} className="inline-flex items-center gap-1 font-semibold text-expert-700 hover:text-expert-500">
                        Review <ArrowRight size={14} />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
          </Table>
        )}
      </motion.div>
    </div>
  );
}
