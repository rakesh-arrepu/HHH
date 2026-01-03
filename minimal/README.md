# Daily Tracker (Minimal)

A simple daily tracker for Health, Happiness, and Hela (Money).

## Quick Start

### Backend

```bash
cd minimal/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd minimal/frontend
npm install
npm run dev
```

Open http://localhost:5173 in your browser.

## Features

- **Daily Entries**: Track 3 sections (Health, Happiness, Hela) each day
- **Groups**: Create groups and invite members to track together
- **Streak Counter**: Counts consecutive days with all 3 sections completed
- **History**: View past 30 days with completion calendar

## Tech Stack

- **Backend**: FastAPI + SQLite + SQLAlchemy
- **Frontend**: React 18 + Vite + Tailwind CSS v4
- **Auth**: Session cookies (simple, secure)

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register | Create account |
| POST | /api/auth/login | Login |
| POST | /api/auth/logout | Logout |
| GET | /api/auth/me | Get current user |
| GET | /api/groups | List groups |
| POST | /api/groups | Create group |
| GET | /api/groups/:id/members | List members |
| POST | /api/groups/:id/members | Add member |
| DELETE | /api/groups/:id/members/:uid | Remove member |
| GET | /api/entries | Get entries |
| POST | /api/entries | Create/update entry |
| GET | /api/analytics/streak | Get streak |
| GET | /api/analytics/history | Get history |

## Production Deployment

The app is deployed to production with the following setup:
- **Frontend**: Hosted on GitHub Pages at https://rakesh-arrepu.github.io/HHH/
- **Backend**: Hosted on Render at https://hhh-backend.onrender.com
- **Database**: Neon Postgres

To access the live application, visit the frontend URL. For updates:
- Push changes to the main branch to trigger deployment via GitHub Actions.
- Monitor workflows in the Actions tab of the repository.

Note: Ensure CORS settings (ALLOWED_ORIGINS) in the backend include the frontend URL. Update in Render if needed.
