import { request } from "./client";
import type { Prediction } from "./types";

export async function history(token: string) {
  return request<Prediction[]>("/history?limit=20", {}, token);
}
export async function getPrediction(id: string, token: string) {
  return request<Prediction>(`/predictions/${id}`, {}, token);
}
export async function predict(
  file: File,
  metadata: { location: string; language: string },
  token: string,
) {
  const body = new FormData();
  body.append("file", file);
  body.append("location", metadata.location);
  body.append("language", metadata.language);
  return request<Prediction>("/predict", { method: "POST", body }, token);
}
export async function submitFeedback(
  predictionId: number,
  isCorrect: boolean,
  note: string,
  token: string,
) {
  return request(
    "/feedback",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prediction_id: predictionId,
        is_correct: isCorrect,
        farmer_note: note || null,
      }),
    },
    token,
  );
}
export async function crops() {
  return request<{ crops: string[] }>("/crops");
}
