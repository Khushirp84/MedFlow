/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#1C2321',
        slate: {
          50: '#F4F7F6',
          100: '#E6ECEA',
          200: '#CBD8D4',
          300: '#A3B8B2',
        },
        teal: {
          50: '#EAF5F2',
          100: '#CDE8E1',
          400: '#3E9C87',
          500: '#2C7A69',
          600: '#215F52',
          700: '#184840',
        },
        clay: {
          400: '#D08860',
          500: '#B96D45',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
