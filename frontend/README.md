# Portal Watch — frontend

A React + TypeScript + Vite frontend for the portals API in `backend/src/presentation/api`.

- **Portals table** (`/`) — lists portals via `GET /portals`, paginated.
- **Portal detail** (`/portals/:id`) — full info via `GET /portals/{id}` (energy, stability,
  risk breakdown, recommended action, change log) and every mutating action the API exposes:
  open, close, stabilize, send/recall observer, mark, unmark.

## Running it

```bash
npm install
npm run dev
```

Opens on `http://localhost:5173`. It expects the backend on `http://localhost:8000` (override
with `VITE_API_TARGET`, e.g. `VITE_API_TARGET=http://localhost:9000 npm run dev`).

## Why a dev proxy

The backend sends no CORS headers, so the browser can't call it directly from a different
origin (`localhost:5173` → `localhost:8000`). Rather than touch backend code, `vite.config.ts`
proxies `/api/*` to the backend during `npm run dev`, stripping the `/api` prefix — the app
only ever calls same-origin `/api/...` paths. **This proxy only exists in dev.** A production
static build has nothing to proxy through; deploying it needs either a reverse proxy that
serves the built frontend and forwards `/api` to the backend under one origin, or CORS enabled
on the backend.

## Known backend limitations this frontend works around

- **Change log is not scoped per portal.** `PortalChangeLogsRepository` (and thus both
  `GET /logs/portal` and the `change_logs` embedded in `GET /portals/{id}`) has no `portal_id`
  filter — it returns the N most recent logs across *all* portals. The detail page filters the
  returned page client-side by `portal_id`; on a busy system with many portals this can mean a
  portal's own history gets pushed off the fetched page even though older entries exist. Fixing
  it properly needs a `portal_id` parameter added to the repository port and both its
  implementations (`memory`, `postgres`).
- **`marked` is not exposed by any endpoint.** The domain has `Portal.marked` and the API has
  `/portals/mark` and `/portals/unmark`, but no response DTO returns the current value, so this
  UI can't show whether a portal is marked or toggle a single button — it shows both actions
  unconditionally (harmless: marking/unmarking has no invariant to violate either way).
- **`GET /portals/{id}` on an expired portal returns a handled error, not data**
  (`400 {"error": {"type": "DomainError", "detail": "The portal is expired"}}`), because
  `Portal.risk` refuses to compute risk for an expired portal and the application layer doesn't
  guard against it for the single-portal lookup (it does for the list). The detail page shows
  this as a normal error banner rather than crashing.

## Project layout

```
src/
  api/          fetch client + typed request functions (mirrors the backend DTOs)
  components/   small presentational pieces (badges, error banner)
  pages/        the two routed pages
```
