import { contractRequest, contractRequestWithMeta } from "./contract";
import type { components } from "./generated/openapi";

type PredictionResponse = components["schemas"]["PredictionResponse"];

function numericPredictionId(id: number | string): number {
  const parsed = typeof id === "number" ? id : Number(id);
  if (!Number.isSafeInteger(parsed) || parsed < 1) {
    throw new Error("Prediction ID must be a positive integer.");
  }
  return parsed;
}

export async function history(token: string, limit = 20, offset = 0) {
  return contractRequest(
    "/api/v1/history",
    "get",
    { query: { limit, offset } },
    token,
  );
}

export async function historyWithMeta(
  token: string,
  params: { limit?: number; offset?: number; status?: string },
) {
  return contractRequestWithMeta("/api/v1/history", "get", {
    query: {
      limit: params.limit,
      offset: params.offset,
      status: params.status,
    },
  }, token);
}

export async function getPrediction(id: string, token: string, lang?: string) {
  return contractRequest(
    "/api/v1/predictions/{prediction_id}",
    "get",
    {
      pathParams: { prediction_id: numericPredictionId(id) },
      query: lang ? { lang } : undefined,
    },
    token,
  );
}

export async function predict(
  file: File,
  metadata: {
    location: string;
    language: string;
    plot_id?: number;
    lat?: number;
    lon?: number;
  },
  token: string,
): Promise<PredictionResponse> {
  const body = new FormData();
  body.append("file", file);
  body.append("location", metadata.location);
  body.append("language", metadata.language);
  if (metadata.plot_id !== undefined) body.append("plot_id", String(metadata.plot_id));
  if (metadata.lat !== undefined) body.append("lat", String(metadata.lat));
  if (metadata.lon !== undefined) body.append("lon", String(metadata.lon));
  return contractRequest("/api/v1/predict", "post", { body }, token);
}

export async function submitFeedback(
  predictionId: number,
  isCorrect: boolean,
  note: string,
  token: string,
) {
  return contractRequest("/api/v1/feedback", "post", {
    data: {
      prediction_id: predictionId,
      is_correct: isCorrect,
      farmer_note: note || null,
    },
  }, token);
}

export async function crops() {
  return contractRequest("/api/v1/crops", "get", {});
}

export async function weather(
  lat: number,
  lon: number,
  token: string,
  language?: string,
) {
  return contractRequest(
    "/api/v1/weather",
    "get",
    { query: { lat, lon, language } },
    token,
  );
}

export async function translateWeather(text: string, targetLanguage: string, token: string) {
  return contractRequest("/api/v1/weather/translate", "post", {
    data: { text, target_language: targetLanguage },
  }, token);
}

export async function textToSpeech(text: string, language: string, token: string) {
  return contractRequest("/api/v1/tts", "post", {
    data: { text, language },
  }, token);
}

export async function translatePrediction(id: number | string, targetLanguage: string, token: string) {
  return contractRequest(
    "/api/v1/predictions/{prediction_id}/translate",
    "post",
    {
      pathParams: { prediction_id: numericPredictionId(id) },
      query: { target_language: targetLanguage },
    },
    token,
  );
}

export async function rescan(
  id: number | string,
  file: File,
  token: string,
  plot_id?: number,
) {
  const body = new FormData();
  body.append("file", file);
  if (plot_id !== undefined) body.append("plot_id", String(plot_id));
  return contractRequest(
    "/api/v1/predictions/{prediction_id}/rescan",
    "post",
    {
      pathParams: { prediction_id: numericPredictionId(id) },
      body,
    },
    token,
  );
}

export async function requestExpertReview(id: string | number, token: string) {
  return contractRequest(
    "/api/v1/predictions/{prediction_id}/request-expert",
    "post",
    { pathParams: { prediction_id: numericPredictionId(id) } },
    token,
  );
}
