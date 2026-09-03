import { request } from "./client";

export type ExpertQueueItem = {
  review_id: number;
  prediction_id: number;
  status: string;
  crop: string;
  disease: string;
  disease_conf: number;
  severity_pct: number;
  created_at: string;
};

export type ExpertReviewDetail = {
  review_id: number;
  prediction_id: number;
  status: string;
  decision: string | null;
  corrected_disease: string | null;
  farmer_guidance: string | null;
  internal_note: string | null;
  raw_path: string;
  processed_path: string | null;
  crop: string;
  disease: string;
  disease_conf: number;
  severity_pct: number;
  created_at: string;
};

export async function getExpertQueue(token: string) {
  return request<ExpertQueueItem[]>("/expert/queue", {}, token);
}

export async function getExpertReview(reviewId: number, token: string) {
  return request<ExpertReviewDetail>("/expert/reviews/" + reviewId, {}, token);
}

export async function submitExpertReview(
  reviewId: number,
  payload: {
    action: "Approve" | "Override / Correct Findings" | "Request Rescan";
    corrected_disease?: string;
    corrected_severity?: string;
    pest_verified?: boolean;
    farmer_guidance?: string;
    internal_note?: string;
    add_to_retraining?: boolean;
  },
  token: string
) {
  return request<{status: string, review_id: number}>(
    "/expert/reviews/" + reviewId,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    },
    token
  );
}
