import { useState, useRef, useEffect, type ReactNode } from "react";
import { ChevronDown, Check } from "../icons";

export interface SelectOption {
  value: string | number;
  label: string;
  sublabel?: string;
  icon?: ReactNode;
}

export type SelectTheme = "farmer" | "expert" | "admin" | "dark" | "light";

interface ThemeStyle {
  triggerBase: string;
  triggerOpen: string;
  triggerFocus: string;
  triggerHover: string;
  chevronColor: string;
  chevronOpenColor: string;
  menuBase: string;
  optionBase: string;
  optionHover: string;
  optionSelected: string;
  checkColor: string;
  leadingIconColor: string;
  sublabelColor: string;
  placeholderColor: string;
}

const themeStyles: Record<SelectTheme, ThemeStyle> = {
  farmer: {
    triggerBase: "border-line bg-surface text-ink",
    triggerHover: "hover:border-farmer-700",
    triggerOpen: "border-farmer-700 ring-1 ring-farmer-700",
    triggerFocus: "focus:border-farmer-700 focus:ring-1 focus:ring-farmer-700",
    chevronColor: "text-muted",
    chevronOpenColor: "text-farmer-700",
    menuBase: "border-line bg-surface text-ink",
    optionBase: "border border-transparent text-ink",
    optionHover: "hover:bg-farmer-100/60 hover:text-ink",
    optionSelected: "border-line bg-farmer-100 text-ink font-semibold",
    checkColor: "text-farmer-700",
    leadingIconColor: "text-farmer-700",
    sublabelColor: "text-muted",
    placeholderColor: "text-muted",
  },
  light: {
    triggerBase: "border-line bg-surface text-ink",
    triggerHover: "hover:border-farmer-700",
    triggerOpen: "border-farmer-700 ring-1 ring-farmer-700",
    triggerFocus: "focus:border-farmer-700 focus:ring-1 focus:ring-farmer-700",
    chevronColor: "text-muted",
    chevronOpenColor: "text-farmer-700",
    menuBase: "border-line bg-surface text-ink",
    optionBase: "border border-transparent text-ink",
    optionHover: "hover:bg-farmer-100/60 hover:text-ink",
    optionSelected: "border-line bg-farmer-100 text-ink font-semibold",
    checkColor: "text-farmer-700",
    leadingIconColor: "text-farmer-700",
    sublabelColor: "text-muted",
    placeholderColor: "text-muted",
  },
  expert: {
    triggerBase: "border-line bg-surface text-ink",
    triggerHover: "hover:border-farmer-700",
    triggerOpen: "border-farmer-700 ring-1 ring-farmer-700",
    triggerFocus: "focus:border-farmer-700 focus:ring-1 focus:ring-farmer-700",
    chevronColor: "text-muted",
    chevronOpenColor: "text-farmer-700",
    menuBase: "border-line bg-surface text-ink",
    optionBase: "border border-transparent text-ink",
    optionHover: "hover:bg-farmer-100/60 hover:text-ink",
    optionSelected: "border-line bg-farmer-100 text-ink font-semibold",
    checkColor: "text-farmer-700",
    leadingIconColor: "text-farmer-700",
    sublabelColor: "text-muted",
    placeholderColor: "text-muted",
  },
  admin: {
    triggerBase: "border-line bg-surface text-ink",
    triggerHover: "hover:border-farmer-700",
    triggerOpen: "border-farmer-700 ring-1 ring-farmer-700",
    triggerFocus: "focus:border-farmer-700 focus:ring-1 focus:ring-farmer-700",
    chevronColor: "text-muted",
    chevronOpenColor: "text-farmer-700",
    menuBase: "border-line bg-surface text-ink",
    optionBase: "border border-transparent text-ink",
    optionHover: "hover:bg-farmer-100/60 hover:text-ink",
    optionSelected: "border-line bg-farmer-100 text-ink font-semibold",
    checkColor: "text-farmer-700",
    leadingIconColor: "text-farmer-700",
    sublabelColor: "text-muted",
    placeholderColor: "text-muted",
  },
  dark: {
    triggerBase: "border-farmer-700/60 bg-farmer-950 text-farmer-100 placeholder:text-farmer-300/40",
    triggerHover: "hover:border-farmer-400",
    triggerOpen: "border-farmer-400 ring-1 ring-farmer-400",
    triggerFocus: "focus:border-farmer-400 focus:ring-1 focus:ring-farmer-400",
    chevronColor: "text-farmer-200",
    chevronOpenColor: "text-farmer-300",
    menuBase: "border-farmer-700 bg-farmer-900 text-farmer-50",
    optionBase: "border border-transparent text-farmer-100",
    optionHover: "hover:bg-farmer-800 hover:text-white",
    optionSelected: "border-farmer-700 bg-farmer-800 text-farmer-200 font-semibold",
    checkColor: "text-farmer-300",
    leadingIconColor: "text-farmer-200",
    sublabelColor: "text-farmer-300",
    placeholderColor: "text-farmer-300/40",
  },
};

