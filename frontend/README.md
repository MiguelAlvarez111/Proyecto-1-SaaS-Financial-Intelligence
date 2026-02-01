# Frontend — SaaS Financial Intelligence

Next.js (App Router) dashboard for the [SaaS Financial Intelligence](https://github.com/MiguelAlvarez111/Proyecto-1-SaaS-Financial-Intelligence) project.

**Stack:** Next.js 16, React 19, Tailwind v4, Recharts, Framer Motion.

## Commands

| Command | Description |
| :--- | :--- |
| `npm run dev` | Development server at [http://localhost:3000](http://localhost:3000) |
| `npm run build` | Production build |
| `npm start` | Run production server |
| `npm run lint` | Run ESLint |

## Setup

From repo root see the main [README](../README.md) for full quick start (backend + frontend). From this folder:

```bash
npm install
cp .env.example .env.local   # optional: NEXT_PUBLIC_API_URL for production API
npm run dev
```

**Production:** Set `NEXT_PUBLIC_API_URL` to your backend URL (with `https://`) and redeploy so the build picks it up.
