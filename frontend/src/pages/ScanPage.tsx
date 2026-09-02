import { useQuery } from '@tanstack/react-query';
import { getFarm } from '../api/farm';
﻿import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Upload, Camera, MapPin, Globe, AlertCircle, Loader2 } from "lucide-react";
import { motion } from "motion/react";
import "../styles/ScanPage.css";

export default function ScanPage() {
  const { token, user } = useAuth();
  const navigate = useNavigate();

  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [location, setLocation] = useState(user?.location || "Bhavnagar");
  const [lat, setLat] = useState(user?.latitude?.toString() || "21.7645");
  const [lon, setLon] = useState(user?.longitude?.toString() || "72.1519");
  const [language, setLanguage] = useState("English");
  const [loading, setLoading] = useState(false);
  const [plotId, setPlotId] = useState<number | undefined>(undefined);
  
  const { data: farmData } = useQuery({
    queryKey: ["farm"],
    queryFn: () => getFarm(token!),
    enabled: !!token,
  });
  
  const plots = farmData?.plots || [];
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      if (selected.size > 10 * 1024 * 1024) {
        setError("File size exceeds 10MB limit.");
        return;
      }
      setFile(selected);
      setPreviewUrl(URL.createObjectURL(selected));
      setError(null);
    }
  };

const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError("Please select a leaf image file first.");
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("location", location);
    formData.append("lat", lat);
    formData.append("lon", lon);
    formData.append("language", language);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || "http://localhost:8000"}/predict`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || "Diagnostic pipeline failed.");
      }

      const result = await response.json();
      // Match the backend key 'prediction_id' instead of 'id'
      navigate(`/predictions/${result.prediction_id}`);
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred during analysis.");
      setLoading(false);
    }
  };
  
  return (
    <div className="scan-page">
      <div className="page-header">
        <h1>AI Crop Diagnostic Scanner</h1>
        <p>Upload a clear photograph of an affected crop leaf to run OpenCV quality checks, pest detection, and LLM analysis.</p>
      </div>

      <motion.form 
        onSubmit={handleSubmit} 
        className="scan-form-container"
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
      >
        {error && (
          <div className="alert alert-error">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        <div className="scan-grid">
          {/* File Upload Box */}
          <div className="upload-section">
            <label className={`dropzone ${previewUrl ? "has-preview" : ""}`}>
              {previewUrl ? (
                <div className="preview-container">
                  <img src={previewUrl} alt="Leaf Preview" className="leaf-preview-img" />
                  <div className="replace-overlay">
                    <Camera size={24} />
                    <span>Click or drop to replace image</span>
                  </div>
                </div>
              ) : (
                <div className="dropzone-prompt">
                  <Upload size={48} className="upload-icon" />
                  <h3>Upload Leaf Image</h3>
                  <p>Supports .jpg, .jpeg, .png, .webp (max 10MB)</p>
                  <span className="btn btn-outline btn-sm">Browse Files</span>
                </div>
              )}
              <input type="file" accept="image/*" onChange={handleFileChange} hidden />
            </label>
          </div>

          {/* Telemetry Parameters */}
          <div className="parameters-section">
            <h3>Diagnostic Telemetry</h3>
            
            <div className="form-group">
              <label><MapPin size={16} /> Location Name</label>
              <input 
                type="text" 
                value={location} 
                onChange={(e) => setLocation(e.target.value)} 
                className="form-control"
                required
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Latitude</label>
                <input 
                  type="number" 
                  step="any" 
                  value={lat} 
                  onChange={(e) => setLat(e.target.value)} 
                  className="form-control"
                  required
                />
              </div>
              <div className="form-group">
                <label>Longitude</label>
                <input 
                  type="number" 
                  step="any" 
                  value={lon} 
                  onChange={(e) => setLon(e.target.value)} 
                  className="form-control"
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label><Globe size={16} /> Recommendation Language</label>
              <select 
                value={language} 
                onChange={(e) => setLanguage(e.target.value)} 
                className="form-control"
              >
                <option value="English">English</option>
                <option value="Hindi">Hindi (à¤¹à¤¿à¤‚à¤¦à¥€)</option>
                <option value="Gujarati">Gujarati (àª—à«àªœàª°àª¾àª¤à«€)</option>
              </select>
            </div>

            <button 
              type="submit" 
              className="btn btn-primary btn-full btn-glow" 
              disabled={loading || !file}
            >
              {loading ? (
                <>
                  <Loader2 size={18} className="spinner-icon animate-spin" />
                  <span>Running AI Pipeline...</span>
                </>
              ) : (
                <>Run Diagnostic Analysis</>
              )}
            </button>
          </div>
        </div>
      </motion.form>
    </div>
  );
}
