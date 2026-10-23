import { contractBlobRequest, contractRequest } from "./contract";
import type { components } from "./generated/openapi";
import type { AdminMetrics, FeedbackLog, AdminUsersResponse } from "./types";

export const adminMetrics = async (token: string): Promise<AdminMetrics> => {
  return contractRequest("/api/v1/admin/metrics", "get", {}, token);
};

export const datasetSummary = (token: string) =>
  contractRequest("/api/v1/admin/dataset/summary", "get", {}, token);

export const modelHealth = (token: string) =>
  contractRequest("/api/v1/admin/models/health", "get", {}, token);

export const readAdminConfig = (token: string) =>
  contractRequest("/api/v1/admin/config", "get", {}, token);

export const updateAdminConfig = (
  token: string,
  config: components["schemas"]["ConfigPayload"],
) =>
  contractRequest("/api/v1/admin/config", "put", { data: config }, token);

export const purgeDatabase = (token: string) =>
  contractRequest(
    "/api/v1/admin/purge",
    "delete",
    {
      query: { confirmation: "DELETE" },
    },
    token,
  );

export const purgeBlobs = (token: string) =>
  contractRequest("/api/v1/admin/blobs", "delete", {}, token);

export const adminFeedback = async (token: string): Promise<FeedbackLog[]> => {
  return contractRequest("/api/v1/admin/feedback", "get", {}, token);
};

export const reviewFeedback = async (
  token: string,
  feedbackId: number,
  status: "approved" | "rejected",
): Promise<void> => {
  await contractRequest(
    "/api/v1/feedback/{feedback_id}/review",
    "post",
    { pathParams: { feedback_id: feedbackId }, data: { status } },
    token,
  );
};

export const getAdminUsers = async (
  token: string,
  params?: { skip?: number; limit?: number; role?: string; search?: string }
): Promise<AdminUsersResponse> => {
  return contractRequest(
    "/api/v1/admin/users",
    "get",
    {
      query: {
        skip: params?.skip,
        limit: params?.limit,
        role: params?.role && params.role !== "all" ? params.role : undefined,
        search: params?.search,
      },
    },
    token,
  );
};

export const updateUserRole = async (
  token: string,
  userId: string,
  role: "farmer" | "expert" | "admin",
  reason?: string
): Promise<{ status: string; user_id: string; old_role: string; new_role: string }> => {
  return contractRequest(
    "/api/v1/admin/users/{target_user_id}/role",
    "patch",
    {
      pathParams: { target_user_id: userId },
      data: { role, reason },
    },
    token,
  );
};

export const updateAdminUser = async (
  token: string,
  userId: string,
  payload: { role?: "farmer" | "expert" | "admin"; phone?: string; name?: string; reason?: string }
): Promise<{
  status: string;
  user_id: string;
  name?: string;
  phone: string | null;
  role: string;
  old_role: string;
  new_role: string;
}> => {
  return contractRequest(
    "/api/v1/admin/users/{target_user_id}",
    "patch",
    {
      pathParams: { target_user_id: userId },
      data: payload,
    },
    token,
  );
};

export const rollbackModel = async (
  token: string,
  modelKey: string,
  targetVersion?: string
): Promise<{
  status: "rolled_back";
  model_key: string;
  previous_version: string | null;
  active_version: string;
  storage: "postgresql_database";
}> => {
  return contractRequest(
    "/api/v1/admin/models/rollback",
    "post",
    {
      data: { model_key: modelKey, target_version: targetVersion },
    },
    token,
  );
};

export const triggerWeatherRisk = async (
  token: string,
): Promise<{ status: "success"; result: string }> => {
  return contractRequest(
    "/api/v1/admin/weather-risk/trigger",
    "post",
    {},
    token,
  );
};

export type DatasetExportRequest = {
  filters: {
    expert: boolean;
    farmer: boolean;
    crop?: string;
    status?: "added_to_dataset" | "all" | "pending_review" | "rejected";
  };
  split: { train: number; val: number; test: number };
  format: "PyTorch Folder" | "JSON Manifest";
  imageTarget: "raw" | "preprocessed";
  replay_ratio?: number;
  include_replay_buffer?: boolean;
};

export const exportDataset = (token: string, payload: DatasetExportRequest, download?: boolean) =>
  contractBlobRequest(
    "/api/v1/admin/dataset/export",
    "post",
    {
      query: download !== undefined ? { download } : undefined,
      data: {
        ...payload,
        filters: { ...payload.filters, status: payload.filters.status ?? "all" },
        replay_ratio: payload.replay_ratio ?? 0.7,
        include_replay_buffer: payload.include_replay_buffer ?? true,
      },
    },
    token,
  );
