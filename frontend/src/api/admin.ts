import { request } from "./client";
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
