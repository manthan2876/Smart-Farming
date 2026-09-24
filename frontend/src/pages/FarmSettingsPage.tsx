import { useState, useEffect, useRef } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "../context/AuthContext";
import { request } from "../api/client";
import { createPlot, deletePlot } from "../api/farm";
import { MapPin, Save, CheckCircle2, Sprout, Trash2, RotateCcw, Map as MapIcon, Navigation2, Satellite } from "lucide-react";
import { APIProvider, Circle, Map as GoogleMap, Marker, Polygon, useMap } from "@vis.gl/react-google-maps";
import { motion } from "motion/react";
import { Button, Card, Input } from "../components/ui";
import { translateCrop } from "../i18n/domain";

type PlotPoint = [number, number];

function GoogleMapController({
  flyToRef,
}: {
  flyToRef: React.MutableRefObject<((latlng: PlotPoint, zoom?: number) => void) | null>;
}) {
  const map = useMap();

  useEffect(() => {
    flyToRef.current = (latlng, zoom = 17) => {
      map?.panTo({ lat: latlng[0], lng: latlng[1] });
      if (map) map.setZoom(zoom);
    };

    return () => {
      flyToRef.current = null;
    };
  }, [flyToRef, map]);

  return null;
}

function toGooglePath(points: PlotPoint[]) {
  return points.map(([latitude, longitude]) => ({ lat: latitude, lng: longitude }));
}

function getEventLatLng(event: any) {
  const latLng = event?.detail?.latLng ?? event?.latLng;
  if (!latLng) return null;
  if (typeof latLng.lat === "function") return [latLng.lat(), latLng.lng()] as PlotPoint;
  if (typeof latLng.lat === "number") return [latLng.lat, latLng.lng] as PlotPoint;
  return null;
}

const boundaryPointIcon = "data:image/svg+xml;charset=UTF-8," + encodeURIComponent(
  '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><circle cx="8" cy="8" r="6" fill="#15803d" stroke="#ffffff" stroke-width="2"/></svg>',
);

const plotBoundaryColors = [
  { stroke: "#2563eb", fill: "#60a5fa" },
  { stroke: "#dc2626", fill: "#f87171" },
  { stroke: "#9333ea", fill: "#c084fc" },
  { stroke: "#ea580c", fill: "#fb923c" },
  { stroke: "#0891b2", fill: "#67e8f9" },
  { stroke: "#ca8a04", fill: "#facc15" },
];

function fromGeoJsonGeometry(geometry: any): PlotPoint[] {
  const coordinates = geometry?.type === "Polygon" ? geometry.coordinates?.[0] : null;
  if (!Array.isArray(coordinates)) return [];

  return coordinates
    .map(([longitude, latitude]: [number, number]) => [latitude, longitude] as PlotPoint)
    .filter(([latitude, longitude]) => Number.isFinite(latitude) && Number.isFinite(longitude));
}

function toGeoJsonPolygon(points: PlotPoint[]) {
  const closedPoints = points.length > 2 && (points[0][0] !== points.at(-1)?.[0] || points[0][1] !== points.at(-1)?.[1])
    ? [...points, points[0]]
    : points;
  return closedPoints.length > 2
    ? { type: "Polygon", coordinates: [closedPoints.map(([latitude, longitude]) => [longitude, latitude])] }
    : null;
}

function pointInsidePolygon(point: PlotPoint, polygon: PlotPoint[]) {
  const [latitude, longitude] = point;
  let inside = false;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const [currentLat, currentLon] = polygon[i];
    const [previousLat, previousLon] = polygon[j];
    const intersects = ((currentLon > longitude) !== (previousLon > longitude))
      && (latitude < (previousLat - currentLat) * (longitude - currentLon) / (previousLon - currentLon) + currentLat);
    if (intersects) inside = !inside;
  }
  return inside;
}

