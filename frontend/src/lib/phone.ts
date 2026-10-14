/**
 * Phone number normalization and validation utility for Smart Farming.
 * Ensures consistent E.164 formatting (+[country_code][number]) before communicating
 * with Supabase Auth or SMS providers, protecting against invalid calls and wasted SMS credits.
 */

export const DEFAULT_COUNTRY_CODE = "+91"; // India default for Smart Farming farmers

/**
 * Normalizes user input into standard E.164 phone string.
 * Examples:
 *   "9999999999"      -> "+919999999999"
 *   "09999999999"     -> "+919999999999"
 *   "+91 99999 99999" -> "+919999999999"
 *   "+1 555-123-4567" -> "+15551234567"
 */
export function normalizePhoneNumber(raw: string, defaultCountryCode = DEFAULT_COUNTRY_CODE): string {
  if (!raw) return "";
  const cleaned = raw.replace(/[\s\-\(\)\.]/g, "").trim();
  if (!cleaned) return "";

  if (cleaned.startsWith("+")) {
    return cleaned;
  }
  if (cleaned.startsWith("00")) {
    return `+${cleaned.slice(2)}`;
  }
  if (cleaned.startsWith("0") && cleaned.length === 11) {
    return `${defaultCountryCode}${cleaned.slice(1)}`;
  }
  if (cleaned.length === 10 && /^\d{10}$/.test(cleaned)) {
    return `${defaultCountryCode}${cleaned}`;
  }
  return cleaned.startsWith("+") ? cleaned : `+${cleaned}`;
}

/**
 * Validates that the normalized string adheres to E.164 phone format.
 * Minimum 8 digits, maximum 15 digits according to ITU-T recommendation E.164.
 */
export function isValidPhoneNumber(phone: string): boolean {
  const normalized = normalizePhoneNumber(phone);
  return /^\+[1-9]\d{8,14}$/.test(normalized);
}

/**
 * Formats a phone number for user-friendly display.
 * E.g., "+919999999999" -> "+91 99999 99999"
 */
export function formatPhoneDisplay(raw: string): string {
  const normalized = normalizePhoneNumber(raw);
  if (normalized.startsWith("+91") && normalized.length === 13) {
    return `+91 ${normalized.slice(3, 8)} ${normalized.slice(8)}`;
  }
  return normalized;
}

