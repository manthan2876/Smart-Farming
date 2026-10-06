import { Sun, Moon, Laptop } from "./icons";
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
      <div className={`inline-flex rounded-sm border border-line bg-canvas p-1 ${className}`} role="radiogroup" aria-label="Theme selection">
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
              className={`flex items-center gap-2 rounded-xs px-2.5 py-1 text-xs font-semibold transition-colors ${
                isSelected
                  ? "bg-surface text-ink border border-line"
                  : "text-muted hover:text-ink"
              }`}
            >
              <Icon size={14} className={isSelected ? "text-farmer-700 dark:text-farmer-300" : ""} />
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
      className={`relative inline-flex items-center justify-center rounded-sm p-2 text-muted transition-colors hover:bg-canvas hover:text-ink focus:outline-none focus-visible:ring-1 focus-visible:ring-farmer-700 ${className}`}
      title={isDark ? "Switch to light mode" : "Switch to dark mode"}
      aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
    >
      {isDark ? (
        <Sun size={18} className="text-amber-500" />
      ) : (
        <Moon size={18} className="text-muted hover:text-ink" />
      )}
    </button>
  );
}
