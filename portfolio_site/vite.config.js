import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/Portfolio/',  // <<--- esta linha é ESSENCIAL
  build: {
    outDir: 'dist',
    emptyOutDir: true
  }
})
