import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const base = process.env.VITE_BASE_PATH || "/";
const apiProxy = process.env.LOGWORK_API_PROXY || "http://127.0.0.1:8000";

export default defineConfig({
  base,
  plugins: [react()],
  server: {
    port: Number(process.env.LOGWORK_UI_PORT || 5173),
    strictPort: true,
    proxy: {
      "/api": {
        target: apiProxy,
        changeOrigin: true,
      },
    },
  },
  preview: {
    port: Number(process.env.LOGWORK_UI_PORT || 5173),
    strictPort: true,
    proxy: {
      "/api": {
        target: apiProxy,
        changeOrigin: true,
      },
    },
  },
});
