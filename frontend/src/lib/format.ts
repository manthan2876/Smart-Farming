import { Units } from "../i18n";

export function confidence(value = 0): string {
  return `${Math.round(value * 100)}%`;
}

export function severityTone(value = 0): "critical" | "watch" | "calm" {
  return value > 60 ? "critical" : value > 30 ? "watch" : "calm";
}

/**
 * Converts and formats temperature based on selected unit preference.
 */
export function formatTemperature(celsius?: number | null, units: Units = "Metric"): string {
  if (celsius == null) return "--";
  if (units === "Imperial") {
    const fahrenheit = (celsius * 9) / 5 + 32;
    return `${Math.round(fahrenheit)}°F`;
  }
  return `${Math.round(celsius)}°C`;
}

/**
 * Converts and formats wind speed based on selected unit preference.
 */
export function formatWindSpeed(speedMps?: number | null, units: Units = "Metric"): string {
  if (speedMps == null) return "--";
  if (units === "Imperial") {
    const mph = speedMps * 2.23694;
    return `${mph.toFixed(1)} mph`;
  }
  const kmh = speedMps * 3.6;
  return `${kmh.toFixed(1)} km/h`;
}

/**
 * Converts and formats land area based on selected unit preference.
 * Backend stores acres in user.farm.area_acres or farm_area_acres.
 */
export function formatArea(acres?: number | null, units: Units = "Metric"): string {
  if (acres == null) return "--";
  if (units === "Imperial") {
    return `${acres.toFixed(1)} acres`;
  }
  // 1 acre = 0.404686 hectares
  const ha = acres * 0.404686;
  return `${ha.toFixed(2)} ha`;
}
