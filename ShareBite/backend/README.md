# ShareBite Backend

Backend-only REST API for the ShareBite food-rescue platform. It uses FastAPI, SQLAlchemy, SQLite for local development (PostgreSQL is supported), JWT bearer tokens, Argon2 password hashing, rule-based recommendations, delivery status tracking, and stored in-app notifications.

## 1. Requirements

- Python 3.12+ recommended; the current project can also run on Python 3.14 when compatible wheels are available
- PostgreSQL for shared/deployed environments; local SQLite is the default
- PowerShell on Windows or a POSIX shell

## 2. Install on Windows PowerShell

```powershell
cd "C:\Users\RipunJoy\Documents\VS CODE FILES\ShareBite\backend"
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env -Force
```

Before deployment, replace `JWT_SECRET_KEY` with a random secret. For PostgreSQL set `DATABASE_URL` to a SQLAlchemy URL such as `postgresql+psycopg://USER:PASSWORD@HOST:5432/sharebite`. Ensure credentials are URL-encoded if they contain reserved characters.

## 3. Upgrade the database and start the API

Run the migration before starting the server, especially when upgrading an older ShareBite folder/database:

```powershell
alembic upgrade head
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`. Health checks are at `/health` and `/health/ready`.

## 4. Main API workflow

1. `POST /api/auth/register` — register a donor, receiver, or volunteer. Admin registration is intentionally disabled.
2. `POST /api/auth/login` — returns a bearer token and profile.
3. In Swagger, click **Authorize** and paste only the `access_token` value; Swagger adds the `Bearer` prefix automatically.
4. A donor creates a donation with `POST /api/donations/`.
5. A donor views ranked receivers at `GET /api/donations/{id}/recommendations`.
6. A receiver submits `POST /api/claims/`; the donor accepts with `POST /api/claims/{id}/accept`.
7. The donor/admin assigns a volunteer with `POST /api/deliveries/claims/{claim_id}/assign`.
8. The assigned volunteer updates `PUT /api/deliveries/{delivery_id}/status` to `picked_up`, then `delivered`.
9. Users fetch notifications using `GET /api/notifications/` and mark them read with `PATCH /api/notifications/{id}/read`.

## 5. Matching formula

`match_score = location_score * 0.30 + quantity_score * 0.20 + expiry_score * 0.25 + need_score * 0.25`. Component scores are normalized from 0 to 100. Receiver location, declared quantity need, and urgency priority are used. Unknown quantity needs receive a neutral score of 70 rather than an artificially perfect score.

## 6. Admin

Do not expose public admin registration. From `backend/`, create an admin using `python ..\scripts\create_admin.py` after configuring `.env`. The first migration also adds new columns to an older SQLite schema without deleting existing records.

## 7. Tests

From `backend/` with the venv active:

```powershell
pytest -q
```

The application auto-creates tables for the local demo. Use the included Alembic configuration/migrations for schema changes in deployment. The in-app notifications are stored in the database and available over REST; email, SMS, push notifications, and live WebSocket delivery are not configured in this version.
