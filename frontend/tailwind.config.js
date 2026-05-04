module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      animation: {
        spin: 'spin 1s linear infinite',
        slideIn: 'slideIn 0.3s ease-out',
      },
    },
  },
  plugins: [
    require('@tailwindcss/line-clamp'),
  ],
}
