import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/blindfoldchess/',
  server: {
    host: true,
    port: 5182,
    allowedHosts: [
      'bartualfdez.asuscomm.com'
    ],
    hmr: {
      host: 'bartualfdez.asuscomm.com',
      protocol: 'wss',
      clientPort: 443,
    }
  }
})
