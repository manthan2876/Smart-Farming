import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useQueryClient } from "@tanstack/react-query";
import { request } from "../api/client";
import { AlertTriangle, Trash2, DownloadCloud, Settings as SettingsIcon } from "lucide-react";
import { motion } from "motion/react";
import "../styles/FarmSettingsPage.css"; // Reuse some card styles

export default function SettingsPage() {
  const { user, token } = useAuth();
  const queryClient = useQueryClient();
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteConfirmText, setDeleteConfirmText] = useState("");
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDeleteData = async () => {
    if (deleteConfirmText !== "DELETE") return;
    setIsDeleting(true);
    try {
      await request("/admin/purge", { method: "DELETE" }, token!);
      alert("Database has been wiped successfully.");
      setShowDeleteModal(false);
      setDeleteConfirmText("");
      queryClient.clear();
      window.location.reload();
    } catch (err: any) {
      alert("Failed to delete database: " + err.message);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleExportMLOps = async () => {
    try {
      const res = await fetch("http://localhost:8000/admin/mlops/export", {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "mlops_dataset.zip";
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
      } else {
        alert("Failed to export MLOps dataset.");
      }
    } catch (err) {
      console.error(err);
      alert("Error exporting MLOps dataset.");
    }
  };

  return (
    <div className="farm-settings-page">
      <div className="page-header">
        <h1><SettingsIcon size={28} style={{ verticalAlign: 'middle', marginRight: '10px' }} /> System Settings</h1>
        <p>Manage your account, preferences, and system-wide configurations.</p>
      </div>

      {user?.role !== "admin" && (
        <div className="card" style={{ padding: "2rem", textAlign: "center", color: "var(--muted)", background: "#f8fafc" }}>
          <h3>General Settings</h3>
          <p>No generic settings available for your role at this time. Future updates will include notification preferences and localization settings.</p>
        </div>
      )}

      {user?.role === "admin" && (
        <motion.div 
          className="admin-danger-zone card"
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          style={{ marginTop: "2rem", border: "1px solid var(--orange)", background: "#fffdfa" }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", color: "var(--orange)", marginBottom: "1rem" }}>
            <AlertTriangle size={20} />
            <h2 style={{ fontSize: "1.1rem", margin: 0 }}>Admin Control Panel</h2>
          </div>
          
          <div style={{ marginBottom: "2rem", paddingBottom: "1.5rem", borderBottom: "1px solid #fce8d5" }}>
            <h3 style={{ fontSize: "1rem", color: "#334155", margin: "0 0 0.5rem 0" }}>MLOps Dataset Export</h3>
            <p style={{ fontSize: "0.9rem", color: "var(--muted)", marginBottom: "1rem" }}>
              Download a curated ZIP archive of field-verified crop scans. Includes 'dataset.csv' mappings and original imagery for fine-tuning Vision Transformers.
            </p>
            <button 
              type="button" 
              className="btn btn-primary" 
              style={{ background: "#0ea5e9" }}
              onClick={handleExportMLOps}
            >
              <DownloadCloud size={16} /> Export MLOps Dataset
            </button>
          </div>

          <div>
            <h3 style={{ fontSize: "1rem", color: "#b91c1c", margin: "0 0 0.5rem 0" }}>Database Purge</h3>
            <p style={{ fontSize: "0.9rem", color: "var(--muted)", marginBottom: "1rem" }}>
              This action is irreversible and will delete all predictions, feedback, farm records, and historical scans across the entire platform.
            </p>
            <button 
              type="button" 
              className="btn btn-primary" 
              style={{ background: "#b44c3c" }}
              onClick={() => setShowDeleteModal(true)}
            >
              <Trash2 size={16} /> Delete Whole Database
            </button>
          </div>
        </motion.div>
      )}

      {showDeleteModal && (
        <div className="modal-backdrop" style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.5)", zIndex: 1000, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <div className="modal-content card" style={{ maxWidth: "400px", width: "90%", padding: "2rem" }}>
            <h3 style={{ color: "#b44c3c", marginTop: 0 }}>Confirm Database Purge</h3>
            <p style={{ fontSize: "0.9rem", color: "var(--muted)" }}>
              This will completely wipe all operational data. To confirm, please type <strong>DELETE</strong> below.
            </p>
            <input 
              type="text" 
              className="form-control" 
              value={deleteConfirmText}
              onChange={(e) => setDeleteConfirmText(e.target.value)}
              placeholder="DELETE"
              style={{ marginBottom: "1rem" }}
            />
            <div style={{ display: "flex", gap: "1rem", justifyContent: "flex-end" }}>
              <button className="btn" onClick={() => { setShowDeleteModal(false); setDeleteConfirmText(""); }}>Cancel</button>
              <button 
                className="btn btn-primary" 
                style={{ background: "#b44c3c", opacity: deleteConfirmText !== "DELETE" ? 0.5 : 1 }}
                disabled={deleteConfirmText !== "DELETE" || isDeleting}
                onClick={handleDeleteData}
              >
                {isDeleting ? "Deleting..." : "Confirm Delete"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
