import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "../context/AuthContext";
import { request } from "../api/client";
import { MapPin, Save, CheckCircle2, Sprout, AlertTriangle, Trash2 } from "lucide-react";
import { motion } from "motion/react";
import "../styles/FarmSettingsPage.css";

export default function FarmSettingsPage() {
  const { token, user } = useAuth();
  const queryClient = useQueryClient();

  const [farmName, setFarmName] = useState("");
  const [location, setLocation] = useState("");
  const [area, setArea] = useState<number>(0);
  const [lat, setLat] = useState<number>(0);
  const [lon, setLon] = useState<number>(0);
  const [cropHistory, setCropHistory] = useState("");
  const [successMessage, setSuccessMessage] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteConfirmText, setDeleteConfirmText] = useState("");
  const [isDeleting, setIsDeleting] = useState(false);


  const { data: farmData, isLoading } = useQuery({
    queryKey: ["farmSettings"],
    queryFn: () => request<any>("/farm", {}, token!),
    enabled: !!token,
  });

  useEffect(() => {
    if (farmData) {
      setFarmName(farmData.name || "");
      setLocation(farmData.location || "");
      setArea(farmData.area_acres || 0);
      setLat(farmData.latitude || 21.7645);
      setLon(farmData.longitude || 72.1519);
      setCropHistory(Array.isArray(farmData.crop_history) ? farmData.crop_history.join(", ") : farmData.crop_history || "");
    }
  }, [farmData]);

  const mutation = useMutation({
    mutationFn: async (updatedPayload: any) => {
      return request("/farm", {
        method: "PUT",
        body: JSON.stringify(updatedPayload),
      }, token!);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["farmSettings"] });
      setSuccessMessage(true);
      setTimeout(() => setSuccessMessage(false), 4000);
    },
  });


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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate({
      name: farmName,
      location: location,
      area_acres: Number(area),
      latitude: Number(lat),
      longitude: Number(lon),
      crop_history: cropHistory.split(",").map((s) => s.trim()).filter(Boolean),
    });
  };

  if (isLoading) return <div className="loading-state"><div className="spinner"></div></div>;

  return (
    <div className="farm-settings-page">
      <div className="page-header">
        <h1>Farm Configuration & Plot Settings</h1>
        <p>Manage your GPS coordinates, total acreage, and historic crop rotation cycles.</p>
      </div>

      <motion.form 
        onSubmit={handleSubmit} 
        className="settings-form-container card"
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
      >
        {successMessage && (
          <div className="alert alert-success">
            <CheckCircle2 size={18} />
            <span>Farm settings updated successfully!</span>
          </div>
        )}

        <div className="form-group">
          <label><Sprout size={16} /> Farm Name / Identifier</label>
          <input 
            type="text" 
            value={farmName} 
            onChange={(e) => setFarmName(e.target.value)} 
            className="form-control"
            required 
          />
        </div>

        <div className="form-group">
          <label><MapPin size={16} /> Location / Region</label>
          <input 
            type="text" 
            value={location} 
            onChange={(e) => setLocation(e.target.value)} 
            className="form-control"
            placeholder="e.g. Bhavnagar, Gujarat"
            required 
          />
        </div>

        <div className="form-group">
          <label>Total Farm Area (Acres)</label>
          <input 
            type="number" 
            step="any" 
            value={area} 
            onChange={(e) => setArea(Number(e.target.value))} 
            className="form-control"
            required 
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label><MapPin size={16} /> GPS Latitude</label>
            <input 
              type="number" 
              step="any" 
              value={lat} 
              onChange={(e) => setLat(Number(e.target.value))} 
              className="form-control"
              required 
            />
          </div>
          <div className="form-group">
            <label><MapPin size={16} /> GPS Longitude</label>
            <input 
              type="number" 
              step="any" 
              value={lon} 
              onChange={(e) => setLon(Number(e.target.value))} 
              className="form-control"
              required 
            />
          </div>
        </div>

        <div className="form-group">
          <label>Crop History (Comma separated)</label>
          <input 
            type="text" 
            value={cropHistory} 
            onChange={(e) => setCropHistory(e.target.value)} 
            className="form-control"
            placeholder="e.g. Cotton, Groundnut, Wheat"
          />
        </div>

        <button type="submit" className="btn btn-primary btn-glow" disabled={mutation.isPending}>
          <Save size={18} /> {mutation.isPending ? "Saving..." : "Save Farm Configuration"}
        </button>
      </motion.form>

      {user?.role === "admin" && (
        <motion.div 
          className="admin-danger-zone card"
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          style={{ marginTop: "2rem", border: "1px solid var(--orange)", background: "#fffdfa" }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", color: "var(--orange)", marginBottom: "1rem" }}>
            <AlertTriangle size={20} />
            <h2 style={{ fontSize: "1.1rem", margin: 0 }}>Admin Danger Zone</h2>
          </div>
          <p style={{ fontSize: "0.9rem", color: "var(--muted)", marginBottom: "1.5rem" }}>
            As an administrator, you have the ability to purge all data from the database. This action is irreversible and will delete all predictions, feedback, farm records, and historical scans.
          </p>
          <button 
            type="button" 
            className="btn btn-primary" 
            style={{ background: "#b44c3c" }}
            onClick={() => setShowDeleteModal(true)}
          >
            <Trash2 size={16} /> Delete Whole Database
          </button>
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
