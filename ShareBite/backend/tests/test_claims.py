def test_create_claim_requires_authentication(client):
    response = client.post("/api/claims/", json={"donation_id": 1, "quantity": 5})
    assert response.status_code == 401
