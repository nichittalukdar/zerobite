def test_create_donation_requires_authentication(client):
    response = client.post(
        "/api/donations/",
        json={
            "name": "Rice and Dal",
            "category": "cooked food",
            "quantity": 20,
            "unit": "meals",
            "expiry_at": "2030-01-01T20:00:00Z",
        },
    )
    assert response.status_code == 401
