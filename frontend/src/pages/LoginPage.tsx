import { FormEvent, useState } from "react";
import { ArrowUpRight, Leaf, LockKeyhole } from "lucide-react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export function LoginPage() {
  const { signIn } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [form, setForm] = useState({
    identifier: "",
    password: "",
  });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await signIn(form.identifier, form.password);
      navigate(searchParams.get("next") ?? "/");
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "Unable to connect to your farm account.",
      );
    } finally {
      setBusy(false);
    }
  }
  return (
    <main className="auth-page">
      <div className="auth-visual">
        <span className="brand">
          <span className="brand-mark">
            <Leaf size={18} />
          </span>
          <span>
            fieldnote<small>smart farming</small>
          </span>
        </span>
        <div>
          <p className="eyebrow">A quieter way to farm</p>
          <h1>
            Read the field
            <br />
            <em>before it speaks louder.</em>
          </h1>
          <p>
            One place for leaf scans, crop history, and advice grounded in your
            farm.
          </p>
        </div>
        <span className="auth-quote">
          “The best diagnosis is the one that arrives in time.”
        </span>
      </div>
      <form className="auth-form" onSubmit={submit}>
        <span className="round-icon">
          <LockKeyhole size={18} />
        </span>
        <p className="eyebrow">{"Farmer access"}</p>
        <h2>{"Welcome back to the field."}</h2>
        <p className="auth-copy">
          {"Sign in to sync live scans and recommendations."}
        </p>
        <label>
          Email or phone
          <input
            required
            value={form.identifier}
            onChange={(e) => setForm({ ...form, identifier: e.target.value })}
            placeholder="you@example.com"
          />
        </label>
        <label>
          Password
          <input
            required
            minLength={8}
            type="password"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
          />
        </label>
        {error && <p className="auth-error">{error}</p>}
        <button className="primary auth-submit" disabled={busy}>
          {busy ? (
            "Connecting…"
          ) : (
            <>
              {"Sign in"}
              <ArrowUpRight size={16} />
            </>
          )}
        </button>
        <p className="auth-switch">
          {"New to Fieldnote? "}
          <Link to={"/auth/register"}>{"Create one"}</Link>
        </p>
      </form>
    </main>
  );
}
