import { contractRequest } from "./contract";

export type ExpertQueueItem = {
  review_id: number;
  prediction_id: number;
  status: string;
  crop: string | null;
  disease: string | null;
  disease_conf: number | null;
  severity_pct: number | null;
  claimed_by?: string | null;
  claimed_at?: string | null;
  created_at: string | null;
};

export type ExpertReviewDetail = {
  review_id: number;
  prediction_id: number;
  status: string;
  decision: string | null;
  corrected_disease: string | null;
  farmer_guidance: string | null;
  internal_note: string | null;
  raw_path: string | null;
  processed_path: string | null;
  raw_url?: string | null;
  processed_url?: string | null;
  crop: string | null;
  disease: string | null;
  disease_conf: number | null;
  severity_pct: number | null;
  created_at: string | null;
};

export async function getExpertQueue(token: string) {
  return contractRequest("/api/v1/expert/queue", "get", {}, token);
}

export async function getExpertReview(reviewId: number, token: string, lang?: string) {
  return contractRequest(
    "/api/v1/expert/reviews/{review_id}",
    "get",
    { pathParams: { review_id: reviewId }, query: lang ? { lang } : undefined },
    token,
  );
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
  return contractRequest(
    "/api/v1/expert/reviews/{review_id}",
    "post",
    {
      pathParams: { review_id: reviewId },
      data: payload,
    },
    token,
  );
}
