import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      devOptions: { enabled: false, type: 'module' },
      manifest: {
        name: 'KrishiSaarthi',
        short_name: 'Krishi',
        description: 'AI-driven farm and crop management ecosystem',
        theme_color: '#f9fafb',
        icons: [{ src: '/pwa-192x192.png', sizes: '192x192', type: 'image/png' }]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2,glb,gltf}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/fonts\.googleapis\.com\/.*/i,
            handler: 'CacheFirst',
            options: { cacheName: 'google-fonts-cache', expiration: { maxEntries: 10, maxAgeSeconds: 60 * 60 * 24 * 365 } }
          }
        ]
      }
    })
  ],
  resolve: {
    alias: {
      "@": path.resolve(import.meta.dirname, "client", "src"),
      "@shared": path.resolve(import.meta.dirname, "shared"),
      "@assets": path.resolve(import.meta.dirname, "attached_assets"),
    },
  },
  root: path.resolve(import.meta.dirname, "client"),
  build: {
    outDir: path.resolve(import.meta.dirname, "dist/public"),
    emptyOutDir: true,
    // Strip debug/info logs from production bundles
    minify: 'esbuild',
    rollupOptions: {
      output: {
        manualChunks: {
          'leaflet': ['leaflet', 'react-leaflet'],
          'charts': ['recharts'],
          'pdf': ['jspdf', 'jspdf-autotable'],
          'radix': ['@radix-ui/react-dialog', '@radix-ui/react-select', '@radix-ui/react-tooltip', '@radix-ui/react-dropdown-menu'],
        },
      },
    },
  },
  esbuild: {
    drop: process.env.NODE_ENV === 'production' ? ['console', 'debugger'] : [],
  },
  server: {
    port: 5173,
    strictPort: true, // Ensures it fails if 5173 is in use, rather than picking 5174
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/field': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/finance': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/planning': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/login': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/signup': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/password-reset': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/test_token': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/logout': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/health': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/pest': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/media': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/static': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});

