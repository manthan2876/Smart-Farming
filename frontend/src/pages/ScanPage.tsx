import { useQuery } from '@tanstack/react-query';
import { getFarm } from '../api/farm';
﻿import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Upload, Camera, MapPin, Globe, AlertCircle, Loader2 } from "lucide-react";
import { motion } from "motion/react";
import imageCompression from 'browser-image-compression';
import { get, set, update } from 'idb-keyval';
import { Button, Card, Input } from "../components/ui";
import { request } from "../api/client";
import { translateCrop } from "../i18n/domain";

export default function ScanPage() {
  const { token, user, language: appLanguage, t } = useAuth();
  const navigate = useNavigate();

  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [location, setLocation] = useState(user?.location || "Bhavnagar");
  const [lat, setLat] = useState(user?.latitude?.toString() || "21.7645");
  const [lon, setLon] = useState(user?.longitude?.toString() || "72.1519");
  const [language, setLanguage] = useState(user?.language || appLanguage || "English");
  const [loading, setLoading] = useState(false);
  const [plotId, setPlotId] = useState<number | undefined>(undefined);
  
  const { data: farmData } = useQuery({
    queryKey: ["farm"],
    queryFn: () => getFarm(token!),
    enabled: !!token,
  });
  
  const plots = farmData?.plots || [];
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      if (selected.size > 24 * 1024 * 1024) {
        setError("File size exceeds 24MB limit.");
        return;
      }
      
      try {
        const options = {
          maxSizeMB: 1,
          maxWidthOrHeight: 1080,
          useWebWorker: true,
        };
        const compressedFile = await imageCompression(selected, options);
        setFile(compressedFile);
        setPreviewUrl(URL.createObjectURL(compressedFile));
        setError(null);
      } catch (error) {
        console.error("Image compression error:", error);
        setError("Failed to compress image.");
      }
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

    if (!navigator.onLine) {
      const offlineData = { id: Date.now(), file, location, plotId, lat, lon, language };
      await update('offline_scans', (val: any) => val ? [...val, offlineData] : [offlineData]);
      alert("You are offline. Scan saved locally and will sync when you regain connection.");
      setLoading(false);
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("location", location);
    if (plotId) formData.append("plot_id", plotId.toString());
    formData.append("lat", lat);
    formData.append("lon", lon);
    formData.append("language", language);

    try {
      const result = await request<any>("/predict", { method: "POST", body: formData }, token);
      navigate(`/predictions/${result.prediction_id}/processing`);
    } catch (err: any) {
      if (err.message === "Failed to fetch") {
        const offlineData = { id: Date.now(), file, location, plotId, lat, lon, language };
        await update('offline_scans', (val: any) => val ? [...val, offlineData] : [offlineData]);
        alert("Network error. Scan saved locally and will sync when you regain connection.");
      } else {
        setError(err.message || "An unexpected error occurred during analysis.");
      }
      setLoading(false);
    }
  };

  useEffect(() => {
    const handleOnline = async () => {
      const scans = await get('offline_scans') || [];
      if (scans.length > 0) {
        alert(`Syncing ${scans.length} offline scans...`);
        for (const scan of scans) {
          const formData = new FormData();
          formData.append("file", scan.file);
          formData.append("location", scan.location);
          if (scan.plotId) formData.append("plot_id", scan.plotId.toString());
          formData.append("lat", scan.lat);
          formData.append("lon", scan.lon);
          formData.append("language", scan.language);
          try {
            await request<any>("/predict", { method: "POST", body: formData }, token);
          } catch (e) {
            console.error("Failed to sync offline scan", e);
          }
        }
        await set('offline_scans', []);
        alert("Offline scans synchronized successfully!");
        navigate("/history");
      }
    };
    window.addEventListener('online', handleOnline);
    return () => window.removeEventListener('online', handleOnline);
  }, [token, navigate]);
  
  return (
    <div className="space-y-6 pb-12">
      <div>
        <h1 className="font-display text-3xl text-ink sm:text-4xl">{t("aiCropScanner")}</h1>
        <p className="mt-3 max-w-3xl leading-7 text-muted">{t("scanDescription")}</p>
      </div>

      <motion.form 
        onSubmit={handleSubmit} 
        className="space-y-5"
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
      >
        {error && (
          <div className="flex items-center gap-3 rounded-sm border border-red-100 bg-red-50 p-4 text-sm text-danger">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        <div className="grid gap-5 lg:grid-cols-[1.15fr_0.85fr]">
          {/* File Upload Box */}
          <Card padding="md">
            <label className={`flex min-h-[25rem] cursor-pointer items-center justify-center overflow-hidden rounded-md border-2 border-dashed border-farmer-700 bg-farmer-50 text-center transition hover:border-farmer-500 hover:bg-farmer-100 ${previewUrl ? "p-0" : "p-8"}`}>
              {previewUrl ? (
                <div className="group relative h-full min-h-[25rem] w-full">
                  <img src={previewUrl} alt="Leaf Preview" className="h-full min-h-[25rem] w-full object-contain" />
                  <div className="absolute inset-0 flex flex-col items-center justify-center bg-ink/55 text-white opacity-0 transition group-hover:opacity-100">
                    <Camera size={24} />
                    <span className="mt-2 text-sm font-semibold">{t("replaceImage")}</span>
                  </div>
                </div>
              ) : (
                <div>
                  <Upload size={48} className="mx-auto text-farmer-700" />
                  <h3 className="mt-5 font-display text-xl text-ink">{t("uploadLeafImage")}</h3>
                  <p className="mt-2 text-sm text-muted">{t("supportedFormats")}</p>
                  <span className="mt-5 inline-flex rounded-sm border border-farmer-700 px-4 py-2 text-sm font-semibold text-farmer-800">{t("browseFiles")}</span>
                </div>
              )}
              <input type="file" accept="image/*" onChange={handleFileChange} hidden />
            </label>
          </Card>

          {/* Telemetry Parameters */}
          <Card className="!border-farmer-900 !bg-farmer-900 text-white" padding="lg">
            <h3 className="font-display text-2xl text-farmer-200">{t("diagnosticTelemetry")}</h3>
            
            <div className="mt-7 space-y-5">
              <label className="block space-y-2" htmlFor="scan-plot">
                <span className="block text-sm font-semibold text-white/75">{t("farm")} / {t("plotOptional")}</span>
              <select 
                id="scan-plot"
                value={plotId || ""} 
                onChange={(e) => setPlotId(e.target.value ? Number(e.target.value) : undefined)} 
                className="min-h-11 w-full rounded-sm border border-white/20 bg-white/10 px-3 text-sm text-white focus:border-farmer-300 focus:outline-none focus:ring-4 focus:ring-farmer-300/20"
              >
                <option value="">{t("noPlotGeneralScan")}</option>
                {plots.map((p: any) => (
                  <option key={p.id} value={p.id}>{p.name} {p.crop ? `(${translateCrop(p.crop, appLanguage)})` : ""}</option>
                ))}
              </select>
              </label>

            <Input label={t("location")} leadingIcon={<MapPin size={16} />} 
                type="text" 
                value={location} 
                onChange={(e) => setLocation(e.target.value)} 
                className="border-white/20 bg-white/10 text-white placeholder:text-white/50 focus:border-farmer-300 focus:ring-farmer-300/20"
                required
              />

            <div className="grid gap-5 sm:grid-cols-2">
              <Input label={t("latitude")} type="number" step="any" value={lat} onChange={(e) => setLat(e.target.value)} className="border-white/20 bg-white/10 text-white focus:border-farmer-300 focus:ring-farmer-300/20" required />
              <Input label={t("longitude")} type="number" step="any" value={lon} onChange={(e) => setLon(e.target.value)} className="border-white/20 bg-white/10 text-white focus:border-farmer-300 focus:ring-farmer-300/20" required />
            </div>

            <label className="block space-y-2" htmlFor="scan-language">
              <span className="flex items-center gap-2 text-sm font-semibold text-white/75"><Globe size={16} /> {t("recommendationLanguage")}</span>
              <select 
                id="scan-language"
                value={language} 
                onChange={(e) => setLanguage(e.target.value)} 
                className="min-h-11 w-full rounded-sm border border-white/20 bg-white/10 px-3 text-sm text-white focus:border-farmer-300 focus:outline-none focus:ring-4 focus:ring-farmer-300/20"
              >
                <option value="English">English</option>
                <option value="Hindi">हिन्दी (Hindi)</option>
                <option value="Gujarati">ગુજરાતી (Gujarati)</option>
              </select>
            </label>

            <Button 
              type="submit" 
              className="mt-2 w-full bg-farmer-300 text-ink hover:bg-farmer-200" 
              disabled={loading || !file}
            >
              {loading ? (
                <>
                  <Loader2 size={18} className="spinner-icon animate-spin" />
                  <span>{t("runningAiPipeline")}</span>
                </>
              ) : (
                <>{t("runDiagnostic")}</>
              )}
            </Button>
            </div>
          </Card>
        </div>
      </motion.form>
    </div>
  );
}
