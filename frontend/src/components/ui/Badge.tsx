import type { HTMLAttributes, ReactNode } from "react";

export type BadgeTone = "neutral" | "success" | "warning" | "danger" | "info";

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: BadgeTone;
  children: ReactNode;
}

const toneClasses: Record<BadgeTone, string> = {
  neutral: "bg-canvas text-muted border border-line dark:bg-farmer-950/70 dark:text-farmer-200 dark:border-farmer-800/70",
  success: "bg-farmer-100 text-farmer-800 dark:bg-emerald-950/80 dark:text-emerald-300 dark:border dark:border-emerald-800/80",
  warning: "bg-amber-100 text-amber-800 dark:bg-amber-950/80 dark:text-amber-300 dark:border dark:border-amber-800/80",
  danger: "bg-red-50 text-danger dark:bg-rose-950/80 dark:text-rose-300 dark:border dark:border-rose-800/80",
  info: "bg-expert-100 text-expert-700 dark:bg-cyan-950/80 dark:text-cyan-300 dark:border dark:border-cyan-800/80",
};

export default function Badge({ tone = "neutral", children, className = "", ...props }: BadgeProps) {
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold ${toneClasses[tone]} ${className}`} {...props}>
      {children}
    </span>
  );
}
