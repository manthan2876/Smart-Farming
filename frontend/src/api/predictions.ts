import { request } from "./client";
import type { Prediction, WeatherData } from "./types";

export async function history(token: string, limit = 20, offset = 0) {
  return request<Prediction[]>(`/history?limit=${limit}&offset=${offset}`, {}, token);
}

export async function getPrediction(id: string, token: string) {
  return request<Prediction>(`/predictions/${id}`, {}, token);
}
export async function predict(
  file: File,
  metadata: { location: string; language: string; plot_id?: number },
  token: string,
) {
  const body = new FormData();
  body.append("file", file);
  body.append("location", metadata.location);
  body.append("language", metadata.language);
  if (metadata.plot_id) body.append("plot_id", metadata.plot_id.toString());
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
export async function weather(lat: number, lon: number, token: string) {
  return request<WeatherData>(`/weather?lat=${lat}&lon=${lon}`, {}, token);
}


export async function rescan(id: number | string, file: File, token: string, plot_id?: number) {
  const body = new FormData();
  body.append("file", file);
  return request<Prediction>(`/predictions/${id}/rescan`, { method: "POST", body }, token);
}
