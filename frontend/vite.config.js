import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, '..', '')
  return {
    plugins: [react(), tailwindcss()],
    // Solo las variables VITE_ se incluyen en el bundle del navegador.
    envDir: '..',
    server: {
      host: '127.0.0.1',
      port: 5173,
      strictPort: true,
      allowedHosts: ['localhost', '127.0.0.1', 'frontend'],
      proxy: {
        '/api': { target: env.API_PROXY_TARGET || 'http://127.0.0.1:8000' },
      },
    },
  }
})
