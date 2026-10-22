import { track } from "@vercel/analytics";

/**
 * Safe wrapper around Vercel Analytics custom event tracking.
 * Vercel Analytics only accepts string, number, boolean, null, undefined as property values.
 * Strictly avoids PII (passwords, phone numbers, email addresses, exact GPS coordinates).
 */
export function trackEvent(
  name: string,
  properties?: Record<string, string | number | boolean | null | undefined>
) {
  try {
    track(name, properties);
  } catch (error) {
    if (import.meta.env.DEV) {
      console.debug(`[Analytics event: ${name}]`, error);
    }
  }
}

/**
 * Typed domain events for Smart Farming actions
 */
export const analytics = {
  scanInitiated: (props: { has_plot: boolean; language?: string; is_offline?: boolean }) => {
    trackEvent("scan_initiated", props);
  },

  predictionViewed: (props: { crop?: string; disease?: string; confidence?: number }) => {
    trackEvent("prediction_viewed", {
      crop: props.crop || "unknown",
      disease: props.disease || "unknown",
      confidence_pct: props.confidence !== undefined ? Math.round(props.confidence * 100) : undefined,
    });
  },

  feedbackSubmitted: (vote: "up" | "down", crop?: string, disease?: string) => {
    trackEvent("feedback_submitted", {
      vote,
      crop: crop || "unknown",
      disease: disease || "unknown",
    });
  },

  expertReviewRequested: (crop?: string, disease?: string) => {
    trackEvent("expert_review_requested", {
      crop: crop || "unknown",
      disease: disease || "unknown",
    });
  },

  languageChanged: (language: string) => {
    trackEvent("language_changed", { language });
  },

  offlineSyncCompleted: (count: number) => {
    trackEvent("offline_sync_completed", { count });
  },

  authAction: (action: "login" | "register" | "guest_login" | "logout") => {
    trackEvent("auth_action", { action });
  },
};

