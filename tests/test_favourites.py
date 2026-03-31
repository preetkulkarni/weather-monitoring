from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_add_favorite():
    response = client.post("/favorites/1/10")
    assert response.status_code == 200

def test_get_favorites():
    response = client.get("/favorites/1")
    assert response.status_code == 200