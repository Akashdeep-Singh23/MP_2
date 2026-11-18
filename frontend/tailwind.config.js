/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#F2F6E8',
          100: '#E2ECC9',
          500: '#A7C957',
          600: '#91B440',
          700: '#789934',
        },
        surface: {
          DEFAULT: '#181818',
          raised: '#1F1F1F',
          high: '#272727',
          border: '#313131',
        }
      }
    },
  },
  plugins: [],
}
