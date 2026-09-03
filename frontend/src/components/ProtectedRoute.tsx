import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

interface ProtectedRouteProps {
  children: React.ReactNode;
  adminOnly?: boolean;
  strictAdminOnly?: boolean;
}

export default function ProtectedRoute({ children, adminOnly = false, strictAdminOnly = false }: ProtectedRouteProps) {
  const { isAuthenticated, user, isLoading } = useAuth();

  // Show a loading state while checking token/session status
  if (isLoading) {
    return (
      <div className="loading-screen" style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh" }}>
        <div className="spinner"></div>
        <p>Loading session...</p>
      </div>
    );
  }

  // If not logged in, redirect to login page
  if (!isAuthenticated) {
    return <Navigate to="/auth/login" replace />;
  }

  // If route requires admin rights and user is not an admin, redirect to dashboard
  if (strictAdminOnly && user?.role !== "admin") {
    return <Navigate to="/dashboard" replace />;
  }

  if (adminOnly && user?.role !== "admin" && user?.role !== "expert") {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
}