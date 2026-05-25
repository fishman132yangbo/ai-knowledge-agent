import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      boxShadow: {
        panel: "0 18px 60px rgba(24, 34, 37, 0.12)",
        inset: "inset 0 1px 0 rgba(255,255,255,0.6)"
      },
      fontFamily: {
        display: ["Avenir Next", "Gill Sans", "ui-sans-serif", "system-ui"],
        body: ["Avenir Next", "ui-sans-serif", "system-ui"]
      }
    }
  },
  plugins: []
};

export default config;
