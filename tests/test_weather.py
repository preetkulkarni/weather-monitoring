from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_fetch_weather():
    response = client.get("/weather/fetch/Delhi")
    assert response.status_code in [200, 401]