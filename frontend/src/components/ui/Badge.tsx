import type { HTMLAttributes, ReactNode } from "react";

export type BadgeTone = "neutral" | "success" | "warning" | "danger" | "info";

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: BadgeTone;
  children: ReactNode;
}

const toneClasses: Record<BadgeTone, string> = {
  neutral: "bg-canvas text-muted border border-line dark:bg-farmer-950 dark:text-farmer-200 dark:border-farmer-800",
  success: "bg-farmer-100/70 text-farmer-800 border border-farmer-300 dark:bg-farmer-900/60 dark:text-farmer-200 dark:border-farmer-700",
  warning: "bg-amber-50 text-amber-900 border border-amber-300 dark:bg-amber-950/40 dark:text-amber-200 dark:border-amber-800",
  danger: "bg-red-50 text-red-900 border border-red-300 dark:bg-red-950/40 dark:text-red-200 dark:border-red-800",
  info: "bg-farmer-50 text-farmer-800 border border-farmer-200 dark:bg-farmer-900/40 dark:text-farmer-200 dark:border-farmer-800",
};

export default function Badge({ tone = "neutral", children, className = "", ...props }: BadgeProps) {
  return (
    <span className={`inline-flex items-center rounded-xs px-2 py-0.5 text-xs font-semibold ${toneClasses[tone]} ${className}`} {...props}>
      {children}
    </span>
  );
}
