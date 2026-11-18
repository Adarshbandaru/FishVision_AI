import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { fileURLToPath, URL } from 'node:url'
import fs from 'node:fs'
import path from 'node:path'

// https://vite.dev/config/
export default defineConfig(() => {
  // 1. Resolve backend port dynamically
  let backendPort = process.env.VITE_BACKEND_PORT || process.env.BACKEND_PORT || '';
  let frontendPort = Number(process.env.VITE_PORT || process.env.PORT || 5173);

  // If not set in environment, attempt reading from logs/runtime/runtime.json
  if (!backendPort) {
    try {
      const configDir = fileURLToPath(new URL('.', import.meta.url));
      const runtimePath = path.resolve(configDir, '../logs/runtime/runtime.json');
      if (fs.existsSync(runtimePath)) {
        const runtimeData = JSON.parse(fs.readFileSync(runtimePath, 'utf-8'));
        if (runtimeData?.backend?.port) {
          backendPort = String(runtimeData.backend.port);
        }
        if (runtimeData?.frontend?.port && !process.env.VITE_PORT) {
          frontendPort = Number(runtimeData.frontend.port);
        }
      }
    } catch {
      // Fallback if file read fails or during partial write
    }
  }

  // Fallback to default preferred port
  if (!backendPort) {
    backendPort = '8000';
  }

  const backendTarget = `http://127.0.0.1:${backendPort}`;

  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    server: {
      port: frontendPort,
      host: '127.0.0.1',
      proxy: {
        '/api': {
          target: backendTarget,
          changeOrigin: true,
          rewrite: (pathStr) => pathStr.replace(/^\/api/, ''),
        },
        '/samples/image': {
          target: backendTarget,
          changeOrigin: true,
        }
      }
    }
  };
});
