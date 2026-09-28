import { Sun, Moon, Laptop } from "lucide-react";
import { useTheme, type Theme } from "../context/ThemeContext";

interface ThemeToggleProps {
  variant?: "icon" | "segmented";
  className?: string;
}

export default function ThemeToggle({ variant = "icon", className = "" }: ThemeToggleProps) {
  const { theme, resolvedTheme, setTheme, toggleTheme } = useTheme();

  if (variant === "segmented") {
    const options: { value: Theme; label: string; icon: typeof Sun }[] = [
      { value: "light", label: "Light", icon: Sun },
      { value: "dark", label: "Dark", icon: Moon },
      { value: "system", label: "System", icon: Laptop },
    ];

    return (
      <div className={`inline-flex rounded-sm border border-line bg-canvas/60 p-1 ${className}`} role="radiogroup" aria-label="Theme selection">
        {options.map((opt) => {
          const Icon = opt.icon;
          const isSelected = theme === opt.value;
          return (
            <button
              key={opt.value}
              type="button"
              role="radio"
              aria-checked={isSelected}
              onClick={() => setTheme(opt.value)}
              className={`flex items-center gap-2 rounded-sm px-3 py-1.5 text-xs font-semibold transition-all ${
                isSelected
                  ? "bg-surface text-ink shadow-xs border border-line/60"
                  : "text-muted hover:text-ink"
              }`}
            >
              <Icon size={14} className={isSelected ? "text-farmer-600 dark:text-farmer-400" : ""} />
              <span>{opt.label}</span>
            </button>
          );
        })}
      </div>
    );
  }

  // Quick icon toggle between light and dark
  const isDark = resolvedTheme === "dark";

  return (
    <button
      type="button"
      onClick={toggleTheme}
      className={`relative inline-flex items-center justify-center rounded-sm p-2 text-muted transition-colors hover:bg-canvas hover:text-ink focus:outline-none focus-visible:ring-2 focus-visible:ring-farmer-500 ${className}`}
      title={isDark ? "Switch to light mode" : "Switch to dark mode"}
      aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
    >
      {isDark ? (
        <Sun size={18} className="text-amber-400 transition-transform duration-200 rotate-0 hover:rotate-45" />
      ) : (
        <Moon size={18} className="text-muted transition-transform duration-200 rotate-0 hover:-rotate-12 hover:text-ink" />
      )}
    </button>
  );
}
