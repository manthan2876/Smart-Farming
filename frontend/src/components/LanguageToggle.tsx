import { useState, useRef, useEffect } from "react";
import { Globe, Check } from "./icons";
import { useAuth } from "../context/AuthContext";
import { type Language } from "../i18n";

interface LanguageToggleProps {
  variant?: "dropdown" | "segmented" | "icon";
  showCode?: boolean;
  className?: string;
}

const LANGUAGES: { code: Language; label: string; short: string; vernacular: string }[] = [
  { code: "English", label: "English", short: "EN", vernacular: "English" },
  { code: "Gujarati", label: "Gujarati", short: "GU", vernacular: "ગુજરાતી" },
  { code: "Hindi", label: "Hindi", short: "HI", vernacular: "हिन्दी" },
];

export default function LanguageToggle({ 
  variant = "dropdown", 
  showCode = true,
  className = "" 
}: LanguageToggleProps) {
  const { language, setLanguage } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  if (variant === "segmented") {
    return (
      <div
        className={`inline-flex rounded-sm border border-line bg-canvas p-0.5 text-xs font-semibold ${className}`}
        role="group"
        aria-label="Language selection"
      >
        {LANGUAGES.map((lang) => {
          const isSelected = language === lang.code;
          return (
            <button
              key={lang.code}
              type="button"
              onClick={() => setLanguage(lang.code)}
              className={`rounded-xs px-2.5 py-1 text-xs transition-colors ${
                isSelected
                  ? "bg-surface font-bold text-ink border border-line"
                  : "text-muted hover:text-ink"
              }`}
            >
              {lang.vernacular}
            </button>
          );
        })}
      </div>
    );
  }

  const currentLang = LANGUAGES.find((l) => l.code === language) || LANGUAGES[0];
  const isIconOnly = variant === "icon" || !showCode;

  return (
    <div className={`relative inline-block ${className}`} ref={containerRef}>
      <button
        type="button"
        onClick={() => setIsOpen((prev) => !prev)}
        className={
          isIconOnly
            ? "relative inline-flex items-center justify-center rounded-sm p-2 text-muted transition-colors hover:bg-canvas hover:text-ink focus:outline-none focus-visible:ring-1 focus-visible:ring-farmer-700"
            : "inline-flex items-center gap-1.5 rounded-sm border border-line bg-surface px-2 py-1 text-xs font-semibold text-ink transition-colors hover:bg-canvas focus:outline-none focus-visible:ring-1 focus-visible:ring-farmer-700"
        }
        aria-expanded={isOpen}
        aria-haspopup="listbox"
        title={`Language: ${currentLang.vernacular} (${currentLang.short})`}
        aria-label={`Language: ${currentLang.vernacular} (${currentLang.short})`}
      >
        <Globe size={isIconOnly ? 18 : 14} className={isIconOnly ? "text-muted hover:text-ink" : "text-farmer-700 dark:text-farmer-300 shrink-0"} />
        {!isIconOnly && (
          <span className="text-[0.72rem] font-bold uppercase tracking-wider">{currentLang.short}</span>
        )}
      </button>

      {isOpen && (
        <div
          role="listbox"
          className="absolute right-0 top-full z-50 mt-1 min-w-[9.5rem] rounded-sm border border-line bg-surface p-1 shadow-soft"
        >
          {LANGUAGES.map((lang) => {
            const isSelected = language === lang.code;
            return (
              <button
                key={lang.code}
                type="button"
                role="option"
                aria-selected={isSelected}
                onClick={() => {
                  setLanguage(lang.code);
                  setIsOpen(false);
                }}
                className={`flex w-full items-center justify-between rounded-xs px-2.5 py-1.5 text-xs transition-colors ${
                  isSelected
                    ? "bg-farmer-50 font-bold text-farmer-900 dark:bg-farmer-950/60 dark:text-farmer-200"
                    : "text-muted hover:bg-canvas hover:text-ink"
                }`}
              >
                <div className="flex items-center gap-2">
                  <span>{lang.vernacular}</span>
                  <span className="text-[0.65rem] text-muted">({lang.label})</span>
                </div>
                {isSelected && <Check size={13} className="text-farmer-700 dark:text-farmer-300" />}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
