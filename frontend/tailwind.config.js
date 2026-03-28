/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        maroon: "#5A0015",
        maroonAccent: "#850221",
        ivory: "#FEFAEF",
      },
      keyframes: {
        floatIn: {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        floatIn: "floatIn 0.5s ease-out",
      },
      boxShadow: {
        panel: "0 10px 30px -12px rgba(2, 44, 34, 0.25)",
      },
    },
  },
  plugins: [],
};
