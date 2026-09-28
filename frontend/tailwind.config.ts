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
          50: "rgb(var(--color-farmer-50, 242 247 231) / <alpha-value>)",
          100: "rgb(var(--color-farmer-100, 228 239 199) / <alpha-value>)",
          200: "rgb(var(--color-farmer-200, 207 227 157) / <alpha-value>)",
          300: "#b4d36b",
          400: "#96bd4c",
          500: "#6f9636",
          600: "#52772d",
          700: "rgb(var(--color-farmer-700, 61 93 42) / <alpha-value>)",
          800: "rgb(var(--color-farmer-800, 48 74 41) / <alpha-value>)",
          900: "rgb(var(--color-farmer-900, 38 61 43) / <alpha-value>)",
          950: "#0e1a12",
        },
        expert: {
          50: "rgb(var(--color-expert-50, 240 245 244) / <alpha-value>)",
          100: "rgb(var(--color-expert-100, 220 233 231) / <alpha-value>)",
          500: "rgb(var(--color-expert-500, 75 119 115) / <alpha-value>)",
          700: "rgb(var(--color-expert-700, 49 87 83) / <alpha-value>)",
        },
        admin: {
          50: "rgb(var(--color-admin-50, 255 247 232) / <alpha-value>)",
          100: "rgb(var(--color-admin-100, 252 232 186) / <alpha-value>)",
          500: "rgb(var(--color-admin-500, 193 132 40) / <alpha-value>)",
          700: "rgb(var(--color-admin-700, 129 87 29) / <alpha-value>)",
        },
        danger: "#b44c3c",
        success: "#52772d",
        warning: "#c18428",
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
        xl: ["1.5rem", { lineHeight: "2rem" }],
        display: ["clamp(2rem, 4vw, 3.5rem)", { lineHeight: "1.05" }],
      },
      borderRadius: {
        sm: "0.5rem",
        DEFAULT: "0.75rem",
        md: "1rem",
        lg: "1.25rem",
      },
      boxShadow: {
        soft: "var(--shadow-soft, 0 2px 10px rgba(36, 53, 45, 0.05))",
        card: "var(--shadow-card, 0 10px 30px rgba(36, 53, 45, 0.08))",
        lift: "var(--shadow-lift, 0 18px 45px rgba(36, 53, 45, 0.12))",
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
