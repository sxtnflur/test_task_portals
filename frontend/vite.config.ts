import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// The backend (src/backend) does not send CORS headers, so in dev we proxy
// API calls through Vite's own origin instead: the browser talks to
// http://localhost:5173/api/v1/... and Vite forwards it to the real backend,
// stripping the /api/v1 prefix. See frontend/README.md for the production case.
const BACKEND_URL = process.env.VITE_API_TARGET || 'http://localhost:8000'

export default defineConfig({
  // Must be root-absolute (Vite's default). react-router's BrowserRouter
  // means a reload can land on any deep path (e.g. /portals/5); with a
  // relative base (`./`), the browser would resolve `./assets/x.js` against
  // that current path instead of the site root, requesting a path nginx's
  // SPA fallback can't serve as JS - "Expected a JavaScript module but
  // server responded with text/html". A root-absolute base always resolves
  // to the real asset regardless of which route triggered the reload.
  base: '/',
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
