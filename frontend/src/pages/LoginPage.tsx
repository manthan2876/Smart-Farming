import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { LogIn, Sprout } from "lucide-react";
import { motion } from "motion/react";
import { Button, Input } from "../components/ui";
import { getDefaultRouteForRole } from "../lib/routes";

export default function LoginPage() {
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { user, isAuthenticated, signIn } = useAuth();

  // If already authenticated, redirect to role's designated landing route
  useEffect(() => {
    if (isAuthenticated && user) {
      navigate(getDefaultRouteForRole(user.role), { replace: true });
    }
  }, [isAuthenticated, user, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const loggedUser = await signIn(identifier, password);
      const targetRoute = getDefaultRouteForRole(loggedUser.role);
      navigate(targetRoute, { replace: true });
    } catch (err: any) {
      setError(err.message || "Failed to login. Please check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid min-h-screen bg-canvas lg:grid-cols-2">
        <div className="flex items-center justify-center px-5 py-12 sm:px-10 lg:px-16">
          <motion.div 
            className="w-full max-w-md"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
          >
            <Sprout className="mb-7 text-farmer-700" size={40} />
            <h2 className="font-display text-3xl text-ink sm:text-4xl">Welcome Back</h2>
            <p className="mt-2 text-xs font-bold uppercase tracking-[0.14em] text-muted">[ACCESS YOUR ACCOUNT]</p>

            {error && <div className="mt-6 rounded-sm border border-red-100 bg-red-50 p-3 text-sm text-danger">{error}</div>}

            <form onSubmit={handleSubmit} className="mt-8 space-y-5">
              <Input id="login-identifier" label="Email or Phone" 
                  type="text" 
                  value={identifier} 
                  onChange={(e) => setIdentifier(e.target.value)}
                  placeholder="farmer@example.com"
                  required />
              <Input id="login-password" label="Password"
                  type="password" 
                  value={password} 
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required />
              <Button type="submit" disabled={loading} className="mt-2 w-full">
                <LogIn size={17} />
                {loading ? "Authenticating..." : "Sign In"}
              </Button>
            </form>

            <div className="mt-8 text-center text-sm text-muted">
              Don't have an account? <Link className="font-bold text-farmer-700 underline" to="/auth/register">Create Account</Link>
              <div className="mt-5"><Link className="text-muted hover:text-ink" to="/">← Back to Home</Link></div>
            </div>
          </motion.div>
        </div>
        <div className="relative hidden min-h-[26rem] items-end overflow-hidden bg-ink bg-[url('https://images.unsplash.com/photo-1592982537447-6f29fbdb9e31?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center p-10 lg:flex lg:p-16">
          <div className="absolute inset-0 bg-gradient-to-t from-ink via-ink/30 to-transparent" />
          <div className="relative z-10 text-white">
            <h2 className="max-w-xl font-display text-4xl leading-tight">"Data-driven decisions start here. Monitor, analyze, and protect your harvest."</h2>
            <p className="mt-5 text-xs font-bold uppercase tracking-[0.14em] text-farmer-300">[SMART FARMING INTELLIGENCE]</p>
          </div>
        </div>
    </div>
  );
}
