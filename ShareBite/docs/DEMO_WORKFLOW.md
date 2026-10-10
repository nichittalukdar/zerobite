# 2-Minute Demo Workflow

1. Register or sign in as a donor.
2. Create a donation with quantity, expiry, pickup address and coordinates.
3. Request `GET /api/donations/{id}/recommendations` and show ranked match percentages.
4. Sign in as a receiver and submit `POST /api/claims/`.
5. The donor accepts the claim; the donor receives an in-app notification.
6. The donor/admin assigns a volunteer to the accepted claim.
7. The assigned volunteer changes delivery status to `picked_up`, then `delivered`.
8. Show status updates and in-app notifications from `/api/notifications/`.

Use seeded demo users only in a local development environment. Notification messages are persisted and served by REST in this MVP; email, SMS, push and live WebSocket delivery require separate providers/integration.
