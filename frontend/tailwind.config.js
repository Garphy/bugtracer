/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        status: {
          closed: '#8c8c8c',
          new: '#1890ff',
          key: '#ff4d4f',
          part_fixed: '#faad14',
          fixed: '#52c41a',
          wont_fix: '#bfbfbf',
          todo: '#722ed1',
          idea: '#13c2c2',
        }
      }
    },
  },
  plugins: [],
}
