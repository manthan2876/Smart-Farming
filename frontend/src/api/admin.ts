import { request, requestBlob } from "./client";
import { AdminMetrics, FeedbackLog, AdminUsersResponse } from "./types";

export const adminMetrics = async (token: string): Promise<AdminMetrics> => {
  return request<AdminMetrics>("/admin/metrics", {}, token);
};

export const adminFeedback = async (token: string): Promise<FeedbackLog[]> => {
  return request<FeedbackLog[]>("/admin/feedback", {}, token);
};

export const reviewFeedback = async (
  token: string,
  feedbackId: number,
  status: "approved" | "rejected",
): Promise<void> => {
  await request(`/feedback/${feedbackId}/review`, {
    method: 'POST',
    body: JSON.stringify({ status })
  }, token);
};

export const getAdminUsers = async (
  token: string,
  params?: { skip?: number; limit?: number; role?: string; search?: string }
): Promise<AdminUsersResponse> => {
  const query = new URLSearchParams();
  if (params?.skip !== undefined) query.set("skip", params.skip.toString());
  if (params?.limit !== undefined) query.set("limit", params.limit.toString());
  if (params?.role && params.role !== "all") query.set("role", params.role);
  if (params?.search) query.set("search", params.search);
  const qStr = query.toString();
  return request<AdminUsersResponse>(`/admin/users${qStr ? `?${qStr}` : ""}`, {}, token);
};

export const updateUserRole = async (
  token: string,
  userId: string,
  role: "farmer" | "expert" | "admin",
  reason?: string
): Promise<{ status: string; user_id: string; old_role: string; new_role: string }> => {
  return request<{ status: string; user_id: string; old_role: string; new_role: string }>(
    `/admin/users/${userId}/role`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ role, reason }),
    },
    token
  );
};

export const rollbackModel = async (
  token: string,
  modelKey: string,
  targetVersion?: string
): Promise<{ status: string; model_key: string; previous_version: string; active_version: string }> => {
  return request(
    "/admin/models/rollback",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model_key: modelKey, target_version: targetVersion }),
    },
    token
  );
};

export const triggerWeatherRisk = async (token: string): Promise<{ status: string; farms_evaluated: number; alerts_generated: number }> => {
  return request(
    "/admin/weather-risk/trigger",
    {
      method: "POST",
    },
    token
  );
};

export type DatasetExportRequest = {
  filters: { expert: boolean; farmer: boolean; crop?: string; status?: string };
  split: { train: number; val: number; test: number };
  format: "PyTorch Folder" | "JSON Manifest";
  imageTarget: "raw" | "preprocessed";
};

export const exportDataset = (token: string, payload: DatasetExportRequest) =>
  requestBlob("/admin/dataset/export", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  }, token);

