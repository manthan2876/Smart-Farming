import { useEffect, useState } from "react";
import { Check, MapPin, Save, Sprout } from "lucide-react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { profile, updateProfile } from "../api/auth";
import { useAuth } from "../context/AuthContext";

export function ProfilePage() {
  const { token, setLanguage } = useAuth();
  const client = useQueryClient();
  const query = useQuery({
    queryKey: ["profile", token],
    queryFn: () => profile(token!),
    enabled: Boolean(token),
  });
  const farmer = query.data;
  const [form, setForm] = useState({
    name: "",
    location: "",
    farmName: "",
    farmArea: 0,
    language: "English",
  });
  useEffect(() => {
    if (farmer)
      setForm({
        name: farmer.name ?? "",
        location: farmer.location ?? "",
        farmName: farmer.farm_name ?? "",
        farmArea: farmer.farm_area_acres ?? 0,
        language: farmer.language,
      });
  }, [farmer]);
  const mutation = useMutation({
    mutationFn: () =>
      updateProfile(
        {
          name: form.name,
          location: form.location,
          farm_name: form.farmName,
          farm_area_acres: form.farmArea,
          language: form.language,
        },
        token!,
      ),
    onSuccess: (data) => {
      client.setQueryData(["profile", token], data);
      setLanguage(data.language);
    },
  });
  if (!token)
    return (
      <section className="empty-state">
        <h1>Connect your farm account</h1>
        <p>Sign in to manage your profile and farm details.</p>
      </section>
    );
  return (
    <section className="profile-page">
      <div className="profile-hero">
        <div className="avatar profile-avatar">
          {form.name.slice(0, 2).toUpperCase() || "MP"}
        </div>
        <div>
          <p className="eyebrow">Farmer profile</p>
          <h1>{form.name || "Your farm profile"}</h1>
          <p>{farmer?.email ?? "Profile details"}</p>
        </div>
      </div>
      <form
        className="profile-form"
        onSubmit={(event) => {
          event.preventDefault();
          mutation.mutate();
        }}
      >
        <div className="profile-panel">
          <div className="panel-heading">
            <MapPin size={18} />
            <div>
              <p className="eyebrow">Personal information</p>
              <h3>About you</h3>
            </div>
          </div>
          <label>
            Full name
            <input
              required
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
          </label>
          <label>
            Location
            <input
              required
              value={form.location}
              onChange={(e) => setForm({ ...form, location: e.target.value })}
            />
          </label>
          <label>
            Preferred advice language
            <select
              value={form.language}
              onChange={(e) => setForm({ ...form, language: e.target.value })}
            >
              <option>English</option>
              <option>Gujarati</option>
              <option>Hindi</option>
            </select>
          </label>
        </div>
        <div className="profile-panel">
          <div className="panel-heading">
            <Sprout size={18} />
            <div>
              <p className="eyebrow">Farm information</p>
              <h3>Your growing ground</h3>
            </div>
          </div>
          <label>
            Farm name
            <input
              required
              value={form.farmName}
              onChange={(e) => setForm({ ...form, farmName: e.target.value })}
              placeholder="North plot farm"
            />
          </label>
          <label>
            Farm area in acres
            <input
              required
              type="number"
              min="0"
              step="0.1"
              value={form.farmArea}
              onChange={(e) =>
                setForm({ ...form, farmArea: Number(e.target.value) })
              }
            />
          </label>
          <div className="crop-chips">
            {(farmer?.crop_history?.length
              ? farmer.crop_history
              : ["Tomato", "Cotton"]
            ).map((crop) => (
              <span key={crop}>{crop}</span>
            ))}
          </div>
        </div>
        <button className="primary profile-save" disabled={mutation.isPending}>
          <Save size={16} />{" "}
          {mutation.isPending
            ? "Saving…"
            : mutation.isSuccess
              ? "Changes saved"
              : "Save changes"}
          {mutation.isSuccess && <Check size={16} />}
        </button>
      </form>
    </section>
  );
}
