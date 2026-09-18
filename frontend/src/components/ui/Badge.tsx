import type { HTMLAttributes, ReactNode } from "react";

export type BadgeTone = "neutral" | "success" | "warning" | "danger" | "info";

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: BadgeTone;
  children: ReactNode;
}

const toneClasses: Record<BadgeTone, string> = {
  neutral: "bg-canvas text-muted",
  success: "bg-farmer-100 text-farmer-800",
  warning: "bg-admin-100 text-admin-700",
  danger: "bg-red-50 text-danger",
  info: "bg-expert-100 text-expert-700",
};

export default function Badge({ tone = "neutral", children, className = "", ...props }: BadgeProps) {
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold ${toneClasses[tone]} ${className}`} {...props}>
      {children}
    </span>
  );
}
