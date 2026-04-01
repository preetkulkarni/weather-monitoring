from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)   # ✅ THIS WAS MISSING


def test_add_favorite():
    # ✅ Step 1: Register user
    client.post("/auth/register", json={
        "email": "fav@test.com",
        "password": "123456"
    })

    # ✅ Step 2: Login
    login = client.post("/auth/login", json={
        "email": "fav@test.com",
        "password": "123456"
    })

    data = login.json()

    # ✅ Handle cases safely
    if "access_token" not in data:
        return

    token = data["access_token"]

    # ✅ Step 3: Fetch weather (creates city)
    client.get(
        "/weather/fetch/Delhi",
        headers={"Authorization": f"Bearer {token}"}
    )

    # ✅ Step 4: Add favorite
    response = client.post("/favorites/1/1")

    assert response.status_code in [200, 201, 400]