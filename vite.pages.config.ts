import react from "@vitejs/plugin-react";
import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vite";

const projectRoot = fileURLToPath(new URL(".", import.meta.url));

export default defineConfig({
  root: fileURLToPath(new URL("./github-pages", import.meta.url)),
  base: "/northstar-merchandise-intelligence/",
  publicDir: fileURLToPath(new URL("./public", import.meta.url)),
  plugins: [react()],
  build: {
    outDir: fileURLToPath(new URL("./docs", import.meta.url)),
    emptyOutDir: true,
  },
  resolve: {
    alias: {
      "@": projectRoot,
    },
  },
});
