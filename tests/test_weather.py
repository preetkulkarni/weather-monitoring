from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_fetch_weather():
    response = client.get("/weather/fetch/Delhi")
    
    # Accept both (auth required)
    assert response.status_code in [200, 401]
    
def test_weather_history():
    response = client.get("/weather/history/Delhi")
    
    # Accept both cases (data may or may not exist)
    assert response.status_code in [200, 404]


def test_weather_by_date():
    response = client.get("/weather/date/Delhi?date=2026-03-30")
    
    # Accept valid or no-data case
    assert response.status_code in [200, 404]
    
def test_compare_weather():
    response = client.get(
        "/weather/compare?city=Delhi&date1=2026-03-29&date2=2026-03-30"
    )

    # May or may not have data
    assert response.status_code in [200, 404]


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert "message" in response.json()