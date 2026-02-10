import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";
import runtimeErrorOverlay from "@replit/vite-plugin-runtime-error-modal";

export default defineConfig({
  plugins: [
    react(),
    runtimeErrorOverlay(),
    ...(process.env.NODE_ENV !== "production" &&
      process.env.REPL_ID !== undefined
      ? [
        await import("@replit/vite-plugin-cartographer").then((m) =>
          m.cartographer(),
        ),
        await import("@replit/vite-plugin-dev-banner").then((m) =>
          m.devBanner(),
        ),
      ]
      : []),
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
  },
  server: {
    strict: true,
    deny: ["**/.*"],
  },
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      // The endpoint in Django is currently mapped under `field/`. 
      // The frontend calls `/api/a`. 
      // We need to map `/api/a` -> `/field/chat`? 
      // OR we should update the Frontend Code to call `/field/chat`.
      // Better to update Frontend Code for clarity, but for Proxy:
      // We can just proxy everything to localhost:8000 and let Django handle routing if paths matched.
      // But paths DON'T match: frontend uses `/api/a`, backend uses `/field/chat`.
      // Let's rewrite path here or update frontend code. 
      // Updating frontend code is cleaner. 
      // For now, let's just proxy `/api` -> `http://localhost:8000` 
      // and I will update the frontend client code next.
    },
    '/field': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    }
  }
});

