from datetime import datetime, timedelta, timezone


def register(client, name, email, role, **extra):
    payload = {"name": name, "email": email, "password": "StrongPassword123!", "role": role}
    payload.update(extra)
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201, response.text
    login = client.post("/api/auth/login", json={"email": email, "password": "StrongPassword123!"})
    assert login.status_code == 200, login.text
    return login.json()["access_token"]


def test_donation_match_claim_delivery_and_notifications(client):
    donor_token = register(client, "Workflow Donor", "workflow-donor@example.com", "donor", latitude=26.1445, longitude=91.7362)
    receiver_token = register(client, "Workflow Receiver", "workflow-receiver@example.com", "receiver", latitude=26.1450, longitude=91.7370, needed_quantity=12, need_priority="urgent")
    volunteer_token = register(client, "Workflow Volunteer", "workflow-volunteer@example.com", "volunteer")
    donor_headers = {"Authorization": f"Bearer {donor_token}"}
    receiver_headers = {"Authorization": f"Bearer {receiver_token}"}
    volunteer_headers = {"Authorization": f"Bearer {volunteer_token}"}

    donation = client.post("/api/donations/", headers=donor_headers, json={
        "name": "Fresh rice meals", "category": "cooked food", "quantity": 12, "unit": "meals",
        "expiry_at": (datetime.now(timezone.utc) + timedelta(hours=3)).isoformat(),
        "latitude": 26.1445, "longitude": 91.7362, "pickup_address": "Community Centre",
        "photo_url": "https://example.com/food.jpg",
    })
    assert donation.status_code == 201, donation.text
    donation_id = donation.json()["id"]

    recommendations = client.get(f"/api/donations/{donation_id}/recommendations", headers=donor_headers)
    assert recommendations.status_code == 200, recommendations.text
    assert recommendations.json()["count"] == 1
    assert recommendations.json()["recommendations"][0]["quantity_score"] == 100

    claim = client.post("/api/claims/", headers=receiver_headers, json={"donation_id": donation_id, "quantity": 12})
    assert claim.status_code == 201, claim.text
    claim_id = claim.json()["id"]

    accepted = client.post(f"/api/claims/{claim_id}/accept", headers=donor_headers)
    assert accepted.status_code == 200, accepted.text
    assert accepted.json()["status"] == "accepted"

    volunteer_profile = client.get("/api/auth/me", headers=volunteer_headers).json()
    assignment = client.post(f"/api/deliveries/claims/{claim_id}/assign", headers=donor_headers, json={"volunteer_id": volunteer_profile["id"]})
    assert assignment.status_code == 201, assignment.text
    delivery_id = assignment.json()["id"]

    picked_up = client.put(f"/api/deliveries/{delivery_id}/status", headers=volunteer_headers, json={"status": "picked_up"})
    assert picked_up.status_code == 200, picked_up.text
    delivered = client.put(f"/api/deliveries/{delivery_id}/status", headers=volunteer_headers, json={"status": "delivered"})
    assert delivered.status_code == 200, delivered.text

    notifications = client.get("/api/notifications/", headers=receiver_headers)
    assert notifications.status_code == 200, notifications.text
    assert any(n["event_type"] == "delivery_delivered" for n in notifications.json())


def test_partial_claim_cancel_restores_remaining_quantity(client):
    donor_token = register(client, "Partial Donor", "partial-donor@example.com", "donor", latitude=26.1445, longitude=91.7362)
    receiver_token = register(client, "Partial Receiver", "partial-receiver@example.com", "receiver", latitude=26.1450, longitude=91.7370, needed_quantity=5)
    volunteer_token = register(client, "Partial Volunteer", "partial-volunteer@example.com", "volunteer")
    donor_headers = {"Authorization": f"Bearer {donor_token}"}
    receiver_headers = {"Authorization": f"Bearer {receiver_token}"}
    volunteer_headers = {"Authorization": f"Bearer {volunteer_token}"}

    donation_response = client.post("/api/donations/", headers=donor_headers, json={
        "name": "Twenty meals", "category": "cooked food", "quantity": 20, "unit": "meals",
        "expiry_at": (datetime.now(timezone.utc) + timedelta(hours=8)).isoformat(),
        "latitude": 26.1445, "longitude": 91.7362,
    })
    assert donation_response.status_code == 201, donation_response.text
    donation_id = donation_response.json()["id"]
    claim_response = client.post("/api/claims/", headers=receiver_headers, json={"donation_id": donation_id, "quantity": 5})
    assert claim_response.status_code == 201, claim_response.text
    claim_id = claim_response.json()["id"]
    accepted = client.post(f"/api/claims/{claim_id}/accept", headers=donor_headers)
    assert accepted.status_code == 200, accepted.text
    listed = client.get("/api/donations/", headers=receiver_headers).json()
    assert next(item for item in listed if item["id"] == donation_id)["quantity"] == 15

    volunteer_id = client.get("/api/auth/me", headers=volunteer_headers).json()["id"]
    assignment = client.post(f"/api/deliveries/claims/{claim_id}/assign", headers=donor_headers, json={"volunteer_id": volunteer_id})
    assert assignment.status_code == 201, assignment.text
    cancelled = client.put(f"/api/deliveries/{assignment.json()['id']}/status", headers=volunteer_headers, json={"status": "cancelled"})
    assert cancelled.status_code == 200, cancelled.text
    listed = client.get("/api/donations/", headers=receiver_headers).json()
    assert next(item for item in listed if item["id"] == donation_id)["quantity"] == 20
