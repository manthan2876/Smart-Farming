import type { InputHTMLAttributes, ReactNode } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  leadingIcon?: ReactNode;
}

export default function Input({ label, error, leadingIcon, className = "", id, ...props }: InputProps) {
  return (
    <label className="block space-y-2" htmlFor={id}>
      {label && <span className="block text-sm font-semibold text-ink">{label}</span>}
      <span className="relative block">
        {leadingIcon && <span className="pointer-events-none absolute inset-y-0 left-3 flex items-center text-muted">{leadingIcon}</span>}
        <input
          id={id}
          className={`min-h-11 w-full rounded-sm border border-line bg-surface px-3 text-sm text-ink placeholder:text-muted/70 focus:border-farmer-500 focus:outline-none focus:ring-4 focus:ring-farmer-100 ${leadingIcon ? "pl-10" : ""} ${className}`}
          {...props}
        />
      </span>
      {error && <span className="block text-sm text-danger">{error}</span>}
    </label>
  );
}
