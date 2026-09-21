import { request, requestBlob } from "./client";
import { AdminMetrics, FeedbackLog } from "./types";

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
