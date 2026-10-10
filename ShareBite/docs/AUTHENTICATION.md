# Authentication and Permissions

Passwords are hashed using Argon2 through `pwdlib`; plaintext passwords are never stored. Successful login returns a short-lived JWT access token. Send that token in the `Authorization: Bearer` header.

Public registration permits `donor`, `receiver`, and `volunteer`; it rejects `admin`. Use `scripts/create_admin.py` from a trusted machine to create an administrator. API routes verify the user is active and enforce route-level role, ownership, and assignment checks.

For production, use HTTPS, set a unique randomly generated `JWT_SECRET_KEY` of at least 32 characters, configure a PostgreSQL `DATABASE_URL`, restrict `CORS_ORIGINS`, and apply Alembic migrations before starting the API.
