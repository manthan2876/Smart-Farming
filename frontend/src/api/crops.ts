import { request } from "./client";

export type CropListResponse = {
  crops: string[];
};

export const fetchSupportedCrops = async (token: string): Promise<string[]> => {
  const res = await request<CropListResponse>("/crops", {}, token);
  return res.crops || [];
};
