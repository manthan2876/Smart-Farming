import { request } from "./client";
import type { Farm } from "./types";

export async function getFarm(token: string) {
  return request<Farm>("/auth/farm", {}, token);
}
export async function saveFarm(farm: Omit<Farm, "id">, token: string) {
  return request<Farm>(
    "/auth/farm",
    {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(farm),
    },
    token,
  );
}
