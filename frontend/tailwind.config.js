/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        background: "#0b1322",
        surface: {
          DEFAULT: "#0b1322",
          low: "#141c2b",
          container: "#18202f",
          high: "#222a3a",
          highest: "#2d3545",
          bright: "#31394a",
        },
        primary: {
          DEFAULT: "#00f2fe",
          light: "#e0fdff",
          dark: "#006a70",
        },
        secondary: {
          DEFAULT: "#47efd6",
          dark: "#00554b",
        },
        border: "#222a3a",
        "border-glow": "rgba(0, 242, 254, 0.35)",
        muted: "#849495",
        "on-surface": "#dbe2f8",
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'Inter', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      boxShadow: {
        glow: "0 0 25px rgba(0, 242, 254, 0.15)",
        "glow-lg": "0 0 35px rgba(0, 242, 254, 0.25)",
      }
    },
  },
  plugins: [],
}