interface SelectProps {
  id?: string;
  name?: string;
  value?: string | number;
  onChange: (value: any) => void;
  options: SelectOption[];
  placeholder?: string;
  disabled?: boolean;
  className?: string;
  menuClassName?: string;
  theme?: SelectTheme;
  leadingIcon?: ReactNode;
}

export default function Select({
  id,
  name,
  value,
  onChange,
  options,
  placeholder = "Select an option...",
  disabled = false,
  className = "",
  menuClassName = "",
  theme = "farmer",
  leadingIcon,
}: SelectProps) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const selectedOption = options.find((opt) => opt.value === value);
  const currentTheme = themeStyles[theme] || themeStyles.farmer;

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (disabled) return;

    if (e.key === "Escape") {
      setIsOpen(false);
    } else if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      setIsOpen((prev) => !prev);
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      if (!isOpen) {
        setIsOpen(true);
      } else {
        const currentIndex = options.findIndex((opt) => opt.value === value);
        const nextIndex = currentIndex < options.length - 1 ? currentIndex + 1 : 0;
        onChange(options[nextIndex].value);
      }
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      if (!isOpen) {
        setIsOpen(true);
      } else {
        const currentIndex = options.findIndex((opt) => opt.value === value);
        const prevIndex = currentIndex > 0 ? currentIndex - 1 : options.length - 1;
        onChange(options[prevIndex].value);
      }
    }
  };

  return (
    <div ref={containerRef} className="relative w-full">
      {name && <input type="hidden" name={name} value={value ?? ""} />}
      <button
        id={id}
        type="button"
        role="combobox"
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        aria-controls={id ? `${id}-listbox` : undefined}
        disabled={disabled}
        onClick={() => !disabled && setIsOpen((prev) => !prev)}
        onKeyDown={handleKeyDown}
        className={`group flex min-h-11 w-full items-center justify-between rounded-sm border px-3 text-left text-sm transition-colors focus:outline-none ${
          currentTheme.triggerBase
        } ${currentTheme.triggerHover} ${
          isOpen ? currentTheme.triggerOpen : currentTheme.triggerFocus
        } ${disabled ? "cursor-not-allowed opacity-50" : "cursor-pointer"} ${className}`}
      >
        <span className="flex items-center gap-2 truncate">
          {leadingIcon && (
            <span className={`shrink-0 ${currentTheme.leadingIconColor}`}>
              {leadingIcon}
            </span>
          )}
          {selectedOption ? (
            <span className="flex items-center gap-2 truncate">
              {!leadingIcon && selectedOption.icon}
              <span className="truncate">{selectedOption.label}</span>
              {selectedOption.sublabel && (
                <span className={`text-xs ${currentTheme.sublabelColor}`}>
                  {selectedOption.sublabel}
                </span>
              )}
            </span>
          ) : (
            <span className={currentTheme.placeholderColor}>{placeholder}</span>
          )}
        </span>
        <ChevronDown
          size={16}
          className={`shrink-0 transition-transform duration-150 ${
            isOpen ? `rotate-180 ${currentTheme.chevronOpenColor}` : currentTheme.chevronColor
          }`}
        />
      </button>

      {isOpen && (
        <ul
          id={id ? `${id}-listbox` : undefined}
          role="listbox"
          onClick={(e) => e.stopPropagation()}
          className={`absolute left-0 top-full z-50 mt-1 max-h-60 w-full overflow-y-auto rounded-sm border p-1 space-y-0.5 custom-scrollbar ${currentTheme.menuBase} ${menuClassName}`}
        >
          {options.map((option) => {
            const isSelected = option.value === value;
            return (
              <li
                key={String(option.value)}
                role="option"
                aria-selected={isSelected}
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  onChange(option.value);
                  setIsOpen(false);
                }}
                className={`flex cursor-pointer select-none items-center justify-between rounded-xs px-3 py-2 text-sm transition-colors ${
                  isSelected
                    ? currentTheme.optionSelected
                    : `${currentTheme.optionBase} ${currentTheme.optionHover}`
                }`}
              >
                <div className="flex items-center gap-2 truncate">
                  {option.icon}
                  <span className="truncate">{option.label}</span>
                  {option.sublabel && (
                    <span className={`text-xs ${isSelected ? "" : currentTheme.sublabelColor}`}>
                      {option.sublabel}
                    </span>
                  )}
                </div>
                {isSelected && (
                  <Check
                    size={15}
                    className={`ml-2 shrink-0 ${currentTheme.checkColor}`}
                  />
                )}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
