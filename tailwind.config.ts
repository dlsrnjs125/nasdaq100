import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#0F172A",
        surface: "#1E293B",
        raised: "#334155",
        ink: "#F1F5F9",
        muted: "#94A3B8",
        disabled: "#64748B",
        primary: "#3B82F6",
        positive: "#10B981",
        warning: "#F59E0B",
        negative: "#EF4444"
      },
      fontFamily: {
        sans: ["Inter", "SF Pro Display", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Roboto Mono", "Fira Code", "monospace"]
      }
    }
  },
  plugins: []
};

export default config;
