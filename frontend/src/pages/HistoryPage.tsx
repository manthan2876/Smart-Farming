import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { request } from "../api/client";
import { History, ArrowRight, Filter, Search } from "lucide-react";
import { motion } from "motion/react";
import { Badge, Button, Card, Input, Table } from "../components/ui";

interface PredictionRecord {
  prediction_id: number | string | null;
  crop?: { label?: string; name?: string; [key: string]: any };
  disease?: { label?: string; name?: string; [key: string]: any };
  severity?: { bucket?: string; level?: string; name?: string; [key: string]: any } | string;
  confidence?: number;
  request_id?: string;
  [key: string]: any;
}

export default function HistoryPage() {
  const { token } = useAuth();
  const [filterCrop, setFilterCrop] = useState("All");
  const [searchQuery, setSearchQuery] = useState("");

  const { data: scans = [], isLoading } = useQuery<PredictionRecord[]>({
    queryKey: ["fullScanHistory"],
    queryFn: () => request<PredictionRecord[]>("/history?limit=50", {}, token!),
    enabled: !!token,
  });

  const filteredScans = scans.filter((scan) => {
    const cropName = String(scan.crop?.label || scan.crop?.name || "");
    const diseaseName = String(scan.disease?.label || scan.disease?.name || "");
    
    const matchesCrop = filterCrop === "All" || cropName.toLowerCase() === filterCrop.toLowerCase();
    const matchesSearch = diseaseName.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          cropName.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCrop && matchesSearch;
  });

  // Extract unique crop names safely using 'label' or 'name'
  const uniqueCrops = [
    "All", 
    ...Array.from(new Set(scans.map((s) => s.crop?.label || s.crop?.name).filter(Boolean)))
  ] as string[];

  return (
    <div className="space-y-6 pb-12">
      <div>
        <h1 className="font-display text-3xl text-ink sm:text-4xl">Diagnostic Scan History</h1>
        <p className="mt-3 max-w-3xl leading-7 text-muted">Review past crop health reports, confidence scores, and historical disease outbreaks.</p>
      </div>

      <motion.div 
        className="space-y-5"
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <Card className="flex flex-col gap-4 sm:flex-row sm:items-end" padding="md">
          <div className="flex-1">
            <Input id="history-search" label="Search records" leadingIcon={<Search size={18} />} type="text" placeholder="Search disease or crop..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} />
          </div>
          <label className="block space-y-2 sm:w-56" htmlFor="history-crop-filter">
            <span className="flex items-center gap-2 text-sm font-semibold text-ink"><Filter size={16} /> Crop</span>
            <select 
              id="history-crop-filter"
              value={filterCrop} 
              onChange={(e) => setFilterCrop(e.target.value)}
              className="min-h-11 w-full rounded-sm border border-line bg-surface px-3 text-sm text-ink focus:border-farmer-500 focus:outline-none focus:ring-4 focus:ring-farmer-100"
            >
              {uniqueCrops.map((crop, idx) => (
                <option key={idx} value={crop}>{crop}</option>
              ))}
            </select>
          </label>
        </Card>

        {isLoading ? (
          <Card className="flex items-center justify-center gap-3 text-sm text-muted"><div className="h-5 w-5 animate-spin rounded-full border-2 border-farmer-200 border-t-farmer-700" /><p>Loading scan records...</p></Card>
        ) : filteredScans.length === 0 ? (
          <Card className="flex flex-col items-center text-center" padding="lg">
            <History className="text-farmer-700" size={48} />
            <h3 className="mt-5 font-display text-xl text-ink">No scan history found</h3>
            <p className="mt-2 text-sm text-muted">You haven't run any diagnostic scans matching this filter yet.</p>
            <Link to="/scan" className="mt-5"><Button size="sm">Run New Scan</Button></Link>
          </Card>
        ) : (
          <Table>
              <thead>
                <tr className="bg-canvas text-xs uppercase tracking-wide text-muted">
                  <th className="px-5 py-4 font-semibold">Crop</th>
                  <th className="px-5 py-4 font-semibold">Identified Condition</th>
                  <th className="px-5 py-4 font-semibold">Severity</th>
                  <th className="px-5 py-4 font-semibold">Date / Request</th>
                  <th className="px-5 py-4 font-semibold">Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredScans.map((scan, index) => {
                  const cropName = scan.crop?.label || scan.crop?.name || "Unknown Crop";
                  const diseaseName = scan.disease?.label || scan.disease?.name || "Unidentified Condition";
                  
                  // Handle severity mapping from object properties like 'bucket'
                  const rawSeverity = scan.severity;
                  const severityText = typeof rawSeverity === "object" && rawSeverity !== null
                    ? (rawSeverity.bucket || rawSeverity.level || rawSeverity.name || "Unknown")
                    : String(rawSeverity || "Unknown");

                  const recordId = scan.prediction_id;

                  return (
                    <tr className="border-t border-line text-sm text-ink" key={recordId || index}>
                      <td className="px-5 py-4"><Badge>{cropName}</Badge></td>
                      <td className="px-5 py-4 font-semibold">{diseaseName}</td>
                      <td className="px-5 py-4">
                        <Badge tone={severityText.toLowerCase() === "severe" ? "danger" : severityText.toLowerCase() === "moderate" ? "warning" : "success"}>{severityText}</Badge>
                      </td>
                      <td className="px-5 py-4 text-muted">{scan.request_id ? `ID: ${scan.request_id.slice(0, 8)}...` : "N/A"}</td>
                      <td className="px-5 py-4">
                        {recordId ? (
                          <Link to={`/predictions/${recordId}`} className="inline-flex items-center gap-1 font-semibold text-farmer-700 hover:text-farmer-900">
                            View <ArrowRight size={14} />
                          </Link>
                        ) : (
                          <span className="text-muted">Unavailable</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
          </Table>
        )}
      </motion.div>
    </div>
  );
}
