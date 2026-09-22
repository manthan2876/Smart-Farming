import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { UserPlus, Sprout } from "lucide-react";
import { motion } from "motion/react";
import { Button, Input } from "../components/ui";

import { getDefaultRouteForRole } from "../lib/routes";

export default function RegisterPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [language, setLanguage] = useState("English");
  const [location, setLocation] = useState("");
  
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { signUp } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const newUser = await signUp({ name, email, phone, password, language, location });
      navigate(getDefaultRouteForRole(newUser.role), { replace: true });
    } catch (err: any) {
      setError(err.message || "Failed to create account.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid min-h-screen bg-canvas lg:grid-cols-2">
        <div className="flex items-center justify-center px-5 py-10 sm:px-10 lg:px-16">
          <motion.div 
            className="w-full max-w-2xl"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
          >
            <Sprout className="mb-6 text-farmer-700" size={40} />
            <h2 className="font-display text-3xl text-ink sm:text-4xl">Create Account</h2>
            <p className="mt-2 text-xs font-bold uppercase tracking-[0.14em] text-muted">[JOIN THE ECOSYSTEM]</p>

            {error && <div className="mt-6 rounded-sm border border-red-100 bg-red-50 p-3 text-sm text-danger">{error}</div>}

            <form onSubmit={handleSubmit} className="mt-8 space-y-5">
              <Input id="register-name" label="Full Name" type="text" value={name} onChange={(e) => setName(e.target.value)} required />
              <div className="grid gap-5 sm:grid-cols-2">
                <Input id="register-email" label="Email Address" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
                <Input id="register-phone" label="Phone Number" type="text" value={phone} onChange={(e) => setPhone(e.target.value)} required />
              </div>
              <Input id="register-password" label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
              <div className="grid gap-5 sm:grid-cols-2">
                <label className="block space-y-2" htmlFor="register-language">
                  <span className="block text-sm font-semibold text-ink">Language</span>
                  <select id="register-language" className="min-h-11 w-full rounded-sm border border-line bg-surface px-3 text-sm text-ink focus:border-farmer-500 focus:outline-none focus:ring-4 focus:ring-farmer-100" value={language} onChange={(e) => setLanguage(e.target.value)}>
                    <option value="English">English</option>
                    <option value="Hindi">Hindi</option>
                    <option value="Gujarati">Gujarati</option>
                  </select>
                </label>
                <Input id="register-location" label="Location" type="text" value={location} onChange={(e) => setLocation(e.target.value)} required />
              </div>

              <Button type="submit" disabled={loading} className="mt-2 w-full">
                <UserPlus size={17} />
                {loading ? "Creating..." : "Register & Continue"}
              </Button>
            </form>

            <div className="mt-8 text-center text-sm text-muted">
              Already have an account? <Link className="font-bold text-farmer-700 underline" to="/auth/login">Sign In</Link>
            </div>
          </motion.div>
        </div>
        <div className="relative hidden min-h-[26rem] items-end overflow-hidden bg-ink bg-[url('https://images.unsplash.com/photo-1595841696650-622839b207ee?q=80&w=2069&auto=format&fit=crop')] bg-cover bg-center p-10 lg:flex lg:p-16">
          <div className="absolute inset-0 bg-gradient-to-t from-ink via-ink/30 to-transparent" />
          <div className="relative z-10 text-white">
            <h2 className="max-w-xl font-display text-4xl leading-tight">"Smarter agriculture built for the next generation of farming."</h2>
            <p className="mt-5 text-xs font-bold uppercase tracking-[0.14em] text-farmer-300">[CROP INTELLIGENCE PLATFORM]</p>
          </div>
        </div>
    </div>
  );
}
