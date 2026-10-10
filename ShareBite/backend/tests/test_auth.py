def test_login_rejects_unknown_account(client):
    response = client.post(
        "/api/auth/login",
        json={"email": "unknown-user@example.com", "password": "WrongPassword123!"},
    )
    assert response.status_code == 401


def test_me_requires_token(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_public_registration_cannot_create_admin(client):
    response = client.post(
        "/api/auth/register",
        json={
            "name": "Attempted Admin",
            "email": "attempted-admin@example.com",
            "password": "StrongPassword123!",
            "role": "admin",
        },
    )
    assert response.status_code == 422


def test_register_login_and_me(client):
    email = "receiver-flow@example.com"
    register = client.post(
        "/api/auth/register",
        json={"name": "Test Receiver", "email": email, "password": "StrongPassword123!", "role": "receiver"},
    )
    assert register.status_code == 201, register.text
    login = client.post("/api/auth/login", json={"email": email, "password": "StrongPassword123!"})
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200, me.text
    assert me.json()["role"] == "receiver"
