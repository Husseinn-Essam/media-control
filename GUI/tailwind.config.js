/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      keyframes: {
        float: {
          '0%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-20px)' },
          '100%': { transform: 'translateY(0)' },
        },
      },
      animation: {
        bounce: 'float 1s infinite ease-in-out',
        note1: 'float 1s infinite ease-in-out 0.2s',
        note2: 'float 1.2s infinite ease-in-out 0.4s',
        note3: 'float 1.4s infinite ease-in-out 0.6s',
      },
    },
  },
  corePlugins: {
    preflight: false,
  },
  plugins: [],
}
