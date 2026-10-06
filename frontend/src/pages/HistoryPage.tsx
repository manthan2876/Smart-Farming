import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { request } from "../api/client";
import { History, ArrowRight, Filter, Search, Sprout } from "../components/icons";
import { Badge, Button, Card, Input, Select, Table, Skeleton } from "../components/ui";
import { translateCrop, translateDisease, translateSeverityBucket } from "../i18n/domain";

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
  const { token, t, language } = useAuth();
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

  const uniqueCrops = [
    "All", 
    ...Array.from(new Set(scans.map((s) => s.crop?.label || s.crop?.name).filter(Boolean)))
  ] as string[];

  return (
    <div className="space-y-6 pb-12">
      <div>
        <span className="text-xs font-semibold uppercase tracking-wider text-muted">{t("diagnosticArchive")}</span>
        <h1 className="mt-1 font-display text-2xl sm:text-3xl text-ink">{t("scanHistoryTitle")}</h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-muted">{t("scanHistorySubtitle")}</p>
      </div>

      <div className="space-y-5">
        <Card className="flex flex-col gap-4 sm:flex-row sm:items-end" padding="md">
          <div className="flex-1">
            <Input 
              id="history-search" 
              label={t("searchRecords")} 
              leadingIcon={<Search size={16} />} 
              type="text" 
              placeholder={t("searchPlaceholder")} 
              value={searchQuery} 
              onChange={(e) => setSearchQuery(e.target.value)} 
            />
          </div>
          <div className="space-y-1.5 sm:w-60">
            <label className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-muted" htmlFor="history-crop-filter">
              <Filter size={14} className="text-farmer-700 dark:text-farmer-300" />
              <span>{t("crop")}</span>
            </label>
            <Select 
              id="history-crop-filter"
              value={filterCrop} 
              onChange={(val) => setFilterCrop(val)}
              options={uniqueCrops.map((crop) => ({
                value: crop,
                label: crop === "All" ? t("all") : translateCrop(crop, language),
                icon: crop === "All" ? <Filter size={14} className="text-muted" /> : <Sprout size={14} className="text-farmer-700 shrink-0" />,
              }))}
            />
          </div>
        </Card>

        {isLoading ? (
          <Table>
            <thead>
              <tr className="bg-canvas text-xs uppercase tracking-wider text-muted">
                <th className="px-5 py-3.5 font-semibold">{t("crop")}</th>
                <th className="px-5 py-3.5 font-semibold">{t("identifiedCondition")}</th>
                <th className="px-5 py-3.5 font-semibold">{t("severity")}</th>
                <th className="px-5 py-3.5 font-semibold">{t("dateOrRequest")}</th>
                <th className="px-5 py-3.5 font-semibold">{t("action")}</th>
              </tr>
            </thead>
            <tbody>
              {[1, 2, 3, 4, 5].map((row) => (
                <tr key={row} className="border-t border-line">
                  <td className="px-5 py-4"><Skeleton className="h-5 w-20" /></td>
                  <td className="px-5 py-4"><Skeleton className="h-5 w-36" /></td>
                  <td className="px-5 py-4"><Skeleton className="h-5 w-24" /></td>
                  <td className="px-5 py-4"><Skeleton className="h-4 w-28" /></td>
                  <td className="px-5 py-4"><Skeleton className="h-4 w-16" /></td>
                </tr>
              ))}
            </tbody>
          </Table>
        ) : filteredScans.length === 0 ? (
          <Card className="flex flex-col items-center text-center" padding="lg">
            <div className="flex h-12 w-12 items-center justify-center rounded-xs bg-farmer-100 text-farmer-800 dark:bg-farmer-900/60 dark:text-farmer-200">
              <History size={24} />
            </div>
            <h3 className="mt-4 font-display text-xl text-ink">{t("noHistoryFound")}</h3>
            <p className="mt-2 text-xs text-muted max-w-sm">{t("noHistoryDesc")}</p>
            <Link to="/scan" className="mt-5">
              <Button size="sm">{t("runNewScan")}</Button>
            </Link>
          </Card>
        ) : (
          <Table>
            <thead>
              <tr className="bg-canvas text-xs uppercase tracking-wider text-muted">
                <th className="px-5 py-3.5 font-semibold">{t("crop")}</th>
                <th className="px-5 py-3.5 font-semibold">{t("identifiedCondition")}</th>
                <th className="px-5 py-3.5 font-semibold">{t("severity")}</th>
                <th className="px-5 py-3.5 font-semibold">{t("dateOrRequest")}</th>
                <th className="px-5 py-3.5 font-semibold">{t("action")}</th>
              </tr>
            </thead>
            <tbody>
              {filteredScans.map((scan, index) => {
                const cropName = scan.crop?.label || scan.crop?.name || "Unknown Crop";
                const diseaseName = scan.disease?.label || scan.disease?.name || "Unidentified Condition";
                
                const rawSeverity = scan.severity;
                const severityText = typeof rawSeverity === "object" && rawSeverity !== null
                  ? (rawSeverity.bucket || rawSeverity.level || rawSeverity.name || "Unknown")
                  : String(rawSeverity || "Unknown");

                const recordId = scan.prediction_id;

                return (
                  <tr className="border-t border-line text-sm text-ink" key={recordId || index}>
                    <td className="px-5 py-4"><Badge>{translateCrop(cropName, language)}</Badge></td>
                    <td className="px-5 py-4 font-semibold">{translateDisease(diseaseName, language)}</td>
                    <td className="px-5 py-4">
                      <Badge tone={severityText.toLowerCase() === "severe" ? "danger" : severityText.toLowerCase() === "moderate" ? "warning" : "success"}>
                        {translateSeverityBucket(severityText, language)}
                      </Badge>
                    </td>
                    <td className="px-5 py-4 text-xs text-muted">{scan.request_id ? `ID: ${scan.request_id.slice(0, 8)}` : "N/A"}</td>
                    <td className="px-5 py-4">
                      {recordId ? (
                        <Link to={`/predictions/${recordId}`} className="inline-flex items-center gap-1 text-xs font-semibold text-farmer-700 hover:text-farmer-900 dark:text-farmer-300 dark:hover:text-farmer-200 transition-colors">
                          <span>{t("viewScan")}</span>
                          <ArrowRight size={13} />
                        </Link>
                      ) : (
                        <span className="text-xs text-muted">{t("unavailable")}</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </Table>
        )}
      </div>
    </div>
  );
}
