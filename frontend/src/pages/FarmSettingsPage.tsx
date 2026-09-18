import { useState, useEffect, useRef } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "../context/AuthContext";
import { request } from "../api/client";
import { createPlot, deletePlot } from "../api/farm";
import { MapPin, Save, CheckCircle2, Sprout, AlertTriangle, Trash2, RotateCcw, Map as MapIcon, Navigation2, Satellite } from "lucide-react";
import { MapContainer, TileLayer, Polygon, CircleMarker, Polyline, useMapEvents, useMap } from "react-leaflet";
import type { LatLng } from "leaflet";
import { motion } from "motion/react";
import { Button, Card, Input } from "../components/ui";

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

  const [newPlotName, setNewPlotName] = useState("");
  const [newPlotCrop, setNewPlotCrop] = useState("");
    const [newPlotArea, setNewPlotArea] = useState<number | "">("");
  const [newPlotGeometry, setNewPlotGeometry] = useState<[number, number][]>([]);
  const [mapLayer, setMapLayer] = useState<'satellite' | 'street'>('satellite');
  const [isLocating, setIsLocating] = useState(false);

  // Tile layer URLs
  const SATELLITE_URL = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}";
  const SATELLITE_ATTR = "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community";
  const STREET_URL = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
  const STREET_ATTR = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';

  // ─── Map Controller: fixes tile sizing + exposes flyTo ref ─────────────────
  function MapController({ flyToRef }: { flyToRef: React.MutableRefObject<((latlng: [number, number], zoom?: number) => void) | null> }) {
    const map = useMap();

    useEffect(() => {
      // Must run after the DOM has painted — requestAnimationFrame guarantees this
      const frame = requestAnimationFrame(() => {
        map.invalidateSize({ animate: false });
      });
      return () => cancelAnimationFrame(frame);
    }, [map]);

    // Expose flyTo so the "Locate Me" button outside MapContainer can fly the map
    flyToRef.current = (latlng, zoom = 17) =>
      map.flyTo(latlng, zoom, { animate: true, duration: 1.2 });

    return null;
  }

  function InteractivePlotDrawer({
    points,
    setPoints,
  }: {
    points: [number, number][];
    setPoints: React.Dispatch<React.SetStateAction<[number, number][]>>;
  }) {
    // Click on map background → add a new vertex
    useMapEvents({
      click(e) {
        // Ignore clicks that bubble from markers/polylines
        if ((e.originalEvent.target as HTMLElement).closest?.(".leaflet-interactive")) return;
        setPoints(prev => [...prev, [e.latlng.lat, e.latlng.lng]]);
      },
    });

    const deletePoint = (idx: number) => {
      setPoints(prev => prev.filter((_, i) => i !== idx));
    };

    // Click on a segment between point[i] and point[i+1] → insert midpoint between them
    const insertMidpoint = (i: number, latlng: LatLng) => {
      setPoints(prev => {
        const next = [...prev];
        next.splice(i + 1, 0, [latlng.lat, latlng.lng]);
        return next;
      });
    };

    return (
      <>
        {/* Filled polygon when we have 3+ points */}
        {points.length >= 3 && (
          <Polygon positions={points} color="#16a34a" weight={2} fillOpacity={0.25} />
        )}

        {/* Editable segment lines — clicking inserts a mid-point */}
        {points.map((pt, i) => {
          const next = points[(i + 1) % points.length];
          if (i === points.length - 1 && points.length < 3) return null; // don't close if < 3 pts
          return (
            <Polyline
              key={`seg-${i}`}
              positions={[pt, next]}
              color="#16a34a"
              weight={4}
              opacity={0.6}
              eventHandlers={{
                click(e) {
                  e.originalEvent.stopPropagation();
                  insertMidpoint(i, e.latlng);
                },
              }}
            />
          );
        })}

        {/* Vertex markers — double-click deletes, regular click is noop */}
        {points.map((pt, i) => (
          <CircleMarker
            key={`pt-${i}`}
            center={pt}
            radius={7}
            color="#fff"
            weight={2}
            fillColor="#16a34a"
            fillOpacity={1}
            eventHandlers={{
              dblclick(e) {
                e.originalEvent.stopPropagation();
                deletePoint(i);
              },
            }}
          />
        ))}
      </>
    );
  }

  // Ref to store the Leaflet flyTo function — set by MapController inside the map
  const flyToRef = useRef<((latlng: [number, number], zoom?: number) => void) | null>(null);

  // GPS Locate Me handler
  const handleLocate = () => {
    if (!navigator.geolocation) {
      alert("Geolocation is not supported by your browser.");
      return;
    }
    setIsLocating(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const latlng: [number, number] = [pos.coords.latitude, pos.coords.longitude];
        flyToRef.current?.(latlng, 17);
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
    }
  });

  const deletePlotMutation = useMutation({
    mutationFn: async (plotId: number) => deletePlot(plotId, token!),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["farmSettings"] })
  });

  const handleCreatePlot = (e: React.FormEvent) => {
    e.preventDefault();
    createPlotMutation.mutate({
      name: newPlotName,
      crop: newPlotCrop || null,
      area_acres: newPlotArea ? Number(newPlotArea) : null,
      geometry: newPlotGeometry.length > 2 ? { type: "Polygon", coordinates: [newPlotGeometry] } : null
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

  if (isLoading) return <div className="flex min-h-[40vh] items-center justify-center"><div className="h-6 w-6 animate-spin rounded-full border-2 border-farmer-200 border-t-farmer-700" /></div>;

  return (
    <div className="space-y-6 pb-12">
      <div>
        <h1 className="font-display text-3xl text-ink sm:text-4xl">Farm Configuration & Plot Settings</h1>
        <p className="mt-3 max-w-3xl leading-7 text-muted">Manage your GPS coordinates, total acreage, and historic crop rotation cycles.</p>
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
            <span>Farm settings updated successfully!</span>
          </div>
        )}

        <div className="space-y-5">
        <Input label="Farm Name / Identifier" leadingIcon={<Sprout size={16} />} type="text" value={farmName} onChange={(e) => setFarmName(e.target.value)} required />

        <Input label="Location / Region" leadingIcon={<MapPin size={16} />} type="text" value={location} onChange={(e) => setLocation(e.target.value)} placeholder="e.g. Bhavnagar, Gujarat" required />

        <Input label="Total Farm Area (Acres)" type="number" step="any" value={area} onChange={(e) => setArea(Number(e.target.value))} required />

        <div className="grid gap-5 sm:grid-cols-2">
          <Input label="GPS Latitude" leadingIcon={<MapPin size={16} />} type="number" step="any" value={lat} onChange={(e) => setLat(Number(e.target.value))} required />
          <Input label="GPS Longitude" leadingIcon={<MapPin size={16} />} type="number" step="any" value={lon} onChange={(e) => setLon(Number(e.target.value))} required />
        </div>

        <Input label="Crop History (Comma separated)" type="text" value={cropHistory} onChange={(e) => setCropHistory(e.target.value)} placeholder="e.g. Cotton, Groundnut, Wheat" />

        <Button type="submit" disabled={mutation.isPending}>
          <Save size={18} /> {mutation.isPending ? "Saving..." : "Save Farm Configuration"}
        </Button>
        </div>
      </motion.form>

      
      <motion.div 
        className="rounded-md border border-line bg-surface p-5 shadow-soft sm:p-6"
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <h2 className="font-display text-2xl text-ink">Manage Farm Plots</h2>
        <p className="mt-2 text-sm leading-6 text-muted">Organize your farm into distinct plots or fields to track disease progression accurately.</p>
        
        <div className="mt-6 space-y-3">
          {farmData?.plots?.map((plot: any) => (
            <div key={plot.id} className="flex items-center justify-between gap-4 rounded-sm border border-line bg-canvas p-4">
              <div>
                <strong className="block text-base font-semibold text-ink">{plot.name}</strong>
                <span className="mt-1 block text-xs text-muted">
                  Crop: {plot.crop || "Unknown"} &bull; Area: {plot.area_acres ? `${plot.area_acres} acres` : "Unknown"}
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
              No plots configured yet.
            </div>
          )}
        </div>

        <form onSubmit={handleCreatePlot} className="mt-8 rounded-sm border border-dashed border-farmer-300 bg-farmer-50 p-5">
          <h3 className="font-display text-xl text-farmer-800">Add New Plot</h3>
          <div className="mt-5 grid gap-5 sm:grid-cols-3">
            <Input label="Plot Name / ID" type="text" value={newPlotName} onChange={e => setNewPlotName(e.target.value)} placeholder="e.g. North Field" required />
            <Input label="Current Crop" type="text" value={newPlotCrop} onChange={e => setNewPlotCrop(e.target.value)} placeholder="e.g. Cotton" />
            <Input label="Area (Acres)" type="number" step="any" value={newPlotArea} onChange={e => setNewPlotArea(e.target.value ? Number(e.target.value) : "")} placeholder="Optional" />
          </div>
          <div className="mt-6">
            {/* Map toolbar */}
            <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
              <label className="flex items-center gap-2 text-sm font-semibold text-ink">
                <MapIcon size={16} /> Draw Plot Boundaries
              </label>
              <div className="flex flex-wrap items-center gap-2">
                {/* GPS Locate Button */}
                <button
                  type="button"
                  onClick={handleLocate}
                  disabled={isLocating}
                  className="inline-flex items-center gap-1.5 rounded-sm border border-expert-100 bg-expert-50 px-3 py-1.5 text-xs font-semibold text-expert-700 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  <Navigation2 size={14} className={isLocating ? 'animate-spin' : ''} />
                  {isLocating ? 'Locating...' : 'My Location'}
                </button>
                {/* Layer Toggle */}
                <div className="flex overflow-hidden rounded-sm border border-line">
                  <button
                    type="button"
                    onClick={() => setMapLayer('satellite')}
                    className={`inline-flex items-center gap-1 px-3 py-1.5 text-xs font-semibold ${mapLayer === 'satellite' ? 'bg-ink text-white' : 'bg-canvas text-muted'}`}
                  >
                    <Satellite size={13} /> Satellite
                  </button>
                  <button
                    type="button"
                    onClick={() => setMapLayer('street')}
                    className={`inline-flex items-center gap-1 border-l border-line px-3 py-1.5 text-xs font-semibold ${mapLayer === 'street' ? 'bg-ink text-white' : 'bg-canvas text-muted'}`}
                  >
                    <MapIcon size={13} /> Street
                  </button>
                </div>
                {/* Clear Drawing */}
                {newPlotGeometry.length > 0 && (
                  <button type="button" onClick={() => setNewPlotGeometry([])} className="inline-flex items-center gap-1 rounded-sm border border-red-200 px-3 py-1.5 text-xs font-semibold text-danger hover:bg-red-50">
                    <RotateCcw size={13} /> Clear
                  </button>
                )}
              </div>
            </div>

            {/* Map container — must be a plain block div so Leaflet reads clientWidth/clientHeight correctly */}
            <div className="h-96 w-full overflow-hidden rounded-sm border border-line">
              <MapContainer
                center={[lat || 21.0, lon || 72.0]}
                zoom={15}
                className="h-full w-full"
                doubleClickZoom={false}
              >
                <TileLayer
                  key={mapLayer}
                  url={mapLayer === 'satellite' ? SATELLITE_URL : STREET_URL}
                  attribution={mapLayer === 'satellite' ? SATELLITE_ATTR : STREET_ATTR}
                  maxZoom={mapLayer === 'satellite' ? 19 : 19}
                />
                <MapController flyToRef={flyToRef} />
                {/* Saved plot boundaries in grey */}
                {farmData?.plots?.map((plot: any) =>
                  plot.geometry?.coordinates ? (
                    <Polygon key={plot.id} positions={plot.geometry.coordinates[0]} color="#f8fafc" weight={2} fillOpacity={0.1} />
                  ) : null
                )}
                {/* Interactive drawing layer */}
                <InteractivePlotDrawer
                  points={newPlotGeometry}
                  setPoints={setNewPlotGeometry}
                />
              </MapContainer>
            </div>
            <p className="mt-2 text-xs leading-5 text-muted">
              <strong>Click</strong> empty map to add vertex &nbsp;·&nbsp;
              <strong>Click a line</strong> to insert vertex &nbsp;·&nbsp;
              <strong>Double-click a point</strong> to delete it
            </p>
          </div>
          <Button type="submit" className="mt-5 bg-farmer-600 hover:bg-farmer-700" disabled={createPlotMutation.isPending || !newPlotName}>
            {createPlotMutation.isPending ? "Adding..." : "+ Add Plot"}
          </Button>
        </form>
      </motion.div>

      

      

    </div>
  );
}