function pointOnPolygonBoundary(point: PlotPoint, polygon: PlotPoint[]) {
  const ring = polygon.length > 1 && polygon[0][0] === polygon.at(-1)?.[0] && polygon[0][1] === polygon.at(-1)?.[1]
    ? polygon.slice(0, -1)
    : polygon;
  const tolerance = 1e-8;
  return ring.some((current, index) => {
    const next = ring[(index + 1) % ring.length];
    const cross = (point[0] - current[0]) * (next[1] - current[1]) - (point[1] - current[1]) * (next[0] - current[0]);
    if (Math.abs(cross) > tolerance) return false;
    return point[0] >= Math.min(current[0], next[0]) - tolerance
      && point[0] <= Math.max(current[0], next[0]) + tolerance
      && point[1] >= Math.min(current[1], next[1]) - tolerance
      && point[1] <= Math.max(current[1], next[1]) + tolerance;
  });
}

function pointInsideOrOnPolygon(point: PlotPoint, polygon: PlotPoint[]) {
  return pointInsidePolygon(point, polygon) || pointOnPolygonBoundary(point, polygon);
}

function nearestEdgeProjection(point: PlotPoint, polygon: PlotPoint[]) {
  const ring = polygon.length > 1 && polygon[0][0] === polygon.at(-1)?.[0] && polygon[0][1] === polygon.at(-1)?.[1]
    ? polygon.slice(0, -1)
    : polygon;
  let closestPoint = ring[0];
  let closestIndex = 0;
  let closestDistance = Number.POSITIVE_INFINITY;

  ring.forEach((current, index) => {
    const next = ring[(index + 1) % ring.length];
    const latitudeLength = next[0] - current[0];
    const longitudeLength = next[1] - current[1];
    const segmentLengthSquared = latitudeLength ** 2 + longitudeLength ** 2 || 1;
    const projection = Math.max(0, Math.min(1, (
      (point[0] - current[0]) * latitudeLength +
      (point[1] - current[1]) * longitudeLength
    ) / segmentLengthSquared));
    const projected: PlotPoint = [
      current[0] + projection * latitudeLength,
      current[1] + projection * longitudeLength,
    ];
    const distance = Math.hypot(point[0] - projected[0], point[1] - projected[1]);
    if (distance < closestDistance) {
      closestDistance = distance;
      closestPoint = projected;
      closestIndex = index;
    }
  });

  return { point: closestPoint, edgeIndex: closestIndex };
}

