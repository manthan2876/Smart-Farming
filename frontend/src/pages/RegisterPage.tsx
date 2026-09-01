import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { User, Mail, Phone, Lock, Globe, MapPin, UserPlus, AlertCircle } from "lucide-react";
import { motion } from "framer-motion";

export default function RegisterPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [language, setLanguage] = useState("English");
  const [location, setLocation] = useState("Bhavnagar");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { signUp } = useAuth();
  const navigate = useNavigate();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

   try {
      await signUp({
        name,
        email: email || undefined,
        phone: phone || undefined,
        password,
        language,
        location,
      });
      navigate("/dashboard");
    } catch (err: any) {
      setError(err.message || "Registration failed. Please check inputs.");
      setLoading(false);
    }
  };

  return (
    <div className="auth-page-layout">
      <motion.div 
        className="auth-card card register-card"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
      >
        <div className="auth-header">
          <div className="logo-icon-lg">🌾</div>
          <h2>Create Farmer Account</h2>
          <p>Join the smart farming ecosystem</p>
        </div>

        {error && (
          <div className="alert alert-error">
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleRegister} className="auth-form">
          <div className="form-group">
            <label><User size={16} /> Full Name</label>
            <input 
              type="text" 
              value={name} 
              onChange={(e) => setName(e.target.value)} 
              placeholder="Manthan Kuvadiya"
              className="form-control"
              required 
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label><Mail size={16} /> Email Address</label>
              <input 
                type="email" 
                value={email} 
                onChange={(e) => setEmail(e.target.value)} 
                placeholder="farmer@domain.com"
                className="form-control"
              />
            </div>
            <div className="form-group">
              <label><Phone size={16} /> Phone Number</label>
              <input 
                type="text" 
                value={phone} 
                onChange={(e) => setPhone(e.target.value)} 
                placeholder="+919876543210"
                className="form-control"
              />
            </div>
          </div>

          <div className="form-group">
            <label><Lock size={16} /> Password</label>
            <input 
              type="password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              placeholder="••••••••"
              className="form-control"
              required 
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label><Globe size={16} /> Language Preference</label>
              <select 
                value={language} 
                onChange={(e) => setLanguage(e.target.value)}
                className="form-control"
              >
                <option value="English">English</option>
                <option value="Hindi">Hindi (हिंदी)</option>
                <option value="Gujarati">Gujarati (ગુજરાતી)</option>
              </select>
            </div>
            <div className="form-group">
              <label><MapPin size={16} /> Farm Location</label>
              <input 
                type="text" 
                value={location} 
                onChange={(e) => setLocation(e.target.value)} 
                placeholder="Bhavnagar"
                className="form-control"
              />
            </div>
          </div>

          <button type="submit" className="btn btn-primary btn-full btn-glow mt-3" disabled={loading}>
            <UserPlus size={18} /> {loading ? "Creating Account..." : "Register & Continue"}
          </button>
        </form>

        <div className="auth-footer mt-3">
          <p>Already have an account? <Link to="/auth/login">Sign In</Link></p>
          <p className="mt-1"><Link to="/">← Back to Home</Link></p>
        </div>
      </motion.div>
    </div>
  );
}