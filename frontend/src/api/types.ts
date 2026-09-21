
export interface Plot {
  id: number;
  name: string;
  crop?: string;
  area_acres?: number;
  status: string;
  geometry?: Record<string, unknown> | null;
}

﻿export type Pest = { label?: string; confidence?: number };
export type Prediction = {
  prediction_id?: number;
  request_id: string;
  image: {
    raw_path?: string;
    processed_path?: string;
    quality_score?: number;
    leaf_detected?: boolean;
  };
  crop: { label?: string; confidence?: number };
  disease: { label?: string; confidence?: number; model_used?: string };
  severity: { percent?: number; bucket?: string };
  pests: Pest[];
  weather: {
    temperature_celsius?: number;
    humidity_percent?: number;
    condition?: string;
    status?: string;
  };
  recommendation: {
    immediate_action?: string;
    treatment?: string;
    prevention?: string;
    monitoring?: string;
    safety_disclaimer?: string;
  };
  status: string | Record<string, string>;
  notes: string[];
  expert_review_data?: {
    decision: string;
    corrected_disease?: string;
    farmer_guidance?: string;
  };
  historical_images?: {
    raw_path?: string;
    processed_path?: string;
  }[];
  follow_up?: Prediction;
  translations?: Record<string, any>;
  schema_version?: string;
  provenance?: Record<string, any>;
  total_duration_ms?: number;
  stages?: Record<string, any>;
};

export type Profile = {
  id: string;
  name?: string;
  email?: string;
  phone?: string;
  language: string;
  role: string;
  location?: string;
  latitude?: number;
  longitude?: number;
  crop_history: string[];
  plots: Plot[];
  farm_name?: string;
  farm_area_acres?: number;
};
export type Farm = {
  id?: number;
  name: string;
  location: string;
  area_acres: number;
  latitude?: number;
  longitude?: number;
  crop_history: string[];
  boundary?: Record<string, unknown> | null;
  plots: Plot[];
};

export type WeatherData = {
  status: string;
  temperature_celsius?: number;
  humidity_percent?: number;
  wind_speed_mps?: number;
  pressure_hpa?: number;
  cloudiness_percent?: number;
  condition?: string;
  city?: string;
  advisory?: string;
  translated_advisory?: string;
  translations?: Record<string, string>;
};

export type AdminMetrics = {
  total_predictions: number;
  total_scans?: number;
  total_feedback?: number;
  accuracy_rate_pct: number | null; 
  feedback_accuracy_pct?: number | null; 
  avg_crop_confidence: number | null;
  avg_disease_confidence: number | null;
  avg_quality_score: number | null;
  crop_distribution: Record<string, number>;
  disease_distribution: Record<string, number>;
};
export type FeedbackLog = {
  id: number;
  prediction_id: number;
  crop: string | null;
  disease: string | null;
  is_correct: boolean;
  farmer_note: string | null;
  created_at: string;
};