function BoundaryMap({
  center,
  mapLayer,
  flyToRef,
  farmBoundary,
  drawingPoints,
  currentLocation,
  drawingActive,
  plotDrawingActive,
  onVertexDragEnd,
  plots = [],
  showPlots = false,
  onMapClick,
  onBoundaryClick,
  onVertexDoubleClick,
}: {
  center: PlotPoint;
  mapLayer: "satellite" | "street";
  flyToRef: React.MutableRefObject<((latlng: PlotPoint, zoom?: number) => void) | null>;
  farmBoundary: PlotPoint[];
  drawingPoints: PlotPoint[];
  currentLocation: PlotPoint | null;
  drawingActive: boolean;
  plotDrawingActive: boolean;
  onVertexDragEnd: (index: number, point: PlotPoint) => void;
  plots?: any[];
  showPlots?: boolean;
  onMapClick: (point: PlotPoint) => void;
  onBoundaryClick: (point: PlotPoint) => void;
  onVertexDoubleClick: (index: number) => void;
}) {
  return (
    <GoogleMap
      defaultCenter={{ lat: center[0], lng: center[1] }}
      defaultZoom={15}
      mapTypeId={mapLayer === "satellite" ? "satellite" : "roadmap"}
      gestureHandling={drawingActive ? "none" : "greedy"}
      disableDoubleClickZoom
      className="h-full w-full"
      onClick={(event) => {
        const point = getEventLatLng(event);
        if (point) onMapClick(point);
      }}
    >
      <GoogleMapController flyToRef={flyToRef} />
      {farmBoundary.length >= 3 && (
        <Polygon
          paths={toGooglePath(farmBoundary)}
          onClick={(event) => {
            const point = getEventLatLng(event);
            if (point) onBoundaryClick(point);
          }}
          options={{
            strokeColor: plotDrawingActive ? "#f59e0b" : "#0f766e",
            strokeWeight: plotDrawingActive ? 4 : 3,
            fillColor: plotDrawingActive ? "#facc15" : "#14b8a6",
            fillOpacity: plotDrawingActive ? 0.28 : 0.12,
            clickable: !plotDrawingActive,
          }}
        />
      )}
      {showPlots && plots.map((plot: any, index: number) => {
        const points = fromGeoJsonGeometry(plot.geometry);
        const color = plotBoundaryColors[index % plotBoundaryColors.length];
        return points.length >= 3 ? (
          <Polygon
            key={plot.id}
            paths={toGooglePath(points)}
            options={{ strokeColor: color.stroke, strokeWeight: 3, fillColor: color.fill, fillOpacity: 0.38, clickable: false }}
          />
        ) : null;
      })}
      {drawingPoints.length >= 3 && (
        <Polygon
          paths={toGooglePath(drawingPoints)}
          onClick={(event) => {
            const point = getEventLatLng(event);
            if (point) onBoundaryClick(point);
          }}
          options={{ strokeColor: "#16a34a", strokeWeight: 3, fillColor: "#16a34a", fillOpacity: 0.25, clickable: true }}
        />
      )}
      {drawingPoints.map((point, index) => (
        <Marker
          key={`drawing-${index}`}
          position={{ lat: point[0], lng: point[1] }}
          icon={boundaryPointIcon}
          draggable={drawingActive}
          onDblClick={() => onVertexDoubleClick(index)}
          onDragEnd={(event) => {
            const point = getEventLatLng(event);
            if (point) onVertexDragEnd(index, point);
          }}
        />
      ))}
      {currentLocation && (
        <Circle
          center={{ lat: currentLocation[0], lng: currentLocation[1] }}
          radius={12}
          options={{ strokeColor: "#2563eb", strokeWeight: 2, fillColor: "#2563eb", fillOpacity: 0.75 }}
        />
      )}
    </GoogleMap>
  );
}

