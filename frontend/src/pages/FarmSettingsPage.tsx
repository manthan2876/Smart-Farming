import { useState, useEffect, useRef } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "../context/AuthContext";
import { createPlot, deletePlot, getFarm, saveFarm, updatePlot } from "../api/farm";
import { MapPin, Save, CheckCircle2, Sprout, Trash2, RotateCcw, Map as MapIcon, Navigation2, Satellite, Pencil, X } from "../components/icons";
import { MapContainer, TileLayer, Polygon, Marker, Circle, useMap, useMapEvents } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { motion } from "motion/react";
import { Button, Input } from "../components/ui";
import { translateCrop } from "../i18n/domain";

type PlotPoint = [number, number];

function LeafletMapController({
  center,
  flyToRef,
}: {
  center: PlotPoint;
  flyToRef: React.MutableRefObject<((latlng: PlotPoint, zoom?: number) => void) | null>;
}) {
  const map = useMap();

  useEffect(() => {
    flyToRef.current = (latlng, zoom = 17) => {
      map.flyTo(latlng, zoom, { duration: 0.8 });
    };

    return () => {
      flyToRef.current = null;
    };
  }, [flyToRef, map]);

  useEffect(() => {
    if (center && Number.isFinite(center[0]) && Number.isFinite(center[1])) {
      map.setView(center, map.getZoom() || 15);
    }
  }, [center, map]);

  return null;
}

function MapResizeHandler() {
  const map = useMap();
  useEffect(() => {
    const timer = setTimeout(() => {
      map.invalidateSize();
    }, 150);
    return () => clearTimeout(timer);
  }, [map]);
  return null;
}

function MapEventsHandler({
  onMapClick,
  drawingActive,
}: {
  onMapClick: (point: PlotPoint) => void;
  drawingActive: boolean;
}) {
  useMapEvents({
    click(e) {
      if (drawingActive) {
        onMapClick([e.latlng.lat, e.latlng.lng]);
      }
    },
  });
  return null;
}

const vertexIcon = L.divIcon({
  className: "custom-vertex-marker",
  html: '<div style="width: 14px; height: 14px; background: #15803d; border: 2.5px solid #ffffff; border-radius: 50%; box-shadow: 0 1px 4px rgba(0,0,0,0.55); cursor: grab;"></div>',
  iconSize: [14, 14],
  iconAnchor: [7, 7],
});

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
  const mapCenter: PlotPoint = [
    Number.isFinite(center[0]) && center[0] !== 0 ? center[0] : 21.7645,
    Number.isFinite(center[1]) && center[1] !== 0 ? center[1] : 72.1519,
  ];

  return (
    <div className="relative h-full w-full overflow-hidden">
      <MapContainer
        center={mapCenter}
        zoom={15}
        scrollWheelZoom={!drawingActive}
        doubleClickZoom={false}
        className="h-full w-full z-0"
      >
        <LeafletMapController center={mapCenter} flyToRef={flyToRef} />
        <MapResizeHandler />
        <MapEventsHandler onMapClick={onMapClick} drawingActive={drawingActive} />

        {mapLayer === "satellite" ? (
          <TileLayer
            key="satellite-tiles"
            attribution='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
            url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
            maxZoom={19}
          />
        ) : (
          <TileLayer
            key="osm-tiles"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            maxZoom={19}
          />
        )}

        {/* Saved Farm Boundary */}
        {farmBoundary.length >= 3 && (
          <Polygon
            positions={farmBoundary}
            pathOptions={{
              color: plotDrawingActive ? "#f59e0b" : "#0f766e",
              weight: plotDrawingActive ? 4 : 3,
              fillColor: plotDrawingActive ? "#facc15" : "#14b8a6",
              fillOpacity: plotDrawingActive ? 0.28 : 0.12,
            }}
            eventHandlers={{
              click: (e) => {
                L.DomEvent.stopPropagation(e);
                if (!plotDrawingActive) {
                  onBoundaryClick([e.latlng.lat, e.latlng.lng]);
                }
              },
            }}
          />
        )}

        {/* Existing Plots Overlays */}
        {showPlots &&
          plots.map((plot: any, index: number) => {
            const points = fromGeoJsonGeometry(plot.geometry);
            const color = plotBoundaryColors[index % plotBoundaryColors.length];
            return points.length >= 3 ? (
              <Polygon
                key={plot.id}
                positions={points}
                pathOptions={{
                  color: color.stroke,
                  weight: 3,
                  fillColor: color.fill,
                  fillOpacity: 0.38,
                }}
              />
            ) : null;
          })}

        {/* Active Drawing Boundary Polygon */}
        {drawingPoints.length >= 3 && (
          <Polygon
            positions={drawingPoints}
            pathOptions={{
              color: "#16a34a",
              weight: 3,
              fillColor: "#16a34a",
              fillOpacity: 0.25,
            }}
            eventHandlers={{
              click: (e) => {
                L.DomEvent.stopPropagation(e);
                onBoundaryClick([e.latlng.lat, e.latlng.lng]);
              },
            }}
          />
        )}

        {/* Draggable Vertex Markers for active polygon */}
        {drawingPoints.map((point, index) => (
          <Marker
            key={`drawing-${index}`}
            position={point}
            icon={vertexIcon}
            draggable={drawingActive}
            eventHandlers={{
              dragend: (e) => {
                const marker = e.target;
                const latlng = marker.getLatLng();
                onVertexDragEnd(index, [latlng.lat, latlng.lng]);
              },
              dblclick: (e) => {
                L.DomEvent.stopPropagation(e);
                onVertexDoubleClick(index);
              },
            }}
          />
        ))}

        {/* Geolocation indicator */}
        {currentLocation && (
          <Circle
            center={currentLocation}
            radius={15}
            pathOptions={{
              color: "#2563eb",
              weight: 2,
              fillColor: "#2563eb",
              fillOpacity: 0.75,
            }}
          />
        )}
      </MapContainer>
    </div>
  );
}

