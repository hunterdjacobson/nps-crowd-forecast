/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        park: {
          green: '#2D6A4F',
          light: '#52B788',
          dark: '#1B4332',
        },
        sky: {
          blue: '#0077B6',
          light: '#90E0EF',
        },
      },
    },
  },
  plugins: [],
}
