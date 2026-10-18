/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './core/templates/**/*.html',
    './games/templates/**/*.html',
    './tools/templates/**/*.html',
    './guestbook/templates/**/*.html',
    './blog/templates/**/*.html',
    './chat/templates/**/*.html',
    './games/static/**/*.js',
    './tools/static/**/*.js',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
