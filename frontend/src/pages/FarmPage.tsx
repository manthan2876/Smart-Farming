import { useEffect, useState } from "react";
import { ArrowUpRight, MapPin, Save, Sprout } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getFarm, saveFarm } from "../api/farm";
import type { Farm, Prediction, Profile } from "../api/types";
import { useAuth } from "../context/AuthContext";

const emptyFarm: Omit<Farm, "id"> = {
  name: "",
  location: "",
  area_acres: 0,
  crop_history: ["Tomato"],
};
export function FarmPage({
  history,
  profile,
}: {
  history: Prediction[];
  profile?: Profile | null;
}) {
  const navigate = useNavigate();
  const { token } = useAuth();
  const client = useQueryClient();
  const query = useQuery({
    queryKey: ["farm", token],
    queryFn: () => getFarm(token!),
    enabled: Boolean(token),
  });
  const [farm, setFarm] = useState<Omit<Farm, "id">>(emptyFarm);
  useEffect(() => {
    if (query.data) {
      const { id: _id, ...saved } = query.data;
      setFarm(saved);
    }
  }, [query.data]);
  const mutation = useMutation({
    mutationFn: () => saveFarm(farm, token!),
    onSuccess: (data) => {
      client.setQueryData(["farm", token], data);
      const { id: _id, ...saved } = data;
      setFarm(saved);
    },
  });
  const latest = history[0];
  if (!token)
    return (
      <section className="empty-state">
        <h1>Connect your farm account</h1>
        <p>Sign in to create and manage your plots.</p>
      </section>
    );
  return (
    <section className="farm-page">
      <div className="section-head">
        <div>
          <p className="eyebrow">Your growing ground</p>
          <h1>My farm</h1>
        </div>
        <span className="farm-save-state">
          {mutation.isSuccess
            ? "Saved just now"
            : query.isLoading
              ? "Loading farm…"
              : "Local farm profile"}
        </span>
      </div>
      <form
        onSubmit={(event) => {
          event.preventDefault();
          mutation.mutate();
        }}
      >
        <div className="farm-overview">
          <label>
            <span className="eyebrow">Farm name</span>
            <input
              required
              value={farm.name ?? ""}
              onChange={(e) => setFarm({ ...farm, name: e.target.value })}
              placeholder="North plot farm"
            />
          </label>
          <label>
            <span className="eyebrow">Home location</span>
            <input
              required
              value={farm.location}
              onChange={(e) => setFarm({ ...farm, location: e.target.value })}
              placeholder="Anand, Gujarat"
            />
          </label>
          <label>
            <span className="eyebrow">Total area · acres</span>
            <input
              required
              type="number"
              min="0"
              step="0.1"
              value={farm.area_acres ?? 0}
              onChange={(e) =>
                setFarm({ ...farm, area_acres: Number(e.target.value) })
              }
            />
          </label>
        </div>
        <div className="section-head compact">
          <div>
            <p className="eyebrow">Your zones</p>
            <h2>Plots at a glance</h2>
          </div>
          <button className="primary" disabled={mutation.isPending}>
            <Save size={15} /> {mutation.isPending ? "Saving…" : "Save farm"}
          </button>
        </div>
      </form>
      <div className="plot-grid">
        <Plot
          name="North Plot"
          crop={farm.crop_history[0] ?? "Tomato"}
          area={`${farm.area_acres || 0} acres`}
          health={
            latest?.severity.percent && latest.severity.percent > 30
              ? "Attention"
              : "Healthy"
          }
          latest={latest?.disease.label ?? "No recent scan"}
        />
        <Plot
          name="Add another plot"
          crop="Set a crop"
          area="Add area"
          health="Healthy"
          latest="Ready to configure"
          empty
        />
      </div>
      <div className="crop-history">
        <Sprout size={19} />
        <div>
          <p className="eyebrow">Crop history</p>
          <h3>{farm.crop_history.join(" · ") || "Add your crops"}</h3>
          <p>Use your crop history to make recommendations more relevant.</p>
        </div>
        <ArrowUpRight size={17} />
      </div>
    </section>
  );
}
function Plot({
  name,
  crop,
  area,
  health,
  latest,
  empty = false,
}: {
  name: string;
  crop: string;
  area: string;
  health: string;
  latest: string;
  empty?: boolean;
}) {
  const navigate = useNavigate();
  return (
    <article className={`plot-card ${empty ? "plot-empty" : ""}`}>
      <div className="plot-header">
        <span
          className={`plot-health ${health === "Healthy" ? "good" : "watch"}`}
        >
          {health}
        </span>
        <MapPin size={16} />
      </div>
      <h3>{name}</h3>
      <p className="plot-crop">{crop}</p>
      <div className="plot-data">
        <span>
          Area <b>{area}</b>
        </span>
        <span>
          Latest <b>{latest}</b>
        </span>
      </div>
      <button type="button" onClick={() => navigate("/history")}>
        View plot history <ArrowUpRight size={15} />
      </button>
    </article>
  );
}
