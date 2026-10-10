def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["project"] == "ShareBite"
    assert response.json()["developer"] == "Ripun"


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_docs_available(client):
    response = client.get("/docs")
    assert response.status_code == 200


def test_readiness(client):
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json()["database"] == "connected"
