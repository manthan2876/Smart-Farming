import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { request } from "../api/client";
import { exportDataset } from "../api/admin";
import { 
  AlertTriangle, 
  Trash2, 
  DownloadCloud, 
  Settings as SettingsIcon,
  Globe,
  Sliders,
  CheckCircle2,
  Database,
  Cloud,
  Sprout,
  FolderArchive,
  Sun
} from "lucide-react";
import { motion } from "motion/react";
import { Button, Card, Input, Select } from "../components/ui";
import ThemeToggle from "../components/ThemeToggle";

export default function SettingsPage() {
  const { user, token, language, units, setLanguage, setUnits, t } = useAuth();
  const queryClient = useQueryClient();
  const isAdmin = user?.role === "admin";
  
  // General
  const [lang, setLang] = useState(language);
  const [unitPref, setUnitPref] = useState(units);
  const [prefSaved, setPrefSaved] = useState(false);

  // Danger Zone
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteConfirmText, setDeleteConfirmText] = useState("");
  const [isDeleting, setIsDeleting] = useState(false);

  // MLOps
  const [exportFilters, setExportFilters] = useState({ expert: true, farmer: true });
  const [exportCrop, setExportCrop] = useState("All Crops (Tomato, Cotton, Potato)");
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
      await request("/admin/purge?confirmation=DELETE", {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ confirmation: "DELETE" }),
      }, token!);
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
      const localCount = res.local_deleted ?? 0;
      const s3Count = res.s3_deleted ?? 0;
      alert(`Success! Deleted ${res.deleted_files ?? (localCount + s3Count)} orphaned files (Local: ${localCount}, S3: ${s3Count}).`);
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
      const blob = await exportDataset(token!, {
        filters: { expert: exportFilters.expert, farmer: exportFilters.farmer, crop: exportCrop },
        split: payload.split,
        format: exportFormat === "JSON Manifest" ? "JSON Manifest" : "PyTorch Folder",
        imageTarget: exportImage as "raw" | "preprocessed",
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "dataset_export.zip";
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
      alert("Export error.");
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="space-y-6 pb-12">
      <div>
        <h1 className="flex items-center gap-3 font-display text-3xl text-ink sm:text-4xl"><SettingsIcon size={28} className="text-farmer-700" /> {t("settings")}</h1>
        <p className="mt-3 max-w-3xl leading-7 text-muted">{t("settingsSubtitle")}</p>
      </div>

      <Card>
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h3 className="flex items-center gap-2 font-display text-xl text-ink">
              <Sun size={20} className="text-farmer-700" />
              <span>Appearance & Theme</span>
            </h3>
            <p className="mt-2 text-sm text-muted">
              Choose between light, dark, or automatic system theme.
            </p>
          </div>
          <ThemeToggle variant="segmented" />
        </div>
      </Card>

      <Card>
        <h3 className="flex items-center gap-2 font-display text-xl text-ink"><Globe size={20} className="text-farmer-700" /> {t("languagePreferences")}</h3>
        <p className="mt-2 text-sm text-muted">{t("languageSubtitle")}</p>
        
        <div className="mt-6 grid gap-5 sm:grid-cols-2">
          <div className="space-y-2">
            <label className="flex items-center gap-2 text-sm font-semibold text-ink" htmlFor="settings-language">
              <Globe size={15} className="text-farmer-700" />
              <span>{t("interfaceLanguage")}</span>
            </label>
            <Select 
              id="settings-language"
              value={lang} 
              onChange={(val) => setLang(val as any)}
              options={[
                { value: "English", label: "English" },
                { value: "Gujarati", label: "ગુજરાતી (Gujarati)" },
                { value: "Hindi", label: "हिन्दी (Hindi)" },
              ]}
            />
          </div>
          <div className="space-y-2">
            <label className="flex items-center gap-2 text-sm font-semibold text-ink" htmlFor="settings-units">
              <Sliders size={15} className="text-farmer-700" />
              <span>{t("units")}</span>
            </label>
            <Select 
              id="settings-units"
              value={unitPref} 
              onChange={(val) => setUnitPref(val as any)}
              options={[
                { value: "Metric", label: "Metric (ha, °C, km/h)" },
                { value: "Imperial", label: "Imperial (acres, °F, mph)" },
              ]}
            />
          </div>
        </div>

        <div className="mt-6 flex items-center gap-3">
          <Button 
            onClick={async () => {
              await setLanguage(lang as any);
              setUnits(unitPref as any);
              setPrefSaved(true);
              setTimeout(() => setPrefSaved(false), 3000);
            }}
          >
            {t("save")}
          </Button>
          {prefSaved && <span className="inline-flex items-center gap-1 text-sm font-semibold text-farmer-700"><CheckCircle2 size={16} /> {t("savedSuccess")}</span>}
        </div>
      </Card>

      {isAdmin && (
        <>
          <motion.div className="rounded-md border border-line border-t-4 border-t-expert-500 bg-surface p-5 shadow-soft sm:p-6" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <h3 className="flex items-center gap-2 font-display text-xl text-ink"><Database size={20} className="text-expert-500" /> {t("mlopsEngine")}</h3>
            <p className="mt-2 text-sm text-muted">{t("mlopsSubtitle")}</p>
            
            <div className="mt-6 rounded-sm bg-canvas p-4">
              <strong className="text-sm text-ink">{t("groundTruthInclusion")}</strong>
              <div className="mt-3 flex flex-col gap-3 text-sm text-muted sm:flex-row sm:gap-6">
                <label className="flex items-center gap-2">
                  <input type="checkbox" checked={exportFilters.expert} onChange={e => setExportFilters(p => ({...p, expert: e.target.checked}))} />
                  {t("expertOverriddenCases")} ({datasetSummary?.expert_overridden || 0})
                </label>
                <label className="flex items-center gap-2">
                  <input type="checkbox" checked={exportFilters.farmer} onChange={e => setExportFilters(p => ({...p, farmer: e.target.checked}))} />
                  {t("confirmedFarmerFeedback")} ({datasetSummary?.farmer_confirmed || 0})
                </label>
              </div>
            </div>

            <div className="mt-6 grid gap-5 sm:grid-cols-2">
              <div className="space-y-2">
                <label className="flex items-center gap-2 text-sm font-semibold text-ink" htmlFor="export-crop">
                  <Sprout size={15} className="text-expert-700" />
                  <span>{t("targetCrop")}</span>
                </label>
                <Select 
                  id="export-crop"
                  value={exportCrop} 
                  onChange={(val) => setExportCrop(val)}
                  theme="expert"
                  options={[
                    { value: "All Crops (Tomato, Cotton, Potato)", label: "All Crops (Tomato, Cotton, Potato)" },
                    { value: "Cotton", label: "Cotton", icon: <Sprout size={14} className="text-expert-600 shrink-0" /> },
                    { value: "Tomato", label: "Tomato", icon: <Sprout size={14} className="text-expert-600 shrink-0" /> },
                  ]}
                />
              </div>
              <div className="space-y-2">
                <label className="flex items-center gap-2 text-sm font-semibold text-ink" htmlFor="export-format">
                  <FolderArchive size={15} className="text-expert-700" />
                  <span>{t("archiveFormat")}</span>
                </label>
                <Select 
                  id="export-format"
                  value={exportFormat} 
                  onChange={(val) => setExportFormat(val)}
                  theme="expert"
                  options={[
                    { value: "PyTorch Folder", label: "PyTorch Folder", sublabel: "Class-based folder structure" },
                    { value: "COCO Bounding Boxes", label: "COCO Bounding Boxes", sublabel: "instances.json format" },
                    { value: "JSON Manifest", label: "JSON Manifest", sublabel: "Full telemetry & predictions" },
                  ]}
                />
              </div>
            </div>

            <div className="mt-6">
              <label className="text-sm font-semibold text-ink">{t("imageTarget")}</label>
              <div className="mt-3 flex flex-col gap-3 text-sm text-muted sm:flex-row sm:gap-6">
                <label className="flex items-center gap-2">
                  <input type="radio" name="imgTarget" checked={exportImage === "preprocessed"} onChange={() => setExportImage("preprocessed")} />
                  {t("preprocessedImg")}
                </label>
                <label className="flex items-center gap-2">
                  <input type="radio" name="imgTarget" checked={exportImage === "raw"} onChange={() => setExportImage("raw")} />
                  {t("rawImg")}
                </label>
              </div>
            </div>

            <div className="mt-6">
              <label className="text-sm font-semibold text-ink">Dataset Split: Train {splitTrain}% / Val {splitVal}% / Test {100 - splitTrain - splitVal}%</label>
              <input className="mt-4 w-full accent-farmer-700" type="range" min="50" max="90" value={splitTrain} onChange={e => setSplitTrain(Number(e.target.value))} />
            </div>

            <div className="mt-7 flex flex-wrap gap-3">
              <Button className="bg-expert-700 hover:bg-expert-500" onClick={handleExportMLOps} disabled={isExporting}>
                <DownloadCloud size={18} /> {isExporting ? t("packaging") : t("exportArchive")}
              </Button>
              <Button variant="secondary" className="border-expert-500 text-expert-700" disabled={isExporting}>
                <Cloud size={18} /> {t("syncS3")}
              </Button>
            </div>
          </motion.div>

          <motion.div className="rounded-md border border-line bg-surface p-5 shadow-soft sm:p-6" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <h3 className="flex items-center gap-2 font-display text-xl text-ink"><Sliders size={20} className="text-farmer-700" /> {t("decisionThresholds")}</h3>
            <p className="mt-2 text-sm text-muted">{t("thresholdsSubtitle")}</p>
            
            <div className="mt-6">
              <label className="text-sm font-semibold text-ink">{t("cropRoutingConfMin")}: {routingThresh}%</label>
              <input className="mt-3 w-full accent-farmer-700" type="range" min="50" max="95" value={routingThresh} onChange={e => setRoutingThresh(Number(e.target.value))} />
            </div>
            
            <div className="mt-6">
              <label className="text-sm font-semibold text-ink">{t("expertEscalationCutoff")}: {expertThresh}%</label>
              <input className="mt-3 w-full accent-farmer-700" type="range" min="50" max="95" value={expertThresh} onChange={e => setExpertThresh(Number(e.target.value))} />
            </div>

            <Button className="mt-7" onClick={() => updateConfig.mutate()} disabled={updateConfig.isPending}>
              {updateConfig.isPending ? t("saving") : t("saveConfigParams")}
            </Button>
            {configSaved && <span className="ml-4 inline-flex items-center gap-1 text-sm font-semibold text-farmer-700"><CheckCircle2 size={16} /> {t("saved")}</span>}
          </motion.div>

          <motion.div className="rounded-md border border-red-200 bg-red-50 dark:border-red-900/60 dark:bg-red-950/30 p-5 shadow-soft sm:p-6" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <h3 className="flex items-center gap-2 font-display text-xl text-danger dark:text-red-400"><AlertTriangle size={20} /> {t("dangerZone")}</h3>
            
            <div className="mt-6 flex flex-wrap gap-3">
              <Button type="button" variant="danger" onClick={() => setShowDeleteModal(true)}>
                <Trash2 size={16} /> {t("clearPredictions")}
              </Button>
              <Button type="button" variant="secondary" className="border-danger text-danger dark:border-red-500 dark:text-red-400" onClick={handlePurgeBlobs}>
                <Trash2 size={16} /> {t("purgeBlobs")}
              </Button>
            </div>
          </motion.div>
        </>
      )}

      {showDeleteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
          <div className="w-full max-w-md rounded-md bg-surface p-6 shadow-lift">
            <h3 className="font-display text-xl text-danger">{t("confirmPurge")}</h3>
            <p className="mt-2 text-sm text-muted">{t("typeDeleteBelow")}</p>
            <Input id="delete-confirmation" className="mt-4" value={deleteConfirmText} onChange={(e) => setDeleteConfirmText(e.target.value)} placeholder="DELETE" />
            <div className="mt-6 flex justify-end gap-3">
              <Button variant="secondary" onClick={() => setShowDeleteModal(false)}>{t("cancel")}</Button>
              <Button variant="danger" disabled={deleteConfirmText !== "DELETE" || isDeleting} onClick={handleDeleteData}>
                {t("confirmDelete")}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
