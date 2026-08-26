import { Bell, Check, Languages, Type } from "lucide-react";
import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { updateProfile } from "../api/auth";
import { useAuth } from "../context/AuthContext";

export function SettingsPage() {
  const { user, token, setLanguage } = useAuth();
  const [language, setSelectedLanguage] = useState(user?.language ?? "English");
  const [largeText, setLargeText] = useState(false);
  const mutation = useMutation({
    mutationFn: () => updateProfile({ language }, token!),
    onSuccess: (result) => setLanguage(result.language),
  });
  return (
    <section className="settings-page">
      <div className="section-head">
        <div>
          <p className="eyebrow">Make it yours</p>
          <h1>Settings</h1>
        </div>
        <button
          className="primary"
          onClick={() => mutation.mutate()}
          disabled={mutation.isPending}
        >
          <Check size={15} /> {mutation.isSuccess ? "Saved" : "Save settings"}
        </button>
      </div>
      <div className="settings-list">
        <div className="setting-row">
          <span className="setting-icon">
            <Languages size={18} />
          </span>
          <div>
            <h3>Advice language</h3>
            <p>Recommendations and voice output</p>
          </div>
          <select
            value={language}
            onChange={(e) => setSelectedLanguage(e.target.value)}
          >
            <option>English</option>
            <option>Gujarati</option>
            <option>Hindi</option>
          </select>
        </div>
        <div className="setting-row">
          <span className="setting-icon">
            <Bell size={18} />
          </span>
          <div>
            <h3>Farm alerts</h3>
            <p>Disease, weather, and expert updates</p>
          </div>
          <label className="toggle">
            <input type="checkbox" defaultChecked />
            <i />
          </label>
        </div>
        <div className="setting-row">
          <span className="setting-icon">
            <Type size={18} />
          </span>
          <div>
            <h3>Larger text</h3>
            <p>Increase reading size across the app</p>
          </div>
          <label className="toggle">
            <input
              type="checkbox"
              checked={largeText}
              onChange={(e) => setLargeText(e.target.checked)}
            />
            <i />
          </label>
        </div>
      </div>
    </section>
  );
}
