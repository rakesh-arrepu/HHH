# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Daily Tracker (HHH) is a simple app for tracking Health, Happiness, and Hela (Money) entries in groups with streak tracking.

## Commands

### Development
```bash
# Backend
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm run dev
```

### Build
```bash
cd frontend && npm run build
```

## Architecture

### Backend (FastAPI + SQLite)
```
backend/
├── main.py           # FastAPI app with all routes
├── auth.py           # Authentication helpers
├── database.py       # SQLAlchemy setup
├── models.py         # User, Group, Entry, Membership models
├── requirements.txt  # Python dependencies
└── venv/             # Virtual environment
```

### Frontend (Vite + React 18 + Tailwind v4)
```
frontend/
├── src/
│   ├── App.tsx       # Main app with routing
│   ├── api.ts        # API client
│   ├── auth.tsx      # Auth context
│   ├── components/   # Shared components
│   └── pages/        # Page components
├── index.html
├── vite.config.ts
└── tailwind.config.js
```

## Key Conventions

### API
- REST endpoints at `/api/auth/*`, `/api/groups/*`, `/api/entries/*`, `/api/analytics/*`
- Session cookies for auth (httpOnly, secure in production)
- CORS configured for frontend origin

### Auth
- Session-based authentication with secure cookies
- Password hashing with bcrypt
- CSRF protection on mutating endpoints

### Database
- SQLite for development (`tracker.db`)
- Neon Postgres for production
- SQLAlchemy models in `models.py`

### Environment Variables
- Backend: `SECRET_KEY`, `DATABASE_URL`, `ALLOWED_ORIGINS`
- Frontend: `VITE_API_URL`

## Production

- **Frontend**: GitHub Pages at https://rakesh-arrepu.github.io/HHH/
- **Backend**: Render at https://hhh-backend.onrender.com
- **Database**: Neon Postgres
