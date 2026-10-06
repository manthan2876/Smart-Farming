import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        canvas: "rgb(var(--color-canvas) / <alpha-value>)",
        surface: "rgb(var(--color-surface) / <alpha-value>)",
        ink: "rgb(var(--color-ink) / <alpha-value>)",
        muted: "rgb(var(--color-muted) / <alpha-value>)",
        line: "rgb(var(--color-line) / <alpha-value>)",
        farmer: {
          50: "rgb(var(--color-farmer-50, 244 246 240) / <alpha-value>)",
          100: "rgb(var(--color-farmer-100, 230 236 224) / <alpha-value>)",
          200: "rgb(var(--color-farmer-200, 206 218 196) / <alpha-value>)",
          300: "#9cb38d",
          400: "#6e8e5d",
          500: "#4d6f3d",
          600: "#3d5a30",
          700: "rgb(var(--color-farmer-700, 46 72 40) / <alpha-value>)",
          800: "rgb(var(--color-farmer-800, 36 57 32) / <alpha-value>)",
          900: "rgb(var(--color-farmer-900, 26 42 24) / <alpha-value>)",
          950: "#142013",
        },
        expert: {
          50: "rgb(var(--color-farmer-50, 244 246 240) / <alpha-value>)",
          100: "rgb(var(--color-farmer-100, 230 236 224) / <alpha-value>)",
          500: "rgb(var(--color-farmer-700, 46 72 40) / <alpha-value>)",
          700: "rgb(var(--color-farmer-800, 36 57 32) / <alpha-value>)",
        },
        admin: {
          50: "rgb(var(--color-farmer-50, 244 246 240) / <alpha-value>)",
          100: "rgb(var(--color-farmer-100, 230 236 224) / <alpha-value>)",
          500: "rgb(var(--color-farmer-700, 46 72 40) / <alpha-value>)",
          700: "rgb(var(--color-farmer-800, 36 57 32) / <alpha-value>)",
        },
        danger: "#9e382b",
        success: "#3d5a30",
        warning: "#8f6520",
      },
      fontFamily: {
        sans: ["Figtree", "DM Sans", "ui-sans-serif", "system-ui", "sans-serif"],
        display: ["Fraunces", "Newsreader", "Georgia", "serif"],
      },
      fontSize: {
        xs: ["0.75rem", { lineHeight: "1rem" }],
        sm: ["0.875rem", { lineHeight: "1.25rem" }],
        base: ["1rem", { lineHeight: "1.5rem" }],
        lg: ["1.125rem", { lineHeight: "1.75rem" }],
        xl: ["1.375rem", { lineHeight: "1.875rem" }],
        display: ["clamp(1.85rem, 3.5vw, 3rem)", { lineHeight: "1.1" }],
      },
      borderRadius: {
        none: "0px",
        xs: "2px",
        sm: "3px",
        DEFAULT: "4px",
        md: "4px",
        lg: "6px",
        full: "4px",
      },
      boxShadow: {
        none: "none",
        soft: "none",
        card: "none",
        lift: "0 1px 2px rgba(25, 35, 29, 0.05)",
      },
      spacing: {
        18: "4.5rem",
        22: "5.5rem",
      },
    },
  },
  plugins: [],
};

export default config;
