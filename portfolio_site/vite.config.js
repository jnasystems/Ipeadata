import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: './',
  build: {
    outDir: 'dist',         // garante que tudo vá direto para dist/
    emptyOutDir: true,      // limpa antes de cada build
  }
})
