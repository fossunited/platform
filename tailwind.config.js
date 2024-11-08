/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './fossunited/www/**/*.html',
    './fossunited/templates/**/*.html',
    './fossunited/stack/web_template/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#e6f8ed',
          100: '#b2e9c8',
          200: '#8ddeae',
          300: '#5acf89',
          400: '#39c572',
          500: '#08b74f',
          600: '#07a748',
          700: '#068238',
          800: '#04652b',
          900: '#034d21',
          950: '#003914',
          DEFAULT: '#08b74f',
        },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
        mono: ['"Fira Code"', 'monospace'],
        code: ['"Fira Code"', 'monospace'],
        fff: ['"FFF Forward"', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
