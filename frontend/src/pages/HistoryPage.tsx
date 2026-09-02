import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { request } from "../api/client";
import { History, ArrowRight, Filter, Search } from "lucide-react";
import { motion } from "motion/react";
import "../styles/HistoryPage.css";

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
    <div className="history-page">
      <div className="page-header">
        <h1>Diagnostic Scan History</h1>
        <p>Review past crop health reports, confidence scores, and historical disease outbreaks.</p>
      </div>

      <motion.div 
        className="history-content-container"
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="history-filters-bar">
          <div className="search-box">
            <Search size={18} />
            <input 
              type="text" 
              placeholder="Search disease or crop..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="form-control"
            />
          </div>
          <div className="filter-dropdown-group">
            <Filter size={16} />
            <select 
              value={filterCrop} 
              onChange={(e) => setFilterCrop(e.target.value)}
              className="form-control"
            >
              {uniqueCrops.map((crop, idx) => (
                <option key={idx} value={crop}>{crop}</option>
              ))}
            </select>
          </div>
        </div>

        {isLoading ? (
          <div className="loading-state"><div className="spinner"></div><p>Loading scan records...</p></div>
        ) : filteredScans.length === 0 ? (
          <div className="empty-state">
            <History size={48} />
            <h3>No scan history found</h3>
            <p>You haven't run any diagnostic scans matching this filter yet.</p>
            <Link to="/scan" className="btn btn-primary btn-sm">Run New Scan</Link>
          </div>
        ) : (
          <div className="scans-table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Crop</th>
                  <th>Identified Condition</th>
                  <th>Severity</th>
                  <th>Date / Request</th>
                  <th>Action</th>
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
                    <tr key={recordId || index}>
                      <td><span className="crop-tag">{cropName}</span></td>
                      <td className="font-semibold">{diseaseName}</td>
                      <td>
                        <span className={`severity-pill ${severityText.toLowerCase()}`}>
                          {severityText}
                        </span>
                      </td>
                      <td>{scan.request_id ? `ID: ${scan.request_id.slice(0, 8)}...` : "N/A"}</td>
                      <td>
                        {recordId ? (
                          <Link to={`/predictions/${recordId}`} className="btn-icon-link">
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
            </table>
          </div>
        )}
      </motion.div>
    </div>
  );
}