export default function FarmSettingsPage() {
  const { token, user, language, t } = useAuth();
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
      setFarmBoundary(fromGeoJsonGeometry(farmData.boundary));
    }
  }, [farmData]);

  const [newPlotName, setNewPlotName] = useState("");
  const [newPlotCrop, setNewPlotCrop] = useState("");
  const [newPlotArea, setNewPlotArea] = useState<number | "">("");
  const [farmBoundary, setFarmBoundary] = useState<PlotPoint[]>([]);
  const [newPlotGeometry, setNewPlotGeometry] = useState<PlotPoint[]>([]);
  const [isDrawingFarm, setIsDrawingFarm] = useState(false);
  const [isDrawingPlot, setIsDrawingPlot] = useState(false);
  const [boundaryDialog, setBoundaryDialog] = useState<"farm" | "plot" | null>(null);
  const [showBoundaryOverview, setShowBoundaryOverview] = useState(false);
  const [isEditingBoundary, setIsEditingBoundary] = useState(false);
  const [mapLayer, setMapLayer] = useState<'satellite' | 'street'>('satellite');
  const [isLocating, setIsLocating] = useState(false);
  const [currentLocation, setCurrentLocation] = useState<PlotPoint | null>(null);
  const plotFlyToRef = useRef<((latlng: PlotPoint, zoom?: number) => void) | null>(null);

  // GPS Locate Me handler
  const handleLocate = () => {
    if (!navigator.geolocation) {
      alert("Geolocation is not supported by your browser.");
      return;
    }
    setIsLocating(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const latlng: PlotPoint = [pos.coords.latitude, pos.coords.longitude];
        setLat(latlng[0]);
        setLon(latlng[1]);
        setCurrentLocation(latlng);
        plotFlyToRef.current?.(latlng, 17);
        setIsLocating(false);
      },
      (err) => {
        console.error("Geolocation error:", err);
        alert("Could not get your location. Please allow location access in your browser.");
        setIsLocating(false);
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  };

  const createPlotMutation = useMutation({
    mutationFn: async (plotData: any) => createPlot(plotData, token!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["farmSettings"] });
      setNewPlotName("");
      setNewPlotCrop("");
      setNewPlotArea("");
      setNewPlotGeometry([]);
      closeBoundaryDialog();
    }
  });

  const deletePlotMutation = useMutation({
    mutationFn: async (plotId: number) => deletePlot(plotId, token!),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["farmSettings"] })
  });

  const addBoundaryPoint = (point: PlotPoint) => {
    const safePoint = isDrawingPlot && farmBoundary.length >= 3 && !pointInsideOrOnPolygon(point, farmBoundary)
      ? nearestEdgeProjection(point, farmBoundary).point
      : point;

    if (isDrawingFarm) {
      setFarmBoundary((points) => [...points, safePoint]);
    } else if (isDrawingPlot) {
      if (farmBoundary.length < 3) return;
      setNewPlotGeometry((points) => [...points, safePoint]);
    }
  };

  const insertBoundaryPoint = (point: PlotPoint, boundary: "farm" | "plot") => {
    const points = boundary === "farm" ? farmBoundary : newPlotGeometry;
    if (points.length < 2) return;
    const safePoint = boundary === "plot" && farmBoundary.length >= 3 && !pointInsideOrOnPolygon(point, farmBoundary)
      ? nearestEdgeProjection(point, farmBoundary).point
      : point;

    const next = [...points];
    const edgeIndex = nearestEdgeProjection(safePoint, next).edgeIndex;
    next.splice(edgeIndex + 1, 0, safePoint);
    if (boundary === "farm") setFarmBoundary(next);
    else setNewPlotGeometry(next);
  };

  const deleteBoundaryPoint = (index: number, boundary: "farm" | "plot") => {
    if (boundary === "farm") setFarmBoundary((points) => points.filter((_, pointIndex) => pointIndex !== index));
    else setNewPlotGeometry((points) => points.filter((_, pointIndex) => pointIndex !== index));
  };

  const moveBoundaryPoint = (index: number, point: PlotPoint, boundary: "farm" | "plot") => {
    const safePoint = boundary === "plot" && farmBoundary.length >= 3 && !pointInsideOrOnPolygon(point, farmBoundary)
      ? nearestEdgeProjection(point, farmBoundary).point
      : point;
    if (boundary === "farm") setFarmBoundary((points) => points.map((current, pointIndex) => pointIndex === index ? safePoint : current));
    else setNewPlotGeometry((points) => points.map((current, pointIndex) => pointIndex === index ? safePoint : current));
  };

  const openBoundaryDialog = (boundary: "farm" | "plot") => {
    if (boundary === "plot" && farmBoundary.length < 3) {
      alert("Save a farm boundary before creating a plot boundary.");
      return;
    }
    setBoundaryDialog(boundary);
    setIsEditingBoundary(false);
    setIsDrawingFarm(boundary === "farm");
    setIsDrawingPlot(boundary === "plot");
  };

  const closeBoundaryDialog = () => {
    setBoundaryDialog(null);
    setIsEditingBoundary(false);
    setIsDrawingFarm(false);
    setIsDrawingPlot(false);
  };

  const handleCreatePlot = (e: React.FormEvent) => {
    e.preventDefault();
    savePlot();
  };

  const savePlot = () => {
    if (farmBoundary.length < 3) {
      alert("Draw and save the farm boundary before adding a plot.");
      return;
    }
    if (newPlotGeometry.length < 3 || newPlotGeometry.some((point) => !pointInsideOrOnPolygon(point, farmBoundary))) {
      alert("Draw at least three plot points inside the farm boundary.");
      return;
    }

    createPlotMutation.mutate({
      name: newPlotName,
      crop: newPlotCrop || null,
      area_acres: newPlotArea ? Number(newPlotArea) : null,
      geometry: toGeoJsonPolygon(newPlotGeometry),
    });
  };

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
      if (boundaryDialog === "farm") closeBoundaryDialog();
    },
  });

  const saveFarmBoundary = () => {
    if (farmBoundary.length < 3) {
      alert("Add at least three farm boundary points before saving.");
      return;
    }
    mutation.mutate({
      name: farmName,
      location,
      area_acres: Number(area),
      latitude: Number(lat),
      longitude: Number(lon),
      crop_history: cropHistory.split(",").map((s) => s.trim()).filter(Boolean),
      boundary: toGeoJsonPolygon(farmBoundary),
    });
  };


  const handleDeleteData = async () => {
    if (deleteConfirmText !== "DELETE") return;
    setIsDeleting(true);
    try {
      await request("/admin/purge?confirmation=DELETE", {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ confirmation: "DELETE" }),
      }, token!);
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
      boundary: toGeoJsonPolygon(farmBoundary),
    });
  };

  if (isLoading) return <div className="flex min-h-[40vh] items-center justify-center"><div className="h-6 w-6 animate-spin rounded-full border-2 border-farmer-200 border-t-farmer-700" /></div>;

  return (
    <APIProvider apiKey={import.meta.env.VITE_GOOGLE_MAPS_API_KEY || ""}>
      <div className="space-y-6 pb-12">
      <div>
        <h1 className="font-display text-3xl text-ink sm:text-4xl">{t("farmConfigTitle")}</h1>
        <p className="mt-3 max-w-3xl leading-7 text-muted">{t("farmConfigSubtitle")}</p>
      </div>

      <motion.form 
        onSubmit={handleSubmit} 
        className="rounded-md border border-line bg-surface p-5 shadow-soft sm:p-6"
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
      >
        {successMessage && (
          <div className="mb-5 flex items-center gap-3 rounded-sm border border-farmer-200 bg-farmer-50 p-3 text-sm font-semibold text-farmer-800">
            <CheckCircle2 size={18} />
            <span>{t("farmUpdatedSuccess")}</span>
          </div>
        )}

        <div className="space-y-5">
        <Input label={t("farmName")} leadingIcon={<Sprout size={16} />} type="text" value={farmName} onChange={(e) => setFarmName(e.target.value)} required />

        <Input label={t("locationRegion")} leadingIcon={<MapPin size={16} />} type="text" value={location} onChange={(e) => setLocation(e.target.value)} placeholder="e.g. Bhavnagar, Gujarat" required />

        <Input label={t("totalFarmArea")} type="number" step="any" value={area} onChange={(e) => setArea(Number(e.target.value))} required />

        <div className="grid gap-5 sm:grid-cols-2">
          <Input label={t("gpsLatitude")} leadingIcon={<MapPin size={16} />} type="number" step="any" value={lat} onChange={(e) => setLat(Number(e.target.value))} required />
          <Input label={t("gpsLongitude")} leadingIcon={<MapPin size={16} />} type="number" step="any" value={lon} onChange={(e) => setLon(Number(e.target.value))} required />
        </div>

        <Input label={t("cropHistory")} type="text" value={cropHistory} onChange={(e) => setCropHistory(e.target.value)} placeholder="e.g. Cotton, Groundnut, Wheat" />

        <div className="rounded-sm border border-farmer-200 bg-farmer-50 p-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h3 className="font-display text-xl text-farmer-800">{t("farmBoundary")}</h3>
              <p className="mt-1 text-xs text-muted">{t("farmBoundaryDesc")}</p>
            </div>
            <div className="flex flex-wrap gap-2">
              <button type="button" onClick={() => openBoundaryDialog("farm")} className="rounded-sm border border-line bg-surface px-3 py-2 text-xs font-semibold text-ink">
                {farmBoundary.length >= 3 ? t("editBoundary") : t("createBoundary")}
              </button>
              {farmBoundary.length > 0 && <button type="button" onClick={() => setFarmBoundary([])} className="rounded-sm border border-red-200 px-3 py-2 text-xs font-semibold text-danger">{t("clearBoundary")}</button>}
            </div>
          </div>
        </div>

        <Button type="submit" disabled={mutation.isPending}>
          <Save size={18} /> {mutation.isPending ? t("saving") : t("saveFarmConfig")}
        </Button>
        </div>
      </motion.form>

      
      <motion.div 
        className="rounded-md border border-line bg-surface p-5 shadow-soft sm:p-6"
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <h2 className="font-display text-2xl text-ink">{t("managePlots")}</h2>
        <p className="mt-2 text-sm leading-6 text-muted">{t("managePlotsSubtitle")}</p>
        
        <div className="mt-6 space-y-3">
          {farmData?.plots?.map((plot: any) => (
            <div key={plot.id} className="flex items-center justify-between gap-4 rounded-sm border border-line bg-canvas p-4">
              <div>
                <strong className="block text-base font-semibold text-ink">{plot.name}</strong>
                <span className="mt-1 block text-xs text-muted">
                  {t("crop")}: {translateCrop(plot.crop, language)} &bull; {t("areaLabel")}: {plot.area_acres ? `${plot.area_acres} ${t("areaUnit")}` : "Unknown"}
                </span>
              </div>
              <button 
                onClick={() => {
                  if (confirm('Are you sure you want to delete this plot?')) {
                    deletePlotMutation.mutate(plot.id);
                  }
                }}
                disabled={deletePlotMutation.isPending}
                className="rounded-sm bg-red-50 p-2 text-danger hover:bg-red-100"
              >
                <Trash2 size={18} />
              </button>
            </div>
          ))}
          {(!farmData?.plots || farmData.plots.length === 0) && (
            <div className="rounded-sm bg-canvas p-8 text-center text-sm text-muted">
              {t("noPlotsConfigured")}
            </div>
          )}
        </div>

        <form onSubmit={handleCreatePlot} className="mt-8 rounded-sm border border-dashed border-farmer-300 bg-farmer-50 p-5">
          <h3 className="font-display text-xl text-farmer-800">{t("addNewPlot")}</h3>
          <div className="mt-5 grid gap-5 sm:grid-cols-3">
            <Input label={t("plotName")} type="text" value={newPlotName} onChange={e => setNewPlotName(e.target.value)} placeholder="e.g. North Field" required />
            <Input label={t("currentCrop")} type="text" value={newPlotCrop} onChange={e => setNewPlotCrop(e.target.value)} placeholder="e.g. Cotton" />
            <Input label={t("plotArea")} type="number" step="any" value={newPlotArea} onChange={e => setNewPlotArea(e.target.value ? Number(e.target.value) : "")} placeholder="Optional" />
          </div>
          <div className="mt-6">
            <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
              <label className="flex items-center gap-2 text-sm font-semibold text-ink">
                <MapIcon size={16} /> {t("plotBoundary")}
              </label>
              <div className="flex flex-wrap items-center gap-2">
                <button
                  type="button"
                  onClick={() => openBoundaryDialog("plot")}
                  className="rounded-sm border border-line bg-surface px-3 py-1.5 text-xs font-semibold text-ink"
                >
                  {newPlotGeometry.length >= 3 ? t("editPlotBoundary") : t("createPlotBoundary")}
                </button>
                <button
                  type="button"
                  onClick={handleLocate}
                  disabled={isLocating}
                  className="inline-flex items-center gap-1.5 rounded-sm border border-expert-100 bg-expert-50 px-3 py-1.5 text-xs font-semibold text-expert-700 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  <Navigation2 size={14} className={isLocating ? 'animate-spin' : ''} />
                  {isLocating ? t("locating") : t("myLocation")}
                </button>
                {/* Layer Toggle */}
                <div className="flex overflow-hidden rounded-sm border border-line">
                  <button
                    type="button"
                    onClick={() => setMapLayer('satellite')}
                    className={`inline-flex items-center gap-1 px-3 py-1.5 text-xs font-semibold ${mapLayer === 'satellite' ? 'bg-ink text-white' : 'bg-canvas text-muted'}`}
                  >
                    <Satellite size={13} /> {t("satellite")}
                  </button>
                  <button
                    type="button"
                    onClick={() => setMapLayer('street')}
                    className={`inline-flex items-center gap-1 border-l border-line px-3 py-1.5 text-xs font-semibold ${mapLayer === 'street' ? 'bg-ink text-white' : 'bg-canvas text-muted'}`}
                  >
                    <MapIcon size={13} /> {t("street")}
                  </button>
                </div>
                {newPlotGeometry.length > 0 && (
                  <button type="button" onClick={() => setNewPlotGeometry([])} className="inline-flex items-center gap-1 rounded-sm border border-red-200 px-3 py-1.5 text-xs font-semibold text-danger hover:bg-red-50">
                    <RotateCcw size={13} /> {t("clear")}
                  </button>
                )}
              </div>
            </div>

            <p className="mt-2 text-xs leading-5 text-muted">{t("plotBoundaryDesc")}</p>
          </div>
          <Button type="submit" className="mt-5 bg-farmer-600 hover:bg-farmer-700" disabled={createPlotMutation.isPending || !newPlotName || farmBoundary.length < 3 || newPlotGeometry.length < 3}>
            {createPlotMutation.isPending ? t("adding") : t("addPlotBtn")}
          </Button>
        </form>
      </motion.div>

      <div className="flex justify-end border-t border-line pt-5">
        <Button type="button" onClick={() => setShowBoundaryOverview(true)}>
          <MapIcon size={18} /> {t("seeBoundaries")}
        </Button>
      </div>

      {boundaryDialog && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-ink/50 p-4" role="dialog" aria-modal="true" aria-label={`${boundaryDialog === "farm" ? "Farm" : "Plot"} boundary editor`}>
          <div className="flex max-h-[92vh] w-full max-w-5xl flex-col overflow-hidden rounded-md border border-line bg-surface shadow-lift">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line p-4">
              <div>
                <h2 className="font-display text-2xl text-ink">{boundaryDialog === "farm" ? t("farmBoundary") : t("plotBoundary")}</h2>
                <p className="mt-1 text-xs text-muted">{isEditingBoundary ? "Edit mode: click to add, drag to move, double-click to delete, or click a line to insert." : "Map mode: pan and zoom normally. Click Edit boundary to change points."}</p>
              </div>
              <div className="flex flex-wrap gap-2">
                <button type="button" onClick={() => setIsEditingBoundary((editing) => !editing)} className={`rounded-sm px-3 py-2 text-xs font-semibold ${isEditingBoundary ? "bg-farmer-700 text-white" : "border border-line bg-surface text-ink"}`}>
                  {isEditingBoundary ? t("stopEditing") : t("editBoundaryBtn")}
                </button>
                <button type="button" onClick={handleLocate} disabled={isLocating} className="inline-flex items-center gap-1.5 rounded-sm border border-expert-100 bg-expert-50 px-3 py-2 text-xs font-semibold text-expert-700 disabled:opacity-60">
                  <Navigation2 size={14} className={isLocating ? "animate-spin" : ""} /> {isLocating ? t("locating") : t("myLocation")}
                </button>
                <button type="button" onClick={() => setMapLayer((layer) => layer === "satellite" ? "street" : "satellite")} className="inline-flex items-center gap-1.5 rounded-sm border border-line px-3 py-2 text-xs font-semibold text-ink">
                  {mapLayer === "satellite" ? <MapIcon size={14} /> : <Satellite size={14} />} {mapLayer === "satellite" ? t("street") : t("satellite")}
                </button>
              </div>
            </div>
            <div className="min-h-[22rem] flex-1 p-4">
              <div className="h-[min(62vh,34rem)] w-full overflow-hidden rounded-sm border border-line">
                <BoundaryMap
                  center={[lat || 21.0, lon || 72.0]}
                  mapLayer={mapLayer}
                  flyToRef={plotFlyToRef}
                  farmBoundary={farmBoundary}
                  drawingPoints={boundaryDialog === "farm" ? farmBoundary : newPlotGeometry}
                  currentLocation={currentLocation}
                  drawingActive={isEditingBoundary}
                  plotDrawingActive={boundaryDialog === "plot"}
                  plots={farmData?.plots}
                  showPlots={boundaryDialog === "plot"}
                  onMapClick={(point) => { if (isEditingBoundary) addBoundaryPoint(point); }}
                  onBoundaryClick={(point) => {
                    if (!isEditingBoundary) return;
                    insertBoundaryPoint(point, boundaryDialog);
                  }}
                  onVertexDoubleClick={(index) => { if (isEditingBoundary) deleteBoundaryPoint(index, boundaryDialog); }}
                  onVertexDragEnd={(index, point) => { if (isEditingBoundary) moveBoundaryPoint(index, point, boundaryDialog); }}
                />
              </div>
            </div>
            <div className="flex justify-end gap-2 border-t border-line p-4">
              <button type="button" onClick={closeBoundaryDialog} className="rounded-sm border border-line px-4 py-2 text-sm font-semibold text-ink">{t("cancel")}</button>
              {boundaryDialog === "farm" ? (
                <Button type="button" onClick={saveFarmBoundary} disabled={mutation.isPending || farmBoundary.length < 3}>
                  {mutation.isPending ? t("saving") : t("saveFarmBoundary")}
                </Button>
              ) : (
                <Button type="button" onClick={() => savePlot()} disabled={createPlotMutation.isPending || newPlotGeometry.length < 3 || !newPlotName}>
                  {createPlotMutation.isPending ? t("saving") : t("savePlotBoundary")}
                </Button>
              )}
            </div>
          </div>
        </div>
      )}

      {showBoundaryOverview && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-ink/50 p-4" role="dialog" aria-modal="true" aria-label="Farm and plot boundaries">
          <div className="flex max-h-[92vh] w-full max-w-5xl flex-col overflow-hidden rounded-md border border-line bg-surface shadow-lift">
            <div className="flex items-center justify-between gap-3 border-b border-line p-4">
              <div>
                <h2 className="font-display text-2xl text-ink">{t("farmAndPlotBoundaries")}</h2>
                <p className="mt-1 text-xs text-muted">{t("boundaryOverviewDesc")}</p>
              </div>
              <button type="button" onClick={() => setShowBoundaryOverview(false)} className="rounded-sm border border-line px-4 py-2 text-sm font-semibold text-ink">
                {t("close")}
              </button>
            </div>
            <div className="p-4">
              <div className="h-[min(70vh,40rem)] w-full overflow-hidden rounded-sm border border-line">
                <BoundaryMap
                  center={[lat || 21.0, lon || 72.0]}
                  mapLayer={mapLayer}
                  flyToRef={plotFlyToRef}
                  farmBoundary={farmBoundary}
                  drawingPoints={[]}
                  currentLocation={null}
                  drawingActive={false}
                  plotDrawingActive={false}
                  plots={farmData?.plots}
                  showPlots
                  onMapClick={() => undefined}
                  onBoundaryClick={() => undefined}
                  onVertexDoubleClick={() => undefined}
                  onVertexDragEnd={() => undefined}
                />
              </div>
              <div className="mt-3 flex flex-wrap items-center gap-4 text-xs font-semibold text-muted">
                <span className="inline-flex items-center gap-2"><span className="h-3 w-3 rounded-sm border-2 border-teal-700 bg-teal-300/40" /> Farm boundary</span>
                <span className="inline-flex items-center gap-2"><span className="h-3 w-3 rounded-sm border-2 border-blue-600 bg-blue-400/60" /> Plot 1</span>
                <span className="inline-flex items-center gap-2"><span className="h-3 w-3 rounded-sm border-2 border-red-600 bg-red-400/60" /> Plot 2</span>
                <span className="text-muted">Additional plots use different colors.</span>
              </div>
            </div>
          </div>
        </div>
      )}

      

      

      </div>
    </APIProvider>
  );
}
