import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { request } from "../api/client";
import { 
  AlertTriangle, 
  Trash2, 
  DownloadCloud, 
  Settings as SettingsIcon,
  Globe,
  Sliders,
  CheckCircle2,
  Database,
  Cloud
} from "lucide-react";
import { motion } from "motion/react";
import "../styles/FarmSettingsPage.css"; 

export default function SettingsPage() {
  const { user, token } = useAuth();
  const queryClient = useQueryClient();
  const isAdmin = user?.role === "admin";
  
  // General
  const [lang, setLang] = useState("English");
  const [units, setUnits] = useState("Metric");

  // Danger Zone
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteConfirmText, setDeleteConfirmText] = useState("");
  const [isDeleting, setIsDeleting] = useState(false);

  // MLOps
  const [exportFilters, setExportFilters] = useState({ expert: true, farmer: true });
  const [exportCrop, setExportCrop] = useState("All Crops");
  const [exportFormat, setExportFormat] = useState("PyTorch Folder");
  const [exportImage, setExportImage] = useState("preprocessed");
  const [splitTrain, setSplitTrain] = useState(70);
  const [splitVal, setSplitVal] = useState(15);
  const [isExporting, setIsExporting] = useState(false);

  // Config
  const [routingThresh, setRoutingThresh] = useState(75);
  const [expertThresh, setExpertThresh] = useState(70);
  const [configSaved, setConfigSaved] = useState(false);

  // Data Fetching
  const { data: configData } = useQuery({
    queryKey: ["adminConfig"],
    queryFn: () => request<any>("/admin/config", {}, token!),
    enabled: isAdmin,
  });

  const { data: datasetSummary } = useQuery({
    queryKey: ["datasetSummary"],
    queryFn: () => request<any>("/admin/dataset/summary", {}, token!),
    enabled: isAdmin,
  });

  useEffect(() => {
    if (configData) {
      setRoutingThresh(Math.round(configData.crop_routing_threshold * 100));
      setExpertThresh(Math.round(configData.expert_escalation_cutoff * 100));
    }
  }, [configData]);

  const updateConfig = useMutation({
    mutationFn: async () => request("/admin/config", {
      method: "PUT",
      body: JSON.stringify({
        crop_routing_threshold: routingThresh / 100,
        expert_escalation_cutoff: expertThresh / 100
      })
    }, token!),
    onSuccess: () => {
      setConfigSaved(true);
      setTimeout(() => setConfigSaved(false), 3000);
      queryClient.invalidateQueries({ queryKey: ["adminConfig"] });
    }
  });

  const handleDeleteData = async () => {
    if (deleteConfirmText !== "DELETE") return;
    setIsDeleting(true);
    try {
      await request("/admin/purge", { method: "DELETE" }, token!);
      alert("Database wiped.");
      setShowDeleteModal(false);
      window.location.reload();
    } catch (err: any) {
      alert("Failed: " + err.message);
    } finally {
      setIsDeleting(false);
    }
  };

  const handlePurgeBlobs = async () => {
    if (!confirm("Delete all orphaned image blobs?")) return;
    try {
      const res = await request<any>("/admin/blobs", { method: "DELETE" }, token!);
      alert(`Success! Deleted ${res.deleted_files} orphaned files.`);
    } catch (err: any) {
      alert("Failed: " + err.message);
    }
  };

  const handleExportMLOps = async () => {
    setIsExporting(true);
    try {
      const payload = {
        filters: exportFilters,
        split: { train: splitTrain, val: splitVal, test: 100 - splitTrain - splitVal },
        format: exportFormat,
        imageTarget: exportImage
      };
      const res = await fetch("http://localhost:8000/admin/dataset/export", {
        method: "POST",
        headers: { 
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "dataset_export.zip";
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
      } else {
        alert("Export failed.");
      }
    } catch (err) {
      console.error(err);
      alert("Export error.");
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="farm-settings-page">
      <div className="page-header">
        <h1><SettingsIcon size={28} style={{ verticalAlign: 'middle', marginRight: '10px' }} /> Settings</h1>
        <p>Manage application defaults, model governance, and MLOps data pipelines.</p>
      </div>

      <div className="card" style={{ padding: "2rem", marginBottom: "2rem" }}>
        <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><Globe size={20} /> Language & Telemetry Preferences</h3>
        <p style={{ color: "var(--muted)", marginBottom: "1.5rem" }}>System-wide defaults for localized UI and measurement units.</p>
        
        <div className="form-row">
          <div className="form-group">
            <label>Interface Language</label>
            <select className="form-control" value={lang} onChange={e => setLang(e.target.value)}>
              <option>English</option>
              <option>Gujarati</option>
              <option>Hindi</option>
            </select>
          </div>
          <div className="form-group">
            <label>Units</label>
            <select className="form-control" value={units} onChange={e => setUnits(e.target.value)}>
              <option>Metric (ha, °C)</option>
              <option>Imperial (acres, °F)</option>
            </select>
          </div>
        </div>
      </div>

      {isAdmin && (
        <>
          <motion.div className="card" initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ padding: "2rem", marginBottom: "2rem", borderTop: "4px solid #0ea5e9" }}>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><Database size={20} color="#0ea5e9" /> MLOps Dataset Curation & Export Engine</h3>
            <p style={{ color: "var(--muted)", marginBottom: "1.5rem" }}>Package validated field diagnostics into versioned model training sets.</p>
            
            <div style={{ background: "#f8fafc", padding: "1.5rem", borderRadius: "8px", marginBottom: "1.5rem" }}>
              <strong>Ground Truth Inclusion:</strong>
              <div style={{ display: "flex", gap: "2rem", marginTop: "0.5rem" }}>
                <label style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <input type="checkbox" checked={exportFilters.expert} onChange={e => setExportFilters(p => ({...p, expert: e.target.checked}))} />
                  Expert Overridden Cases ({datasetSummary?.expert_overridden || 0})
                </label>
                <label style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <input type="checkbox" checked={exportFilters.farmer} onChange={e => setExportFilters(p => ({...p, farmer: e.target.checked}))} />
                  Confirmed Farmer Feedback ({datasetSummary?.farmer_confirmed || 0})
                </label>
              </div>
            </div>

            <div className="form-row" style={{ marginBottom: "1.5rem" }}>
              <div className="form-group">
                <label>Target Crop</label>
                <select className="form-control" value={exportCrop} onChange={e => setExportCrop(e.target.value)}>
                  <option>All Crops (Tomato, Cotton, Potato)</option>
                  <option>Cotton</option>
                  <option>Tomato</option>
                </select>
              </div>
              <div className="form-group">
                <label>Archive Format</label>
                <select className="form-control" value={exportFormat} onChange={e => setExportFormat(e.target.value)}>
                  <option>PyTorch Folder</option>
                  <option>COCO Bounding Boxes</option>
                  <option>JSON Manifest</option>
                </select>
              </div>
            </div>

            <div style={{ marginBottom: "1.5rem" }}>
              <label>Image Target:</label>
              <div style={{ display: "flex", gap: "2rem", marginTop: "0.5rem" }}>
                <label style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <input type="radio" name="imgTarget" checked={exportImage === "preprocessed"} onChange={() => setExportImage("preprocessed")} />
                  OpenCV Preprocessed (224x224)
                </label>
                <label style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <input type="radio" name="imgTarget" checked={exportImage === "raw"} onChange={() => setExportImage("raw")} />
                  Raw Camera Originals
                </label>
              </div>
            </div>

            <div style={{ marginBottom: "2rem" }}>
              <label>Dataset Split: Train {splitTrain}% / Val {splitVal}% / Test {100 - splitTrain - splitVal}%</label>
              <input type="range" min="50" max="90" value={splitTrain} onChange={e => setSplitTrain(Number(e.target.value))} style={{ width: "100%", margin: "1rem 0" }} />
            </div>

            <div style={{ display: "flex", gap: "1rem" }}>
              <button className="btn btn-primary" style={{ background: "#0ea5e9" }} onClick={handleExportMLOps} disabled={isExporting}>
                <DownloadCloud size={18} /> {isExporting ? "Packaging..." : "Export Dataset Archive (.zip)"}
              </button>
              <button className="btn" style={{ border: "1px solid #0ea5e9", color: "#0ea5e9" }} disabled={isExporting}>
                <Cloud size={18} /> Sync to MinIO/S3
              </button>
            </div>
          </motion.div>

          <motion.div className="card" initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ padding: "2rem", marginBottom: "2rem" }}>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><Sliders size={20} /> Diagnostic Decision Thresholds (config.yaml)</h3>
            <p style={{ color: "var(--muted)", marginBottom: "1.5rem" }}>Enables real-time modification of operational rules without redeploying backend application code.</p>
            
            <div style={{ marginBottom: "1.5rem" }}>
              <label>Crop Routing Confidence Min: {routingThresh}%</label>
              <input type="range" min="50" max="95" value={routingThresh} onChange={e => setRoutingThresh(Number(e.target.value))} style={{ width: "100%" }} />
            </div>
            
            <div style={{ marginBottom: "1.5rem" }}>
              <label>Expert Escalation Cutoff: {expertThresh}%</label>
              <input type="range" min="50" max="95" value={expertThresh} onChange={e => setExpertThresh(Number(e.target.value))} style={{ width: "100%" }} />
            </div>

            <button className="btn btn-primary" onClick={() => updateConfig.mutate()} disabled={updateConfig.isPending}>
              {updateConfig.isPending ? "Saving..." : "Save Config Parameters"}
            </button>
            {configSaved && <span style={{ marginLeft: "1rem", color: "var(--green)" }}><CheckCircle2 size={16} style={{ verticalAlign: 'middle' }} /> Saved</span>}
          </motion.div>

          <motion.div className="admin-danger-zone card" initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ padding: "2rem", border: "1px solid var(--orange)", background: "#fffdfa" }}>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', color: "var(--orange)" }}><AlertTriangle size={20} /> Administrative Danger Zone</h3>
            
            <div style={{ display: "flex", gap: "1rem", marginTop: "1.5rem" }}>
              <button type="button" className="btn btn-primary" style={{ background: "#b44c3c" }} onClick={() => setShowDeleteModal(true)}>
                <Trash2 size={16} /> Clear Operational Predictions
              </button>
              <button type="button" className="btn" style={{ border: "1px solid #b44c3c", color: "#b44c3c" }} onClick={handlePurgeBlobs}>
                <Trash2 size={16} /> Purge Orphaned Leaf Blobs
              </button>
            </div>
          </motion.div>
        </>
      )}

      {showDeleteModal && (
        <div className="modal-backdrop" style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.5)", zIndex: 1000, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <div className="modal-content card" style={{ maxWidth: "400px", width: "90%", padding: "2rem" }}>
            <h3 style={{ color: "#b44c3c", marginTop: 0 }}>Confirm Purge</h3>
            <p style={{ fontSize: "0.9rem", color: "var(--muted)" }}>Type <strong>DELETE</strong> below.</p>
            <input type="text" className="form-control" value={deleteConfirmText} onChange={(e) => setDeleteConfirmText(e.target.value)} placeholder="DELETE" style={{ marginBottom: "1rem" }} />
            <div style={{ display: "flex", gap: "1rem", justifyContent: "flex-end" }}>
              <button className="btn" onClick={() => setShowDeleteModal(false)}>Cancel</button>
              <button className="btn btn-primary" style={{ background: "#b44c3c" }} disabled={deleteConfirmText !== "DELETE" || isDeleting} onClick={handleDeleteData}>
                Confirm Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
