import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// En développement, Vite relaie /api vers l'API comme le fera nginx dans l'image :
// /api/documents/1 -> http://localhost:8000/documents/1
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': {
        target: process.env.API_URL || 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
