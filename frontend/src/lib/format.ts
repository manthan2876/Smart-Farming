export function confidence(value = 0) {
  return `${Math.round(value * 100)}%`;
}
export function severityTone(value = 0) {
  return value > 60 ? "critical" : value > 30 ? "watch" : "calm";
}
export const imagePath = "/aphids_tomato.jpeg";
