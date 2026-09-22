/**
 * Returns the default primary landing route based on the user's platform role.
 * - Admin -> /admin/metrics (Platform Control Center)
 * - Expert -> /admin/expert (Agronomy Desk Review Queue)
 * - Farmer -> /dashboard (Farmer Diagnostic Dashboard)
 */
export function getDefaultRouteForRole(role?: string): string {
  const normalized = (role || "").toLowerCase().trim();
  if (normalized === "admin") {
    return "/admin/metrics";
  }
  if (normalized === "expert") {
    return "/admin/expert";
  }
  return "/dashboard";
}

