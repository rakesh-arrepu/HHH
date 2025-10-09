# daily-tracker

Monorepo skeleton for the Daily Tracker app.

## Getting started

Quick commands to run the project locally.

Backend (venv):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements/base.txt
uvicorn backend.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm ci
npm run dev
```

Start both with Docker Compose (dev):

```bash
make dev
```

Install pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

Commit message template is configured in `.gitmessage.txt`.