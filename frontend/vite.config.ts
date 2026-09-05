import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// The backend (src/backend) does not send CORS headers, so in dev we proxy
// API calls through Vite's own origin instead: the browser talks to
// http://localhost:5173/api/v1/... and Vite forwards it to the real backend,
// stripping the /api/v1 prefix. See frontend/README.md for the production case.
const BACKEND_URL = process.env.VITE_API_TARGET || 'http://localhost:8000'

export default defineConfig({
  // Root-absolute asset paths (Vite's default, `base: '/'`) only resolve
  // once the built `dist/` is served from a web server's actual root.
  // Opening `dist/index.html` directly (double-click, `file://...`) or
  // serving it from a subfolder then 404s on every `/assets/...` request -
  // a relative base keeps the build working from any location.
  base: './',
  plugins: [react()],
  server: {
    proxy: {
      '/api/v1': {
        target: BACKEND_URL,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/v1/, ''),
      },
    },
  },
})
