import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#f5f2eb",
        surface: "#ffffff",
        ink: "#24352d",
        muted: "#6b776f",
        line: "#e3e6df",
        farmer: {
          50: "#f2f7e7",
          100: "#e4efc7",
          200: "#cfe39d",
          300: "#b4d36b",
          400: "#96bd4c",
          500: "#6f9636",
          600: "#52772d",
          700: "#3d5d2a",
          800: "#304a29",
          900: "#263d2b",
        },
        expert: {
          50: "#f0f5f4",
          100: "#dce9e7",
          500: "#4b7773",
          700: "#315753",
        },
        admin: {
          50: "#fff7e8",
          100: "#fce8ba",
          500: "#c18428",
          700: "#81571d",
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
        soft: "0 2px 10px rgba(36, 53, 45, 0.05)",
        card: "0 10px 30px rgba(36, 53, 45, 0.08)",
        lift: "0 18px 45px rgba(36, 53, 45, 0.12)",
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
