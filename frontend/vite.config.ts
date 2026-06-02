import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import compression from 'vite-plugin-compression';

export default defineConfig({
  plugins: [
    react(),
    compression({ algorithm: 'gzip', threshold: 10240 }),
  ],
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) return 'vendor';
          if (id.includes('/animations/')) return 'animation-lib';
        },
      },
    },
    chunkSizeWarningLimit: 800,
  },
  css: {
    modules: { localsConvention: 'camelCaseOnly' },
  },
});