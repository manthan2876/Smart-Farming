import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
  adminMetrics,
  datasetSummary as getDatasetSummary,
  modelHealth as getModelHealth,
  exportDataset,
  getMlopsRuns,
} from "../api/admin";
import { useAuth } from "../context/AuthContext";
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell
} from "recharts";
import { Loader2, Download, Filter, Sprout, Image, FileText, Database, History, Activity, ShieldCheck } from "../components/icons";
import { Card, Button, Select, Skeleton } from "../components/ui";
import { translateCrop, translateDisease } from "../i18n/domain";

const COLORS = ['#284b35', '#4d6f3d', '#8f6520', '#9e382b', '#6b7280'];
const CROP_OPTIONS = ["All Crops", "Tomato", "Cotton", "Groundnut", "Pepper Bell", "Potato"];
const STATUS_OPTIONS = ["Any", "pending_review", "added_to_dataset", "rejected"];

export default function AdminMetricsPage() {
  const { token, t, language } = useAuth();
  const queryClient = useQueryClient();

  // MLOps UI tab state: summary | export | history
  const [mlopsTab, setMlopsTab] = useState<"summary" | "export" | "history">("summary");

  // Export filter state
  const [exportCrop, setExportCrop] = useState("All Crops");
  const [exportStatus, setExportStatus] = useState("Any");
  const [exportImageTarget, setExportImageTarget] = useState<"preprocessed" | "raw">("preprocessed");
  const [exportFormat, setExportFormat] = useState<"PyTorch Folder" | "JSON Manifest">("PyTorch Folder");
  const [exportTrain, setExportTrain] = useState(70);
  const [exportVal, setExportVal] = useState(15);
  const [exportTest, setExportTest] = useState(15);
  const [exporting, setExporting] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ["admin_metrics"],
    queryFn: () => adminMetrics(token!),
    enabled: !!token
  });

  const { data: datasetSummary, isError: datasetSummaryError } = useQuery({
    queryKey: ["dataset_summary"],
    queryFn: () => getDatasetSummary(token!),
    enabled: !!token,
  });

  const { data: modelHealth } = useQuery({
    queryKey: ["model_health"],
    queryFn: () => getModelHealth(token!),
    enabled: !!token,
    staleTime: 60_000,
  });

  const { data: mlopsRunsData } = useQuery({
    queryKey: ["mlops_runs"],
    queryFn: () => getMlopsRuns(token!),
    enabled: !!token,
    staleTime: 30_000,
  });

  const handleExportMLOps = async () => {
    if (exportTrain + exportVal + exportTest !== 100) {
      alert(t("adminSplitPercentagesTotal"));
      return;
    }
    setExporting(true);
    try {
      const blob = await exportDataset(token!, {
        filters: {
          expert: true,
          farmer: true,
          crop: exportCrop === "All Crops" ? undefined : exportCrop,
          status: exportStatus === "Any" ? "all" : exportStatus as "added_to_dataset" | "pending_review" | "rejected",
        },
        split: { train: exportTrain, val: exportVal, test: exportTest },
        format: exportFormat,
        imageTarget: exportImageTarget,
      });

      // Invalidate audit history so the export appears in the History tab immediately
      queryClient.invalidateQueries({ queryKey: ["mlops_runs"] });

      // If backend uploaded to Supabase/S3, it returns a JSON payload with signed download_url
      if (blob.type.includes("json")) {
        const text = await blob.text();
        try {
          const json = JSON.parse(text);
          if (json.download_url) {
            const a = document.createElement("a");
            a.href = json.download_url;
            a.download = `dataset_export_${json.export_id || "bundle"}.zip`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            return;
          }
        } catch {
          // Fall through to regular blob handling
        }
      }

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "dataset_export.zip";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (e: any) {
      console.error("Dataset export failed:", e);
      const msg = typeof e?.message === "string" ? e.message : (typeof e?.detail === "string" ? e.detail : t("adminExportFailed"));
      alert(msg);
    } finally {
      setExporting(false);
    }
  };

  if (isLoading) return <div className="flex min-h-[40vh] items-center justify-center"><Loader2 className="animate-spin text-admin-500 dark:text-amber-400" /></div>;
  if (!data) return <div className="rounded-md border border-red-100 bg-red-50 p-6 text-danger dark:border-red-900/60 dark:bg-red-950/40 dark:text-red-300">{t("adminMetricsLoadFailed")}</div>;

  const localizedDiseaseDist = (data?.disease_distribution || []).map((entry: any) => ({
    ...entry,
    name: translateDisease(entry.name, language),
  }));

  const localizedConfidenceHist = (data?.confidence_histogram || []).map((entry: any) => ({
    ...entry,
    name: entry.name?.includes("High")
      ? `${t("highConfidence")} (>75%)`
      : entry.name?.includes("Medium")
      ? `${t("moderate")} (50-75%)`
      : `${t("low")} (<50%)`,
  }));

  const modelNameMap: Record<string, string> = {
    crop_identifier: t("cropIdentifier"),
    cotton_disease: t("cottonDisease"),
    groundnut_disease: t("groundnutDisease"),
    pepper_bell_disease: t("pepperBellDisease"),
    potato_disease: t("potatoDisease"),
    tomato_disease: t("tomatoDisease"),
    pest_classifier: t("pestClassifier"),
  };

  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="font-display text-3xl text-ink sm:text-4xl">{t("metricsMlops")}</h1>
          <p className="mt-2 text-sm text-muted">{t("systemMetricsSubtitle")}</p>
        </div>
      </div>

      {/* ── Key metrics row 1 ── */}
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <h3 className="text-xs font-bold uppercase tracking-wide text-muted">{t("totalUsers")}</h3>
          <div className="mt-3 font-display text-3xl text-ink">{data.total_users}</div>
        </Card>
        <Card>
          <h3 className="text-xs font-bold uppercase tracking-wide text-muted">{t("totalScans")}</h3>
          <div className="mt-3 font-display text-3xl text-ink">{data.total_scans}</div>
          <p className="mt-1 text-xs text-muted">{data.completed_scans || 0} {t("completed")}</p>
        </Card>
        <Card>
          <h3 className="text-xs font-bold uppercase tracking-wide text-muted">{t("activeQueueDepth")}</h3>
          <div className={`mt-3 font-display text-3xl ${(data.queue_depth || 0) > 5 ? "text-amber-600" : "text-ink"}`}>{data.queue_depth || 0}</div>
          <p className="mt-1 text-xs text-muted">{t("predictionsProcessing")}</p>
        </Card>
        <Card>
          <h3 className="text-xs font-bold uppercase tracking-wide text-muted">{t("pipelineLatency")}</h3>
          <div className="mt-3 font-display text-3xl text-ink">{data.processing_duration?.avg_ms || 0}<span className="text-sm font-normal text-muted"> {t("avgLatency")}</span></div>
          <p className="mt-1 text-xs text-muted">P95: {data.processing_duration?.p95_ms || 0} ms</p>
        </Card>
      </div>

      {/* ── Key metrics row 2 ── */}
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <h3 className="text-xs font-bold uppercase tracking-wide text-muted">{t("farmerFieldAccuracy")}</h3>
          <div className={`mt-3 font-display text-3xl ${data.accuracy > 85 ? "text-farmer-700 dark:text-emerald-400" : "text-danger dark:text-rose-400"}`}>
            {typeof data.accuracy === "number" ? data.accuracy.toFixed(1) : data.accuracy}%
          </div>
          <p className="mt-1 text-xs text-muted">{t("farmerFieldValidationSignals")}</p>
        </Card>
        <Card>
          <h3 className="text-xs font-bold uppercase tracking-wide text-muted">{t("specialistValidatedAccuracy")}</h3>
          <div className="mt-3 font-display text-3xl text-expert-700 dark:text-cyan-400">
            {data.expert_metrics?.validated_accuracy != null ? `${data.expert_metrics.validated_accuracy}%` : t("pendingData")}
          </div>
          <p className="mt-1 text-xs text-muted">{data.expert_metrics?.overrides || 0} {t("agronomistOverrides")}</p>
        </Card>
        <Card>
          <h3 className="text-xs font-bold uppercase tracking-wide text-muted">{t("pipelineFailureRate")}</h3>
          <div className={`mt-3 font-display text-3xl ${(data.failures?.failure_rate || 0) > 5 ? "text-danger dark:text-rose-400" : "text-farmer-700 dark:text-emerald-400"}`}>
            {data.failures?.failure_rate !== undefined ? `${data.failures.failure_rate.toFixed(1)}%` : "0.0%"}
          </div>
          <p className="mt-1 text-xs text-muted">{data.failures?.total_failed || 0} {t("failedScans")}</p>
        </Card>
        <Card>
          <h3 className="text-xs font-bold uppercase tracking-wide text-muted">{t("degradedFallbackSignals")}</h3>
          <div className="mt-3 font-display text-3xl text-amber-600 dark:text-amber-400">
            {(data.fallbacks?.recommendation_fallbacks || 0) + (data.fallbacks?.weather_fallbacks || 0)}
          </div>
          <p className="mt-1 text-xs text-muted">{data.fallbacks?.recommendation_fallbacks || 0} {t("aiFallbacks")}, {data.fallbacks?.weather_fallbacks || 0} {t("weatherOffline")}</p>
        </Card>
      </div>

      {/* ── Drift & Retraining row ── */}
      {data.drift && (
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <Card>
            <h3 className="text-xs font-bold uppercase tracking-wide text-muted">{t("avgConfidence7d")}</h3>
            <div className={`mt-3 font-display text-3xl ${(data.drift.avg_disease_confidence_7d || 1) < 0.7 ? "text-amber-600 dark:text-amber-400" : "text-farmer-700 dark:text-emerald-400"}`}>
              {data.drift.avg_disease_confidence_7d != null ? `${(data.drift.avg_disease_confidence_7d * 100).toFixed(1)}%` : "N/A"}
            </div>
            <p className="mt-1 text-xs text-muted">{t("avg30d")} {data.drift.avg_disease_confidence_30d != null ? `${(data.drift.avg_disease_confidence_30d * 100).toFixed(1)}%` : "N/A"}</p>
          </Card>
          <Card>
            <h3 className="text-xs font-bold uppercase tracking-wide text-muted">{t("lowConfidenceRate7d")}</h3>
            <div className={`mt-3 font-display text-3xl ${(data.drift.low_confidence_rate_7d || 0) > 20 ? "text-danger dark:text-rose-400" : "text-ink"}`}>
              {data.drift.low_confidence_rate_7d != null ? `${data.drift.low_confidence_rate_7d.toFixed(1)}%` : "N/A"}
            </div>
            <p className="mt-1 text-xs text-muted">{t("predictionsBelowThreshold")}</p>
          </Card>
          <Card>
            <h3 className="text-xs font-bold uppercase tracking-wide text-muted">{t("retrainingCandidates")}</h3>
            <div className={`mt-3 font-display text-3xl ${(data.drift.retraining_candidates || 0) > 50 ? "text-amber-600 dark:text-amber-400" : "text-ink"}`}>
              {data.drift.retraining_candidates ?? 0}
            </div>
            <p className="mt-1 text-xs text-muted">{t("pendingDatasetCandidates")}</p>
          </Card>
          <Card>
            <h3 className="text-xs font-bold uppercase tracking-wide text-muted">{t("expertCorrectionRate")}</h3>
            <div className={`mt-3 font-display text-3xl ${(data.drift.expert_correction_rate || 0) > 30 ? "text-danger dark:text-rose-400" : "text-farmer-700 dark:text-emerald-400"}`}>
              {data.drift.expert_correction_rate != null ? `${data.drift.expert_correction_rate.toFixed(1)}%` : "N/A"}
            </div>
            <p className="mt-1 text-xs text-muted">{t("reviewsCorrections")}</p>
          </Card>
        </div>
      )}

      {/* ── Charts ── */}
      <div className="grid gap-5 lg:grid-cols-2">
        <Card>
          <h3 className="font-display text-xl text-ink">{t("diseaseDistribution")}</h3>
          <div className="mt-5 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={localizedDiseaseDist} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label>
                  {localizedDiseaseDist.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card>
          <h3 className="font-display text-xl text-ink">{t("aiConfidenceHistogram")}</h3>
          <div className="mt-5 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={localizedConfidenceHist}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#52772d" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* ── Model Health Panel ── */}
      {modelHealth && (
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-display text-xl text-ink">{t("modelRegistryHealth")}</h3>
              <p className="mt-1 text-sm text-muted">
                {modelHealth.overall_status === "healthy"
                  ? t("allModelsLoaded")
                  : t("someModelsMissing")}
              </p>
            </div>
            <span className={`rounded-xs px-2.5 py-0.5 text-xs font-semibold border ${
              modelHealth.overall_status === "healthy"
                ? "bg-farmer-100 text-farmer-800 border-farmer-300 dark:bg-farmer-900/60 dark:text-farmer-200 dark:border-farmer-700"
                : "bg-amber-50 text-amber-900 border-amber-300 dark:bg-amber-950/40 dark:text-amber-200 dark:border-amber-800"
            }`}>
              {modelHealth.overall_status === "healthy" ? t("healthy") : modelHealth.overall_status}
            </span>
          </div>
          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-line text-left text-xs font-semibold uppercase tracking-wide text-muted">
                  <th className="pb-2 pr-4">{t("model")}</th>
                  <th className="pb-2 pr-4">{t("version")}</th>
                  <th className="pb-2 pr-4">{t("status")}</th>
                  <th className="pb-2 pr-4">{t("valAcc")}</th>
                  <th className="pb-2">{t("testAcc")}</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(modelHealth.models as Record<string, any>).map(([key, m]) => (
                  <tr key={key} className="border-b border-line last:border-0">
                    <td className="py-2 pr-4 font-medium text-ink">{modelNameMap[key] || key.replace(/_/g, " ")}</td>
                    <td className="py-2 pr-4 text-muted">{m.active_version ?? "N/A"}</td>
                    <td className="py-2 pr-4">
                      <span className={`inline-flex items-center rounded-xs px-2 py-0.5 text-xs font-medium border ${
                        m.status === "ok" ? "bg-farmer-100 text-farmer-800 border-farmer-300 dark:bg-farmer-900/60 dark:text-farmer-200 dark:border-farmer-700" : "bg-red-50 text-red-900 border-red-300 dark:bg-red-950/40 dark:text-red-200 dark:border-red-800"
                      }`}>
                        {m.status === "ok" ? t("modelReady") : t("modelMissing")}
                      </span>
                    </td>
                    <td className="py-2 pr-4 text-muted">{m.val_acc != null ? `${(m.val_acc * 100).toFixed(1)}%` : "N/A"}</td>
                    <td className="py-2 text-muted">{m.test_acc != null ? `${(m.test_acc * 100).toFixed(1)}%` : "N/A"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* ── Dataset Curation & MLOps Engine ── */}
      <Card>
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-line pb-4">
          <div>
            <h3 className="flex items-center gap-2 font-display text-xl text-ink">
              <Database size={20} className="text-admin-600 dark:text-amber-400" />
              {t("mlopsDatasetExport")}
            </h3>
            <p className="mt-1 text-sm text-muted">
              {datasetSummary
                ? `${datasetSummary.total} ${t("totalCandidates")} · ${datasetSummary.by_status?.pending_review ?? 0} ${t("pendingReview")}`
                : datasetSummaryError
                ? t("datasetSummaryUnavailable")
                : t("loadingSummary")}
            </p>
          </div>

          {/* MLOps Tabs */}
          <div className="flex rounded-md border border-line bg-canvas p-1 text-xs font-semibold">
            <button
              type="button"
              onClick={() => setMlopsTab("summary")}
              className={`flex items-center gap-1.5 rounded-sm px-3 py-1.5 transition-colors ${
                mlopsTab === "summary"
                  ? "bg-surface text-ink shadow-sm"
                  : "text-muted hover:text-ink"
              }`}
            >
              <Activity size={14} />
              <span>{t("candidateSummaryTab")}</span>
              {datasetSummary && (
                <span className="ml-1 rounded-full bg-admin-100 px-1.5 py-0.5 text-[10px] font-bold text-admin-800 dark:bg-amber-950/60 dark:text-amber-300">
                  {datasetSummary.total}
                </span>
              )}
            </button>
            <button
              type="button"
              onClick={() => setMlopsTab("export")}
              className={`flex items-center gap-1.5 rounded-sm px-3 py-1.5 transition-colors ${
                mlopsTab === "export"
                  ? "bg-surface text-ink shadow-sm"
                  : "text-muted hover:text-ink"
              }`}
            >
              <Download size={14} />
              <span>{t("datasetExportTab")}</span>
            </button>
            <button
              type="button"
              onClick={() => setMlopsTab("history")}
              className={`flex items-center gap-1.5 rounded-sm px-3 py-1.5 transition-colors ${
                mlopsTab === "history"
                  ? "bg-surface text-ink shadow-sm"
                  : "text-muted hover:text-ink"
              }`}
            >
              <History size={14} />
              <span>{t("exportHistoryTab")}</span>
              {mlopsRunsData?.runs && mlopsRunsData.runs.length > 0 && (
                <span className="ml-1 rounded-full bg-line px-1.5 py-0.5 text-[10px] font-bold text-muted">
                  {mlopsRunsData.runs.length}
                </span>
              )}
            </button>
          </div>
        </div>

        {/* ── TAB 1: Candidate Summary ── */}
        {mlopsTab === "summary" && (
          <div className="mt-5 space-y-5">
            {/* 4 Stat Cards */}
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <div className="rounded-sm border border-line bg-canvas p-4">
                <span className="text-xs font-semibold uppercase tracking-wide text-muted">{t("totalCandidates")}</span>
                <div className="mt-2 font-display text-2xl text-ink">{datasetSummary?.total ?? 0}</div>
                <p className="mt-1 text-xs text-muted">{t("vettedAgriculturalScans")}</p>
              </div>

              <div className="rounded-sm border border-line bg-canvas p-4">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold uppercase tracking-wide text-muted">{t("pendingReview")}</span>
                  <span className="rounded-xs bg-amber-50 px-2 py-0.5 text-[10px] font-bold text-amber-800 border border-amber-300 dark:bg-amber-950/60 dark:text-amber-200 dark:border-amber-700">
                    {t("awaitingAgronomist")}
                  </span>
                </div>
                <div className="mt-2 font-display text-2xl text-amber-600 dark:text-amber-400">
                  {datasetSummary?.by_status?.pending_review ?? 0}
                </div>
                <p className="mt-1 text-xs text-muted">{t("pendingDatasetCandidates")}</p>
              </div>

              <div className="rounded-sm border border-line bg-canvas p-4">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold uppercase tracking-wide text-muted">{t("addedToDataset")}</span>
                  <span className="rounded-xs bg-farmer-50 px-2 py-0.5 text-[10px] font-bold text-farmer-800 border border-farmer-300 dark:bg-farmer-950/60 dark:text-farmer-200 dark:border-farmer-700">
                    {t("approvedForRetraining")}
                  </span>
                </div>
                <div className="mt-2 font-display text-2xl text-farmer-700 dark:text-emerald-400">
                  {datasetSummary?.by_status?.added_to_dataset ?? 0}
                </div>
                <p className="mt-1 text-xs text-muted">{t("readyForFineTuning")}</p>
              </div>

              <div className="rounded-sm border border-line bg-canvas p-4">
                <span className="text-xs font-semibold uppercase tracking-wide text-muted">{t("groundTruthSources")}</span>
                <div className="mt-2 text-sm font-semibold text-ink">
                  {datasetSummary?.expert_overridden ?? 0} {t("expertOverriddenCases")}
                </div>
                <div className="mt-1 text-xs text-muted">
                  {datasetSummary?.farmer_confirmed ?? 0} {t("confirmedFarmerFeedback")}
                </div>
              </div>
            </div>

            {/* Crop Distribution Breakdown */}
            <div className="rounded-sm border border-line bg-canvas p-5">
              <div className="flex items-center justify-between border-b border-line pb-3">
                <h4 className="flex items-center gap-2 text-sm font-bold text-ink">
                  <Sprout size={16} className="text-admin-600 dark:text-amber-400" />
                  {t("cropDistributionBreakdown")}
                </h4>
                <Button size="sm" variant="secondary" onClick={() => setMlopsTab("export")} className="text-xs">
                  {t("configureAndExport")} →
                </Button>
              </div>

              {(!datasetSummary?.by_crop || datasetSummary.by_crop.length === 0) ? (
                <p className="py-6 text-center text-sm text-muted">
                  {t("noCandidatesLogged")}
                </p>
              ) : (
                <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                  {datasetSummary.by_crop.map((c) => {
                    const total = datasetSummary.total || 1;
                    const pct = Math.round((c.count / total) * 100);
                    return (
                      <div key={c.crop} className="rounded-sm border border-line bg-surface p-3">
                        <div className="flex items-center justify-between text-sm">
                          <span className="font-semibold text-ink">{translateCrop(c.crop, language)}</span>
                          <span className="font-mono text-xs font-bold text-muted">{c.count} ({pct}%)</span>
                        </div>
                        <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-line">
                          <div
                            className="h-full bg-admin-600 dark:bg-amber-400"
                            style={{ width: `${Math.min(100, pct)}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Privacy & Partitioning Safeguards banner */}
            <div className="flex items-start gap-3 rounded-sm border border-farmer-200 bg-farmer-50/50 p-3.5 text-xs text-muted dark:border-farmer-900 dark:bg-farmer-950/20">
              <ShieldCheck size={18} className="mt-0.5 shrink-0 text-farmer-700 dark:text-emerald-400" />
              <div>
                <strong className="text-ink">{t("zeroLeakagePrivacyTitle")}:</strong> {t("zeroLeakagePrivacyDesc")}
              </div>
            </div>
          </div>
        )}

        {/* ── TAB 2: Export Dataset Form ── */}
        {mlopsTab === "export" && (
          <div className="mt-5 space-y-5">
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wide text-muted mb-1">{t("cropFilter")}</label>
                <Select
                  value={exportCrop}
                  onChange={(val) => setExportCrop(val)}
                  theme="admin"
                  leadingIcon={<Sprout size={14} className="text-admin-600 dark:text-amber-400" />}
                  options={[
                    { value: "All Crops", label: t("allCrops") },
                    ...CROP_OPTIONS.slice(1).map((c) => ({ value: c, label: translateCrop(c, language) })),
                  ]}
                />
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wide text-muted mb-1">{t("statusFilter")}</label>
                <Select
                  value={exportStatus}
                  onChange={(val) => setExportStatus(val)}
                  theme="admin"
                  leadingIcon={<Filter size={14} className="text-admin-600 dark:text-amber-400" />}
                  options={[
                    { value: "Any", label: t("any") },
                    { value: "pending_review", label: t("pendingReview") },
                    { value: "added_to_dataset", label: t("addedToDataset") },
                    { value: "rejected", label: t("rejected") },
                  ]}
                />
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wide text-muted mb-1">{t("imageTarget")}</label>
                <Select
                  value={exportImageTarget}
                  onChange={(val) => setExportImageTarget(val as any)}
                  theme="admin"
                  leadingIcon={<Image size={14} className="text-admin-600 dark:text-amber-400" />}
                  options={[
                    { value: "preprocessed", label: t("preprocessedImg") },
                    { value: "raw", label: t("rawImg") },
                  ]}
                />
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wide text-muted mb-1">{t("format")}</label>
                <Select
                  value={exportFormat}
                  onChange={(val) => setExportFormat(val as any)}
                  theme="admin"
                  leadingIcon={<FileText size={14} className="text-admin-600 dark:text-amber-400" />}
                  options={[
                    { value: "PyTorch Folder", label: "PyTorch Folder" },
                    { value: "JSON Manifest", label: "JSON Manifest" },
                  ]}
                />
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wide text-muted mb-1">{t("trainValTestSplit")}</label>
                <div className="flex gap-2">
                  <input
                    type="number"
                    min={0}
                    max={100}
                    className="min-h-11 w-full rounded-sm border border-line bg-surface px-3 py-2 text-sm text-ink placeholder:text-muted/70 focus:border-admin-500 focus:outline-none focus:ring-4 focus:ring-admin-100 dark:focus:ring-admin-900/40 transition-colors"
                    placeholder={t("train")}
                    value={exportTrain}
                    onChange={e => setExportTrain(Number(e.target.value))}
                  />
                  <input
                    type="number"
                    min={0}
                    max={100}
                    className="min-h-11 w-full rounded-sm border border-line bg-surface px-3 py-2 text-sm text-ink placeholder:text-muted/70 focus:border-admin-500 focus:outline-none focus:ring-4 focus:ring-admin-100 dark:focus:ring-admin-900/40 transition-colors"
                    placeholder={t("val")}
                    value={exportVal}
                    onChange={e => setExportVal(Number(e.target.value))}
                  />
                  <input
                    type="number"
                    min={0}
                    max={100}
                    className="min-h-11 w-full rounded-sm border border-line bg-surface px-3 py-2 text-sm text-ink placeholder:text-muted/70 focus:border-admin-500 focus:outline-none focus:ring-4 focus:ring-admin-100 dark:focus:ring-admin-900/40 transition-colors"
                    placeholder={t("test")}
                    value={exportTest}
                    onChange={e => setExportTest(Number(e.target.value))}
                  />
                </div>
                <p className="mt-1 text-xs text-muted">{t("mustSum100")}. {t("current")}: {exportTrain + exportVal + exportTest}</p>
              </div>
            </div>

            <div className="pt-2">
              <Button variant="secondary" onClick={handleExportMLOps} disabled={exporting} className="flex items-center gap-2">
                {exporting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Download className="h-4 w-4" />}
                {exporting ? t("exporting") : t("exportMlopsDataset")}
              </Button>
            </div>
          </div>
        )}

        {/* ── TAB 3: Export History / Runs ── */}
        {mlopsTab === "history" && (
          <div className="mt-5 space-y-4">
            <h4 className="text-sm font-bold text-ink">{t("exportRunsHistory")}</h4>
            {(!mlopsRunsData?.runs || mlopsRunsData.runs.length === 0) ? (
              <div className="rounded-sm border border-line bg-canvas py-8 text-center text-sm text-muted">
                {t("noExportRunsYet")}
              </div>
            ) : (
              <div className="overflow-x-auto rounded-sm border border-line">
                <table className="w-full text-left text-sm">
                  <thead className="border-b border-line bg-canvas text-xs font-semibold uppercase tracking-wide text-muted">
                    <tr>
                      <th className="py-2.5 px-3">{t("runId")}</th>
                      <th className="py-2.5 px-3">{t("bundleName")}</th>
                      <th className="py-2.5 px-3">{t("status")}</th>
                      <th className="py-2.5 px-3">{t("runMessage")}</th>
                      <th className="py-2.5 px-3">{t("exportedAt")}</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-line">
                    {mlopsRunsData.runs.map((r) => (
                      <tr key={r.id} className="hover:bg-canvas/50">
                        <td className="py-2 px-3 font-mono text-xs text-muted">#{r.id}</td>
                        <td className="py-2 px-3 font-medium text-ink">{r.model_name}</td>
                        <td className="py-2 px-3">
                          <span className="inline-flex rounded-xs border border-farmer-300 bg-farmer-50 px-2 py-0.5 text-[11px] font-semibold text-farmer-800 dark:border-farmer-700 dark:bg-farmer-950/60 dark:text-farmer-200">
                            {r.status}
                          </span>
                        </td>
                        <td className="py-2 px-3 text-xs text-muted">{r.message || "—"}</td>
                        <td className="py-2 px-3 text-xs text-muted">{new Date(r.started_at).toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </Card>
    </div>
  );
}