export default function FarmSettingsPage() {
  const { token, language, t } = useAuth();
  const queryClient = useQueryClient();

  const [farmName, setFarmName] = useState("");
  const [location, setLocation] = useState("");
  const [area, setArea] = useState<number>(0);
  const [lat, setLat] = useState<number>(0);
  const [lon, setLon] = useState<number>(0);
  const [cropHistory, setCropHistory] = useState("");
  const [successMessage, setSuccessMessage] = useState(false);


  const { data: farmData, isLoading } = useQuery({
    queryKey: ["farmSettings", language],
    queryFn: () => getFarm(token!, language),
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
  const [boundaryDialog, setBoundaryDialog] = useState<"farm" | "plot" | "edit_plot" | null>(null);
  const [showBoundaryOverview, setShowBoundaryOverview] = useState(false);
  const [isEditingBoundary, setIsEditingBoundary] = useState(false);
  const [mapLayer, setMapLayer] = useState<'satellite' | 'street'>('satellite');
  const [isLocating, setIsLocating] = useState(false);
  const [currentLocation, setCurrentLocation] = useState<PlotPoint | null>(null);
  const plotFlyToRef = useRef<((latlng: PlotPoint, zoom?: number) => void) | null>(null);

  // Edit plot state
  const [editingPlot, setEditingPlot] = useState<any | null>(null);
  const [editPlotName, setEditPlotName] = useState("");
  const [editPlotCrop, setEditPlotCrop] = useState("");
  const [editPlotArea, setEditPlotArea] = useState<number | "">("");
  const [editPlotGeometry, setEditPlotGeometry] = useState<PlotPoint[]>([]);
  const [plotSuccessMessage, setPlotSuccessMessage] = useState<string | null>(null);

  // GPS Locate Me handler
  const handleLocate = () => {
    if (!navigator.geolocation) {
      alert(t("geolocationUnsupported"));
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
        alert(t("locationUnavailable"));
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

  const updatePlotMutation = useMutation({
    mutationFn: async ({ id, plotData }: { id: number; plotData: any }) =>
      updatePlot(id, plotData, token!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["farmSettings"] });
      setPlotSuccessMessage(t("plotUpdatedSuccess"));
      setTimeout(() => setPlotSuccessMessage(null), 4000);
      setEditingPlot(null);
      setEditPlotName("");
      setEditPlotCrop("");
      setEditPlotArea("");
      setEditPlotGeometry([]);
      closeBoundaryDialog();
    },
    onError: (err: any) => {
      alert(err?.message || t("plotUpdateFailed"));
    },
  });

  const deletePlotMutation = useMutation({
    mutationFn: async (plotId: number) => deletePlot(plotId, token!),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["farmSettings"] })
  });

  const addBoundaryPoint = (point: PlotPoint) => {
    const isPlot = isDrawingPlot;
    const safePoint = isPlot && farmBoundary.length >= 3 && !pointInsideOrOnPolygon(point, farmBoundary)
      ? nearestEdgeProjection(point, farmBoundary).point
      : point;

    if (isDrawingFarm) {
      setFarmBoundary((points) => [...points, safePoint]);
    } else if (boundaryDialog === "edit_plot") {
      if (farmBoundary.length < 3) return;
      setEditPlotGeometry((points) => [...points, safePoint]);
    } else if (isDrawingPlot) {
      if (farmBoundary.length < 3) return;
      setNewPlotGeometry((points) => [...points, safePoint]);
    }
  };

  const insertBoundaryPoint = (point: PlotPoint, boundary: "farm" | "plot" | "edit_plot") => {
    const points = boundary === "farm" ? farmBoundary : boundary === "edit_plot" ? editPlotGeometry : newPlotGeometry;
    if (points.length < 2) return;
    const safePoint = boundary !== "farm" && farmBoundary.length >= 3 && !pointInsideOrOnPolygon(point, farmBoundary)
      ? nearestEdgeProjection(point, farmBoundary).point
      : point;

    const next = [...points];
    const edgeIndex = nearestEdgeProjection(safePoint, next).edgeIndex;
    next.splice(edgeIndex + 1, 0, safePoint);
    if (boundary === "farm") setFarmBoundary(next);
    else if (boundary === "edit_plot") setEditPlotGeometry(next);
    else setNewPlotGeometry(next);
  };

  const deleteBoundaryPoint = (index: number, boundary: "farm" | "plot" | "edit_plot") => {
    if (boundary === "farm") setFarmBoundary((points) => points.filter((_, pointIndex) => pointIndex !== index));
    else if (boundary === "edit_plot") setEditPlotGeometry((points) => points.filter((_, pointIndex) => pointIndex !== index));
    else setNewPlotGeometry((points) => points.filter((_, pointIndex) => pointIndex !== index));
  };

  const moveBoundaryPoint = (index: number, point: PlotPoint, boundary: "farm" | "plot" | "edit_plot") => {
    const safePoint = boundary !== "farm" && farmBoundary.length >= 3 && !pointInsideOrOnPolygon(point, farmBoundary)
      ? nearestEdgeProjection(point, farmBoundary).point
      : point;
    if (boundary === "farm") setFarmBoundary((points) => points.map((current, pointIndex) => pointIndex === index ? safePoint : current));
    else if (boundary === "edit_plot") setEditPlotGeometry((points) => points.map((current, pointIndex) => pointIndex === index ? safePoint : current));
    else setNewPlotGeometry((points) => points.map((current, pointIndex) => pointIndex === index ? safePoint : current));
  };

  const openBoundaryDialog = (boundary: "farm" | "plot" | "edit_plot") => {
    if ((boundary === "plot" || boundary === "edit_plot") && farmBoundary.length < 3) {
      alert(t("saveFarmBoundaryFirst"));
      return;
    }
    setBoundaryDialog(boundary);
    setIsEditingBoundary(true);
    setIsDrawingFarm(boundary === "farm");
    setIsDrawingPlot(boundary === "plot" || boundary === "edit_plot");

    if (boundary === "edit_plot" && editPlotGeometry.length > 0) {
      setTimeout(() => {
        plotFlyToRef.current?.(editPlotGeometry[0], 17);
      }, 100);
    }
  };

  const closeBoundaryDialog = () => {
    setBoundaryDialog(null);
    setIsEditingBoundary(false);
    setIsDrawingFarm(false);
    setIsDrawingPlot(false);
  };

  const handleStartEditPlot = (plot: any) => {
    const points = fromGeoJsonGeometry(plot.geometry);
    setEditingPlot(plot);
    setEditPlotName(plot.name || "");
    setEditPlotCrop(plot.crop || "");
    setEditPlotArea(plot.area_acres ?? "");
    setEditPlotGeometry(points);
  };

  const handleSaveEditPlot = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!editingPlot) return;
    if (!editPlotName.trim()) {
      alert(t("plotNameRequired"));
      return;
    }
    if (editPlotGeometry.length > 0 && editPlotGeometry.length < 3) {
      alert(t("minimumPlotBoundaryPoints"));
      return;
    }
    if (
      editPlotGeometry.length >= 3 &&
      farmBoundary.length >= 3 &&
      editPlotGeometry.some((point) => !pointInsideOrOnPolygon(point, farmBoundary))
    ) {
      alert(t("plotBoundaryMustBeInsideFarm"));
      return;
    }

    updatePlotMutation.mutate({
      id: editingPlot.id,
      plotData: {
        name: editPlotName.trim(),
        crop: editPlotCrop.trim() || null,
        area_acres: editPlotArea !== "" ? Number(editPlotArea) : null,
        geometry: editPlotGeometry.length >= 3 ? toGeoJsonPolygon(editPlotGeometry) : null,
        reset_geometry: editPlotGeometry.length === 0,
      },
    });
  };

  const handleCreatePlot = (e: React.FormEvent) => {
    e.preventDefault();
    savePlot();
  };

  const savePlot = () => {
    if (farmBoundary.length < 3) {
      alert(t("drawFarmBoundaryFirst"));
      return;
    }
    if (newPlotGeometry.length < 3 || newPlotGeometry.some((point) => !pointInsideOrOnPolygon(point, farmBoundary))) {
      alert(t("minimumPlotBoundaryPoints"));
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
      return saveFarm(updatedPayload, token!);
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
      alert(t("minimumFarmBoundaryPoints"));
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
          <div className="mb-5 flex items-center gap-3 rounded-sm border border-farmer-200 bg-farmer-50 p-3 text-sm font-semibold text-farmer-800 dark:border-farmer-800 dark:bg-farmer-900/60 dark:text-farmer-200">
            <CheckCircle2 size={18} />
            <span>{t("farmUpdatedSuccess")}</span>
          </div>
        )}

        <div className="space-y-5">
        <Input label={t("farmName")} leadingIcon={<Sprout size={16} />} type="text" value={farmName} onChange={(e) => setFarmName(e.target.value)} required />

        <Input label={t("locationRegion")} leadingIcon={<MapPin size={16} />} type="text" value={location} onChange={(e) => setLocation(e.target.value)} placeholder={t("farmLocationPlaceholder")} required />

        <Input label={t("totalFarmArea")} type="number" step="any" value={area} onChange={(e) => setArea(Number(e.target.value))} required />

        <div className="grid gap-5 sm:grid-cols-2">
          <Input label={t("gpsLatitude")} leadingIcon={<MapPin size={16} />} type="number" step="any" value={lat} onChange={(e) => setLat(Number(e.target.value))} required />
          <Input label={t("gpsLongitude")} leadingIcon={<MapPin size={16} />} type="number" step="any" value={lon} onChange={(e) => setLon(Number(e.target.value))} required />
        </div>

        <Input label={t("cropHistory")} type="text" value={cropHistory} onChange={(e) => setCropHistory(e.target.value)} placeholder={t("cropHistoryPlaceholder")} />

        <div className="rounded-sm border border-farmer-200 bg-farmer-50 p-4 dark:border-farmer-800 dark:bg-farmer-900/60">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h3 className="font-display text-xl text-farmer-800 dark:text-farmer-200">{t("farmBoundary")}</h3>
              <p className="mt-1 text-xs text-muted dark:text-farmer-100/80">{t("farmBoundaryDesc")}</p>
            </div>
            <div className="flex flex-wrap gap-2">
              <button type="button" onClick={() => openBoundaryDialog("farm")} className="rounded-sm border border-line bg-surface px-3 py-2 text-xs font-semibold text-ink hover:bg-canvas transition-colors">
                {farmBoundary.length >= 3 ? t("editBoundary") : t("createBoundary")}
              </button>
              {farmBoundary.length > 0 && <button type="button" onClick={() => setFarmBoundary([])} className="rounded-sm border border-red-200 px-3 py-2 text-xs font-semibold text-danger dark:border-red-900/60 dark:bg-red-950/40 dark:text-rose-300 hover:bg-red-50 dark:hover:bg-red-950/70 transition-colors">{t("clearBoundary")}</button>}
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
        
        {plotSuccessMessage && (
          <div className="mt-4 flex items-center gap-3 rounded-sm border border-farmer-200 bg-farmer-50 p-3 text-sm font-semibold text-farmer-800 dark:border-farmer-800 dark:bg-farmer-900/60 dark:text-farmer-200">
            <CheckCircle2 size={18} />
            <span>{plotSuccessMessage}</span>
          </div>
        )}

        <div className="mt-6 space-y-3">
          {farmData?.plots?.map((plot: any) => {
            const hasBoundary = Boolean(plot.geometry?.coordinates?.length);
            return (
              <div key={plot.id} className="flex flex-wrap items-center justify-between gap-4 rounded-sm border border-line bg-canvas p-4">
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <strong className="truncate text-base font-semibold text-ink">{plot.name}</strong>
                    {hasBoundary ? (
                      <span className="inline-flex items-center gap-1 rounded-xs bg-farmer-100 px-2 py-0.5 text-[0.65rem] font-semibold text-farmer-800 dark:bg-farmer-900/60 dark:text-farmer-200">
                        <MapIcon size={12} /> {t("boundaryDefined")}
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 rounded-xs bg-amber-100 px-2 py-0.5 text-[0.65rem] font-semibold text-amber-800 dark:bg-amber-900/40 dark:text-amber-200">
                        {t("noBoundaryDefined")}
                      </span>
                    )}
                  </div>
                  <span className="mt-1 block text-xs text-muted">
                    {t("crop")}: {plot.crop ? translateCrop(plot.crop, language) : t("unknown")} · {t("areaLabel")}: {plot.area_acres ? `${plot.area_acres} ${t("areaUnit")}` : t("unknown")}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => handleStartEditPlot(plot)}
                    className="inline-flex items-center gap-1.5 rounded-sm border border-line bg-surface px-3 py-1.5 text-xs font-semibold text-ink hover:bg-canvas transition-colors"
                  >
                    <Pencil size={14} />
                    <span>{t("edit")}</span>
                  </button>
                  <button 
                    type="button"
                    onClick={() => {
                      if (confirm(t("confirmDeletePlot"))) {
                        deletePlotMutation.mutate(plot.id);
                      }
                    }}
                    disabled={deletePlotMutation.isPending}
                    className="rounded-sm border border-red-200/80 bg-red-50 p-2 text-danger hover:bg-red-100 dark:border-red-900/60 dark:bg-red-950/40 dark:text-red-400 dark:hover:bg-red-900/40 transition-colors"
                    title={t("delete")}
                    aria-label={t("delete")}
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>
            );
          })}
          {(!farmData?.plots || farmData.plots.length === 0) && (
            <div className="rounded-sm bg-canvas p-8 text-center text-sm text-muted">
              {t("noPlotsConfigured")}
            </div>
          )}
        </div>

        <form onSubmit={handleCreatePlot} className="mt-8 rounded-sm border border-dashed border-farmer-300 bg-farmer-50 dark:border-farmer-700 dark:bg-farmer-900/40 p-5">
          <h3 className="font-display text-xl text-farmer-800 dark:text-farmer-200">{t("addNewPlot")}</h3>
          <div className="mt-5 grid gap-5 sm:grid-cols-3">
            <Input label={t("plotName")} type="text" value={newPlotName} onChange={e => setNewPlotName(e.target.value)} placeholder={t("plotNamePlaceholder")} required />
            <Input label={t("currentCrop")} type="text" value={newPlotCrop} onChange={e => setNewPlotCrop(e.target.value)} placeholder={t("cropExamplePlaceholder")} />
            <Input label={t("plotArea")} type="number" step="any" value={newPlotArea} onChange={e => setNewPlotArea(e.target.value ? Number(e.target.value) : "")} placeholder={t("optionalPlaceholder")} />
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
                  className="inline-flex items-center gap-1.5 rounded-sm border border-expert-100 bg-expert-50 px-3 py-1.5 text-xs font-semibold text-expert-700 disabled:cursor-not-allowed disabled:opacity-60 dark:border-cyan-800/60 dark:bg-cyan-950/40 dark:text-cyan-200"
                >
                  <Navigation2 size={14} className={isLocating ? 'animate-spin' : ''} />
                  {isLocating ? t("locating") : t("myLocation")}
                </button>
                {/* Layer Toggle */}
                <div className="flex overflow-hidden rounded-sm border border-line">
                  <button
                    type="button"
                    onClick={() => setMapLayer('satellite')}
                    className={`inline-flex items-center gap-1 px-3 py-1.5 text-xs font-semibold transition-colors ${mapLayer === 'satellite' ? 'bg-farmer-600 text-white dark:bg-farmer-500 dark:text-farmer-950 font-bold shadow-xs' : 'bg-canvas text-muted hover:text-ink hover:bg-surface'}`}
                  >
                    <Satellite size={13} /> {t("satellite")}
                  </button>
                  <button
                    type="button"
                    onClick={() => setMapLayer('street')}
                    className={`inline-flex items-center gap-1 border-l border-line px-3 py-1.5 text-xs font-semibold transition-colors ${mapLayer === 'street' ? 'bg-farmer-600 text-white dark:bg-farmer-500 dark:text-farmer-950 font-bold shadow-xs' : 'bg-canvas text-muted hover:text-ink hover:bg-surface'}`}
                  >
                    <MapIcon size={13} /> {t("street")}
                  </button>
                </div>
                {newPlotGeometry.length > 0 && (
                  <button type="button" onClick={() => setNewPlotGeometry([])} className="inline-flex items-center gap-1 rounded-sm border border-red-200 px-3 py-1.5 text-xs font-semibold text-danger hover:bg-red-50 dark:border-red-900/60 dark:bg-red-950/40 dark:text-red-400 dark:hover:bg-red-900/40">
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

      {/* Edit Plot Modal */}
      {editingPlot && boundaryDialog !== "edit_plot" && (
        <div className="fixed inset-0 z-[90] flex items-center justify-center bg-ink/50 p-4" role="dialog" aria-modal="true" aria-label={t("editPlot")}>
          <div className="flex max-h-[92vh] w-full max-w-lg flex-col overflow-hidden rounded-md border border-line bg-surface shadow-lift">
            <div className="flex items-center justify-between border-b border-line p-4">
              <div>
                <h2 className="font-display text-xl text-ink">{t("editPlot")}</h2>
                <p className="mt-1 text-xs text-muted">{t("editPlotSubtitle")}</p>
              </div>
              <button
                type="button"
                onClick={() => setEditingPlot(null)}
                className="rounded-sm p-1.5 text-muted hover:bg-canvas hover:text-ink transition-colors"
                aria-label={t("close")}
              >
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleSaveEditPlot} className="flex-1 overflow-y-auto p-5 space-y-4 custom-scrollbar">
              <Input
                label={t("plotName")}
                type="text"
                value={editPlotName}
                onChange={(e) => setEditPlotName(e.target.value)}
                placeholder={t("plotNamePlaceholder")}
                required
              />

              <Input
                label={t("currentCrop")}
                type="text"
                value={editPlotCrop}
                onChange={(e) => setEditPlotCrop(e.target.value)}
                placeholder={t("cropExamplePlaceholder")}
              />

              <Input
                label={t("plotArea")}
                type="number"
                step="any"
                value={editPlotArea}
                onChange={(e) => setEditPlotArea(e.target.value ? Number(e.target.value) : "")}
                placeholder={t("optionalPlaceholder")}
              />

              <div className="rounded-sm border border-line bg-canvas p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold uppercase tracking-wider text-muted flex items-center gap-1.5">
                    <MapIcon size={14} /> {t("plotBoundary")}
                  </span>
                  <span className="text-xs font-medium text-ink">
                    {editPlotGeometry.length >= 3
                      ? `${editPlotGeometry.length} ${t("boundaryPointsCount")}`
                      : t("noBoundaryDefined")}
                  </span>
                </div>
                <p className="text-xs text-muted">{t("plotBoundaryDesc")}</p>
                <div className="pt-2 flex flex-wrap gap-2">
                  <button
                    type="button"
                    onClick={() => openBoundaryDialog("edit_plot")}
                    className="inline-flex items-center gap-1.5 rounded-sm border border-farmer-700 bg-farmer-50 px-3 py-1.5 text-xs font-semibold text-farmer-800 dark:border-farmer-500 dark:bg-farmer-950/50 dark:text-farmer-200 hover:bg-farmer-100 transition-colors"
                  >
                    <MapIcon size={14} />
                    <span>{editPlotGeometry.length >= 3 ? t("editPlotBoundary") : t("createPlotBoundary")}</span>
                  </button>
                  {editPlotGeometry.length > 0 && (
                    <button
                      type="button"
                      onClick={() => setEditPlotGeometry([])}
                      className="inline-flex items-center gap-1 rounded-sm border border-red-200 px-3 py-1.5 text-xs font-semibold text-danger hover:bg-red-50 dark:border-red-900/60 dark:bg-red-950/40 dark:text-red-400 transition-colors"
                    >
                      <RotateCcw size={13} />
                      <span>{t("clearBoundary")}</span>
                    </button>
                  )}
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-line">
                <button
                  type="button"
                  onClick={() => setEditingPlot(null)}
                  className="rounded-sm border border-line px-4 py-2 text-sm font-semibold text-ink hover:bg-canvas transition-colors"
                >
                  {t("cancel")}
                </button>
                <Button type="submit" disabled={updatePlotMutation.isPending || !editPlotName.trim()}>
                  <Save size={16} />
                  <span>{updatePlotMutation.isPending ? t("updating") : t("save")}</span>
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="flex justify-end border-t border-line pt-5">
        <Button type="button" onClick={() => setShowBoundaryOverview(true)}>
          <MapIcon size={18} /> {t("seeBoundaries")}
        </Button>
      </div>

      {boundaryDialog && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-ink/50 p-4" role="dialog" aria-modal="true" aria-label={`${t(boundaryDialog === "farm" ? "farm" : "plotOrdinal")} ${t("boundaryEditor")}`}>
          <div className="flex max-h-[92vh] w-full max-w-5xl flex-col overflow-hidden rounded-md border border-line bg-surface shadow-lift">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line p-4">
              <div>
                <h2 className="font-display text-2xl text-ink">
                  {boundaryDialog === "farm"
                    ? t("farmBoundary")
                    : boundaryDialog === "edit_plot"
                    ? `${t("editPlotBoundary")}: ${editPlotName || editingPlot?.name}`
                    : t("plotBoundary")}
                </h2>
                <p className="mt-1 text-xs text-muted">{isEditingBoundary ? t("boundaryEditInstructions") : t("boundaryMapInstructions")}</p>
              </div>
              <div className="flex flex-wrap gap-2">
                <button type="button" onClick={() => setIsEditingBoundary((editing) => !editing)} className={`rounded-sm px-3 py-2 text-xs font-semibold ${isEditingBoundary ? "bg-farmer-700 text-white dark:bg-farmer-600" : "border border-line bg-surface text-ink"}`}>
                  {isEditingBoundary ? t("stopEditing") : t("editBoundaryBtn")}
                </button>
                <button type="button" onClick={handleLocate} disabled={isLocating} className="inline-flex items-center gap-1.5 rounded-sm border border-expert-100 bg-expert-50 px-3 py-2 text-xs font-semibold text-expert-700 disabled:opacity-60 dark:border-cyan-800/60 dark:bg-cyan-950/40 dark:text-cyan-200">
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
                  drawingPoints={boundaryDialog === "farm" ? farmBoundary : boundaryDialog === "edit_plot" ? editPlotGeometry : newPlotGeometry}
                  currentLocation={currentLocation}
                  drawingActive={isEditingBoundary}
                  plotDrawingActive={boundaryDialog === "plot" || boundaryDialog === "edit_plot"}
                  plots={boundaryDialog === "edit_plot" ? farmData?.plots?.filter((p: any) => p.id !== editingPlot?.id) : farmData?.plots}
                  showPlots={boundaryDialog === "plot" || boundaryDialog === "edit_plot"}
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
              <button
                type="button"
                onClick={() => {
                  if (boundaryDialog === "edit_plot" && editingPlot) {
                    setEditPlotGeometry(fromGeoJsonGeometry(editingPlot.geometry));
                  }
                  closeBoundaryDialog();
                }}
                className="rounded-sm border border-line px-4 py-2 text-sm font-semibold text-ink"
              >
                {t("cancel")}
              </button>
              {boundaryDialog === "farm" ? (
                <Button type="button" onClick={saveFarmBoundary} disabled={mutation.isPending || farmBoundary.length < 3}>
                  {mutation.isPending ? t("saving") : t("saveFarmBoundary")}
                </Button>
              ) : boundaryDialog === "edit_plot" ? (
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => {
                      if (editPlotGeometry.length > 0 && editPlotGeometry.length < 3) {
                        alert(t("minimumPlotBoundaryPoints"));
                        return;
                      }
                      if (
                        editPlotGeometry.length >= 3 &&
                        farmBoundary.length >= 3 &&
                        editPlotGeometry.some((point) => !pointInsideOrOnPolygon(point, farmBoundary))
                      ) {
                        alert(t("plotBoundaryMustBeInsideFarm"));
                        return;
                      }
                      setBoundaryDialog(null);
                    }}
                    className="rounded-sm border border-line bg-surface px-4 py-2 text-sm font-semibold text-ink hover:bg-canvas transition-colors"
                  >
                    {t("doneEditingBoundary")}
                  </button>
                  <Button
                    type="button"
                    onClick={() => handleSaveEditPlot()}
                    disabled={updatePlotMutation.isPending || (editPlotGeometry.length > 0 && editPlotGeometry.length < 3) || !editPlotName.trim()}
                  >
                    {updatePlotMutation.isPending ? t("updating") : t("save")}
                  </Button>
                </div>
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
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-ink/50 p-4" role="dialog" aria-modal="true"         aria-label={t("farmPlotMapLabel")}>
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
                <span className="inline-flex items-center gap-2"><span className="h-3 w-3 rounded-sm border-2 border-teal-700 bg-teal-300/40" /> {t("farmBoundary")}</span>
                <span className="inline-flex items-center gap-2"><span className="h-3 w-3 rounded-sm border-2 border-blue-600 bg-blue-400/60" /> {t("plotOrdinal")} 1</span>
                <span className="inline-flex items-center gap-2"><span className="h-3 w-3 rounded-sm border-2 border-red-600 bg-red-400/60" /> {t("plotOrdinal")} 2</span>
                <span className="text-muted">{t("additionalPlotsLegend")}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      

      

      </div>
  );
}
