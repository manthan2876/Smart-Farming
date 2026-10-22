import type { components } from "./generated/openapi";
import { contractRequest } from "./contract";

export type CropListResponse = components["schemas"]["CropListResponse"];

export const fetchSupportedCrops = async (token?: string): Promise<string[]> => {
  const res = await contractRequest("/api/v1/crops", "get", {}, token);
  return res.crops || [];
};
