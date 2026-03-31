import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  // CodeServer proxy arkasında çalışmak için relative path'ler
  base: './',
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor-vue': ['vue', 'vue-router', 'pinia'],
          'vendor-primevue': ['primevue', '@primevue/themes'],
          'vendor-charts': ['chart.js', 'vue-chartjs'],
          'vendor-http': ['axios'],
        },
      },
    },
  },
})
