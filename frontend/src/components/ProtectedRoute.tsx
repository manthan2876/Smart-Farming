import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { getDefaultRouteForRole } from "../lib/routes";

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
      <div className="flex min-h-screen items-center justify-center bg-canvas px-4 text-muted">
        <div className="flex items-center gap-3 rounded-md border border-line bg-surface px-5 py-4 shadow-soft">
          <div className="h-5 w-5 animate-spin rounded-full border-2 border-farmer-200 border-t-farmer-700" />
          <p className="text-sm font-semibold">Loading session...</p>
        </div>
      </div>
    );
  }

  // If not logged in, redirect to login page
  if (!isAuthenticated) {
    return <Navigate to="/auth/login" replace />;
  }

  // If route requires super-admin rights and user is not an admin, redirect to role's home
  if (strictAdminOnly && user?.role !== "admin") {
    return <Navigate to={getDefaultRouteForRole(user?.role)} replace />;
  }

  // If route requires admin or expert rights and user is neither, redirect to role's home
  if (adminOnly && user?.role !== "admin" && user?.role !== "expert") {
    return <Navigate to={getDefaultRouteForRole(user?.role)} replace />;
  }

  return <>{children}</>;
}