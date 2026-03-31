/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        mhrs: {
          blue: '#1A56DB',
          dark: '#1E429F'
        }
      }
    },
  },
  plugins: [],
}