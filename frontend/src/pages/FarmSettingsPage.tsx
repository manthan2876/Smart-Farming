import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "../context/AuthContext";
import { request } from "../api/client";
import { MapPin, Save, CheckCircle2, Sprout } from "lucide-react";
import { motion } from "motion/react";
import "../styles/FarmSettingsPage.css";

export default function FarmSettingsPage() {
  const { token } = useAuth();
  const queryClient = useQueryClient();

  const [farmName, setFarmName] = useState("");
  const [location, setLocation] = useState("");
  const [area, setArea] = useState<number>(0);
  const [lat, setLat] = useState<number>(0);
  const [lon, setLon] = useState<number>(0);
  const [cropHistory, setCropHistory] = useState("");
  const [successMessage, setSuccessMessage] = useState(false);

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
    </div>
  );
}
