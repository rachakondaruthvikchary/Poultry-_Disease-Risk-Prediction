import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#d97706",
          soft: "#f59e0b",
          dark: "#b45309",
        },
        farm: {
          gold: "#fcd34d",
          rust: "#92400e",
          green: "#16a34a",
          brown: "#78350f",
        },
      },
      boxShadow: {
        glow: "0 14px 40px rgba(217, 119, 6, 0.28)",
        "glow-warm": "0 20px 50px rgba(217, 119, 6, 0.35)",
      },
    },
  },
  plugins: [],
};

export default config;
