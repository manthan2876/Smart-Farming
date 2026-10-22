import type { components } from "./generated/openapi";
import { contractRequest } from "./contract";

export type AlertItem = components["schemas"]["AlertResponse"];

export async function fetchAlerts(token: string, lang?: string): Promise<AlertItem[]> {
  return contractRequest(
    "/api/v1/alerts",
    "get",
    { query: { lang } },
    token,
  );
}

export async function markAlertRead(
  alertId: number,
  token: string,
): Promise<components["schemas"]["AlertReadResponse"]> {
  return contractRequest(
    "/api/v1/alerts/{alert_id}/read",
    "post",
    { pathParams: { alert_id: alertId } },
    token,
  );
}

export async function markAllAlertsRead(alerts: AlertItem[], token: string): Promise<void> {
  const unread = alerts.filter((a) => !a.is_read);
  await Promise.all(unread.map((a) => markAlertRead(a.id, token)));
}
