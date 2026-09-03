import { request } from "./client";
import type { Farm } from "./types";

export async function getFarm(token: string) {
  return request<Farm>("/farm", {}, token);
}
export async function saveFarm(farm: Omit<Farm, "id">, token: string) {
  return request<Farm>(
    "/farm",
    {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(farm),
    },
    token,
  );
}

export async function createPlot(plot: { name: string, crop: string | null, area_acres: number | null }, token: string) {
  return request("/farm/plots", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(plot),
  }, token);
}

export async function updatePlot(id: number, plot: { name: string, crop: string | null, area_acres: number | null }, token: string) {
  return request(`/farm/plots/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(plot),
  }, token);
}

export async function deletePlot(id: number, token: string) {
  return request(`/farm/plots/${id}`, {
    method: "DELETE",
  }, token);
}
