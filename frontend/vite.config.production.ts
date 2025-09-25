import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// Production configuration for deployment
export default defineConfig({
  plugins: [react()],
  base: './', // Use relative paths for GitHub Pages
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom'],
          ui: ['react-bootstrap', 'bootstrap']
        }
      }
    }
  },
  server: {
    port: 5173,
    host: true
  }
})
