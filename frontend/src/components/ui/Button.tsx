import type { ButtonHTMLAttributes, ReactNode } from "react";

export type ButtonVariant = "primary" | "secondary" | "ghost" | "danger";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: "sm" | "md" | "lg";
  children: ReactNode;
}

const variantClasses: Record<ButtonVariant, string> = {
  primary: "bg-farmer-700 text-white shadow-soft hover:bg-farmer-800",
  secondary: "border border-line bg-surface text-ink hover:border-farmer-300 hover:bg-farmer-50",
  ghost: "text-muted hover:bg-farmer-50 hover:text-ink",
  danger: "bg-danger text-white hover:bg-red-800",
};

const sizeClasses = {
  sm: "min-h-9 px-3 text-sm",
  md: "min-h-11 px-4 text-sm",
  lg: "min-h-13 px-5 text-base",
};

export default function Button({
  variant = "primary",
  size = "md",
  className = "",
  children,
  type = "button",
  ...props
}: ButtonProps) {
  return (
    <button
      type={type}
      className={`inline-flex items-center justify-center gap-2 rounded-sm font-semibold transition-colors disabled:cursor-not-allowed disabled:opacity-50 ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
