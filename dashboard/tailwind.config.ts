import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        mono: ['var(--font-mono)', 'monospace'],
        condensed: ['var(--font-condensed)', 'sans-serif'],
      },
      colors: {
        accent: '#F59E0B',
        positive: '#34D399',
        negative: '#F87171',
        surface: '#0D1017',
        border: '#1C2333',
      },
    },
  },
  plugins: [],
}
export default config
