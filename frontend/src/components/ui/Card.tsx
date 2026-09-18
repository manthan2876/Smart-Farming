import type { HTMLAttributes, ReactNode } from "react";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  padding?: "none" | "sm" | "md" | "lg";
}

const paddingClasses = {
  none: "",
  sm: "p-4",
  md: "p-5 sm:p-6",
  lg: "p-6 sm:p-8",
};

export default function Card({ children, className = "", padding = "md", ...props }: CardProps) {
  return (
    <div
      className={`rounded-md border border-line bg-surface shadow-soft ${paddingClasses[padding]} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}
