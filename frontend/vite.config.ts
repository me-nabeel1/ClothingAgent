import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  envDir: "..",
  server: {
    host: "0.0.0.0",
    port: 5173,
    proxy: {
      "/agent": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/agent/, ""),
      },
      "/catalog": {
        target: "http://localhost:8100",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/catalog/, ""),
      },
      "/assets/products": {
        target: "http://localhost:8100",
        changeOrigin: true,
      },
    },
  },
  preview: {
    host: "0.0.0.0",
    port: 4173,
  },
});
