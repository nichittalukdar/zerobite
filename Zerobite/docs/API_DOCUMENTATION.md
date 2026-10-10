# ShareBite API Reference

Interactive Swagger documentation is served at `/docs`; the OpenAPI JSON is at `/openapi.json`.

Base URL for local development: `http://127.0.0.1:8000`.

| Method | Path | Access | Purpose |
|---|---|---|---|
| POST | `/api/auth/register` | Public | Create donor, receiver, or volunteer account |
| POST | `/api/auth/login` | Public | Obtain JWT bearer token |
| GET | `/api/auth/me` | Any authenticated user | Current user profile |
| GET/PATCH/DELETE | `/api/donations/{id}` | Authenticated; edits restricted to owner/admin | Read or manage a donation |
| POST | `/api/donations/` | Donor/admin | Create donation |
| GET | `/api/donations/` | Authenticated | List available, unexpired donations |
| GET | `/api/donations/{id}/recommendations` | Owning donor/admin | Ranked receiver recommendations |
| POST | `/api/claims/` | Receiver | Create a claim |
| GET | `/api/claims/mine` | Receiver | List own claims |
| POST | `/api/claims/{id}/accept` | Donor who owns donation/admin | Accept a pending claim |
| POST | `/api/claims/{id}/reject` | Donor who owns donation/admin | Reject a pending claim |
| POST | `/api/claims/{id}/cancel` | Claiming receiver/admin | Cancel a pending claim |
| POST | `/api/deliveries/claims/{claim_id}/assign` | Owning donor/admin | Assign an active volunteer to an accepted claim |
| GET | `/api/deliveries/mine` | Authenticated | List deliveries visible to user |
| PUT | `/api/deliveries/{id}/status` | Assigned volunteer/admin | Update pickup/delivery status |
| GET | `/api/notifications/` | Authenticated | Get in-app notifications |
| PATCH | `/api/notifications/{id}/read` | Notification owner | Mark notification read |
| GET | `/health` | Public | Process health check |
| GET | `/health/ready` | Public | Check database connectivity |

Use the `Authorization: Bearer <access_token>` request header for protected API calls. Public registration intentionally does not permit the `admin` role.
