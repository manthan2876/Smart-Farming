import { request } from "./client";

export interface AlertItem {
  id: number;
  prediction_id?: number | null;
  kind?: string;
  severity?: string;
  title: string;
  body: string;
  is_read: boolean;
  created_at: string;
}

export async function fetchAlerts(token: string, lang?: string): Promise<AlertItem[]> {
  const query = lang ? `?lang=${encodeURIComponent(lang)}` : "";
  return request<AlertItem[]>(`/alerts${query}`, {}, token);
}

export async function markAlertRead(alertId: number, token: string): Promise<{ status: string }> {
  return request<{ status: string }>(`/alerts/${alertId}/read`, { method: "POST" }, token);
}

export async function markAllAlertsRead(alerts: AlertItem[], token: string): Promise<void> {
  const unread = alerts.filter((a) => !a.is_read);
  await Promise.all(unread.map((a) => markAlertRead(a.id, token)));
}
