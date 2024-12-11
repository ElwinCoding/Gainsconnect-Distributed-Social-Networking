import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  build: {
    outDir: '../gainsconnect_django/static/',
    emptyOutDir: true
  },
  plugins: [
    vue(),
  ],
  server: {
    port: 3000,
    watch: {
      usePolling: true
    },
  },
  optimizeDeps: {
    exclude: ['chunk-EAUNOWDZ.js']
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})