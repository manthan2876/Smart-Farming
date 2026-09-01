import { request } from "./client";
import type { AdminMetrics, FeedbackLog } from "./types";

export async function adminMetrics(token: string): Promise<AdminMetrics> {
  return request<AdminMetrics>("/admin/metrics", {}, token);
}

export async function adminFeedback(
  token: string,
  page = 0,
  limit = 20,
): Promise<FeedbackLog[]> {
  return request<FeedbackLog[]>(
    `/admin/feedback?skip=${page * limit}&limit=${limit}`,
    {},
    token,
  );
}
