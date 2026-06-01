import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: Number(process.env.LOGWORK_UI_PORT || 5173),
    strictPort: true,
    proxy: {
      "/api": {
        target: process.env.LOGWORK_API_PROXY || "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
  preview: {
    port: Number(process.env.LOGWORK_UI_PORT || 5173),
    strictPort: true,
    proxy: {
      "/api": {
        target: process.env.LOGWORK_API_PROXY || "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
});
