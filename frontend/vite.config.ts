import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  base: process.env.VITE_BASE_PATH || '/',
  plugins: [react()],
  css: { postcss: './postcss.config.js' },
  server: {
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
})
