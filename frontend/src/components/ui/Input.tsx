import { useState } from "react";
import type { InputHTMLAttributes, ReactNode } from "react";
import { Eye, EyeOff } from "lucide-react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  leadingIcon?: ReactNode;
  trailingIcon?: ReactNode;
  showPasswordToggle?: boolean;
}

export default function Input({
  label,
  error,
  leadingIcon,
  trailingIcon,
  showPasswordToggle,
  type,
  className = "",
  id,
  ...props
}: InputProps) {
  const isPassword = type === "password";
  const enableToggle = showPasswordToggle ?? isPassword;
  const [showPassword, setShowPassword] = useState(false);

  const effectiveType =
    isPassword && enableToggle ? (showPassword ? "text" : "password") : type;

  return (
    <label className="block space-y-2" htmlFor={id}>
      {label && <span className="block text-sm font-semibold text-ink">{label}</span>}
      <span className="relative block">
        {leadingIcon && (
          <span className="pointer-events-none absolute inset-y-0 left-3 flex items-center text-muted">
            {leadingIcon}
          </span>
        )}
        <input
          id={id}
          type={effectiveType}
          className={`min-h-11 w-full rounded-sm border border-line bg-surface px-3 text-sm text-ink placeholder:text-muted/70 focus:border-farmer-500 focus:outline-none focus:ring-4 focus:ring-farmer-100 ${
            leadingIcon ? "pl-10" : ""
          } ${enableToggle && isPassword ? "pr-10" : trailingIcon ? "pr-10" : ""} ${className}`}
          {...props}
        />
        {enableToggle && isPassword ? (
          <button
            type="button"
            onClick={(e) => {
              e.preventDefault();
              setShowPassword((prev) => !prev);
            }}
            className="absolute inset-y-0 right-3 flex items-center text-muted hover:text-ink focus:outline-none"
            aria-label={showPassword ? "Hide password" : "Show password"}
            tabIndex={-1}
          >
            {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
          </button>
        ) : trailingIcon ? (
          <span className="pointer-events-none absolute inset-y-0 right-3 flex items-center text-muted">
            {trailingIcon}
          </span>
        ) : null}
      </span>
      {error && <span className="block text-sm text-danger">{error}</span>}
    </label>
  );
}
