/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      colors: {
        // Warm dark backgrounds
        dark: {
          950: '#0f0f12',
          900: '#141418',
          850: '#1a1a20',
          800: '#1f1f27',
          750: '#25252e',
          700: '#2c2c36',
          600: '#3a3a47',
          500: '#4d4d5c',
        },
        // Warm amber/terracotta accent
        primary: {
          50: '#fdf8f0',
          100: '#f9eddb',
          200: '#f2d8b4',
          300: '#e8bd84',
          400: '#de9d52',
          500: '#d4832e',
          600: '#c06b22',
          700: '#9f521e',
          800: '#804220',
          900: '#69381f',
        },
        // Muted sage green secondary
        secondary: {
          50: '#f4f7f4',
          100: '#e2eae1',
          200: '#c5d5c3',
          300: '#9db99a',
          400: '#749a70',
          500: '#537e4f',
          600: '#3f653c',
          700: '#335132',
          800: '#2b412a',
          900: '#243624',
        },
        // Warm muted accent
        accent: {
          50: '#f8f5f2',
          100: '#ede7e0',
          200: '#dcd0c3',
          300: '#c6b29e',
          400: '#b09479',
          500: '#a17e62',
          600: '#946c56',
          700: '#7b5748',
          800: '#654840',
          900: '#533d37',
        },
        // Warm neutrals
        neutral: {
          50: '#f9f8f6',
          100: '#f0eeea',
          200: '#e0ddd6',
          300: '#cbc6bc',
          400: '#a9a298',
          500: '#8f877c',
          600: '#706961',
          700: '#5a544d',
          800: '#3d3935',
          900: '#252320',
        },
      },
      boxShadow: {
        'soft': '0 2px 10px rgba(0, 0, 0, 0.2)',
        'card': '0 1px 4px rgba(0, 0, 0, 0.15)',
        'glass': '0 4px 30px rgba(0, 0, 0, 0.25)',
        'glow': '0 0 20px rgba(212, 131, 46, 0.15)',
        'glow-lg': '0 0 40px rgba(212, 131, 46, 0.2)',
      },
      animation: {
        'pulse': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.5s ease-out',
        'fade-up': 'fadeUp 0.6s ease-out',
        'spin': 'spin 1s linear infinite',
        'shimmer': 'shimmer 2.5s ease-in-out infinite',
      },
      keyframes: {
        pulse: {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0.5 },
        },
        fadeIn: {
          '0%': { opacity: 0 },
          '100%': { opacity: 1 },
        },
        fadeUp: {
          '0%': { opacity: 0, transform: 'translateY(12px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
        spin: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
    },
  },
  plugins: [],
}
