# Daily Tracker (Minimal)

A simple daily tracker for Health, Happiness, and Hela (Money).

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 in your browser.

## Features

- **Daily Entries**: Track 3 sections (Health, Happiness, Hela) each day
- **Groups**: Create groups and invite members to track together
- **Group Ownership**: Each group has exactly one owner who can manage members and transfer ownership
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
| POST | /api/auth/password/forgot | Request password reset (dev returns token) |
| POST | /api/auth/password/reset | Reset password with token |
| GET | /api/groups | List groups |
| POST | /api/groups | Create group |
| GET | /api/groups/:id/members | List members |
| POST | /api/groups/:id/members | Add member |
| DELETE | /api/groups/:id/members/:uid | Remove member |
| PUT | /api/groups/:id/owner | Transfer ownership |
| GET | /api/entries | Get entries |
| POST | /api/entries | Create/update entry |
| GET | /api/analytics/streak | Get streak |
| GET | /api/analytics/history | Get history |

## Password Reset Flow (Dev)

In development, the password reset flow is available without email delivery:
1) Forgot Password
   - Go to /forgot-password
   - Enter your account email
   - The backend issues a time-limited token (15 min) and returns it in the response as reset_token
2) Reset Password
   - Click "Continue to Reset Password" or open /reset-password?token=... directly
   - Enter a new password (min 6 chars) and submit
   - On success, your stored password hash is overwritten in the database

Notes:
- Tokens are signed with SECRET_KEY (set it in your environment for security)
- In production, the token should be emailed to the user instead of returned in the API response
- Endpoints:
  - POST /api/auth/password/forgot  { email }
  - POST /api/auth/password/reset   { token, password }

## Production Deployment

The app is deployed to production with the following setup:
- **Frontend**: Hosted on GitHub Pages at https://rakesh-arrepu.github.io/HHH/
- **Backend**: Hosted on Render at https://hhh-backend.onrender.com
- **Database**: Neon Postgres

To access the live application, visit the frontend URL. For updates:
- Push changes to the main branch to trigger deployment via GitHub Actions.
- Monitor workflows in the Actions tab of the repository.

Note: Ensure CORS settings (ALLOWED_ORIGINS) in the backend include the frontend URL. Update in Render if needed.
