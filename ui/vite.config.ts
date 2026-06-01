import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const base = env.VITE_BASE_PATH || "/";
  const apiProxy = env.LOGWORK_API_PROXY || "http://127.0.0.1:8001";

  return {
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
};
});
