# Sathya Agencies - Vercel Deployment

## What was changed
- Replaced `Flask-MySQLdb` / native `mysqlclient` with `PyMySQL`, which avoids the native client build failure on Vercel.
- Added a Flask-aware database adapter in `db.py` so the existing `mysql.connection.cursor()`, `commit()`, and `rollback()` code continues to work.
- Added `api/index.py` as the Vercel Flask entry point.
- Pinned Python to 3.12.
- Pinned compatible Python dependencies in `requirements.txt`.

## Vercel environment variables
Add these in Vercel Project Settings -> Environment Variables:

- `SECRET_KEY`
- `MYSQL_HOST`
- `MYSQL_PORT` (normally `3306`)
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `MYSQL_DB`

Do not commit `.env` or real passwords to GitHub.

## Database
`database.sql` creates the required MySQL database/tables. Vercel does not run MySQL itself; use an externally reachable MySQL-compatible database and put its credentials in Vercel Environment Variables.
