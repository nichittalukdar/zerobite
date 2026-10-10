# ShareBite Database Schema

- `users`: identity, normalized email, Argon2 password hash, role, active flag, coordinates, receiver need quantity and priority.
- `donations`: donor, food description, photo URL, pickup address, quantity/unit, expiry, location coordinates and current state.
- `claims`: receiver request against a donation, claimed quantity and decision state.
- `deliveries`: one delivery record per accepted claim, assigned volunteer, status, pickup and delivery timestamps.
- `notifications`: user-specific in-app notification messages with event type and read state.

SQLAlchemy models are in `backend/app/models/`. `alembic upgrade head` creates a fresh schema or upgrades the older SQLite schema shipped with previous ShareBite work without removing existing rows. Back up any real database before applying migrations.
