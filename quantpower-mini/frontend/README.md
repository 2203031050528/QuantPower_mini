# QuantPower Mini — Frontend

React + Vite SPA for the Django backend (JWT auth, market WebSocket, virtual/live orders, positions, Dhan account, proxy status).

## Local
```bash
cp .env.example .env     # point at your backend
npm install
npm run dev              # http://localhost:5173
```
Run the backend with `python manage.py runserver` and `python manage.py mock_market` for fake ticks.

## Deploy on Vercel
1. Import the repo in Vercel and set **Root Directory = `frontend`** (framework: Vite, auto-detected).
2. Environment variables:
   - `VITE_API_URL=https://api.your-domain.com`
   - `VITE_WS_URL=wss://api.your-domain.com`
3. Deploy. `vercel.json` rewrites all routes to `index.html` for client-side routing.

Backend requirements:
- Must be served over **HTTPS/WSS** (Vercel is HTTPS; browsers block mixed content).
- Set `CORS_ALLOWED_ORIGINS=https://your-app.vercel.app` in the backend `.env` and restart Daphne.
- Add the API host to `ALLOWED_HOSTS`.
