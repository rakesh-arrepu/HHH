# Local Database Access & Viewing Guide

This guide explains in simple steps how to set up and view your local development database for this project. It covers **both PostgreSQL (default)** and **SQLite (if configured for local dev)**.

---

## 1. Determine the Database Type

Check your DB connection:

1. Open `backend/.env` (if not present, copy from `backend/.env.example`).
2. Find the value for `DATABASE_URL`. Example values:
    - **PostgreSQL:** `postgresql://user:pass@localhost:5432/daily_tracker`
    - **SQLite:** `sqlite:///app.db`

---

## 2. (Re)Create and Load the Database Schema

From project root, run:

```sh
cd backend
alembic upgrade head
```
This command applies all migrations, creating all current tables.

---

## 3. View Data in Tables

### A. If using **PostgreSQL**:

**Using CLI (`psql`):**
```sh
psql postgresql://user:pass@localhost:5432/daily_tracker
# or, if your database user has no password:
psql -U user -h localhost -d daily_tracker
```
Replace `user`, `pass`, and `daily_tracker` as per your config.

**Once inside `psql`:**
- List tables:
  ```
  \dt
  ```
- Show table columns:
  ```
  \d tablename
  ```
- View data:
  ```
  SELECT * FROM tablename LIMIT 10;
  ```
- Exit:
  ```
  \q
  ```

**Using a GUI:**
- Install [DBeaver](https://dbeaver.io/) or [pgAdmin](https://www.pgadmin.org/).
- Add a new connection using details from your `DATABASE_URL`.
- Browse tables; right-click to "View Data".

---

### B. If using **SQLite**:

**Find your SQLite DB file** (example: `backend/app.db` or `app.db`).

**Using CLI:**
```sh
sqlite3 app.db
```
Inside sqlite prompt:
- Show tables:
  ```
  .tables
  ```
- Show schema:
  ```
  .schema tablename
  ```
- View data:
  ```
  SELECT * FROM tablename LIMIT 10;
  ```
- Exit:
  ```
  .quit
  ```

**Using a GUI:**
- Install [DB Browser for SQLite](https://sqlitebrowser.org/).
- File → Open Database, select `app.db`.
- Browse tables and records.

---

## 4. (Optional) Populate Sample Data

If available, run the seed script:

```sh
python scripts/seed_data.py
```
(Check script for arguments/usage.)

---

## 5. Troubleshooting

- **If connection fails**: Check `.env` settings and that Postgres (if using) is running.
- **No tables/empty schema**: Make sure you ran `alembic upgrade head`.

---

## Reference Table

| DB Type    | Access Tool         | List Tables      | Show Data                        |
|------------|---------------------|------------------|----------------------------------|
| PostgreSQL | psql/DBeaver/pgAdmin| `\dt`            | `SELECT * FROM tablename LIMIT 10;` |
| SQLite     | sqlite3/DB Browser  | `.tables`        | `SELECT * FROM tablename LIMIT 10;` |

---
