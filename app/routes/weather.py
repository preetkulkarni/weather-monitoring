from fastapi import APIRouter
from app.services.weather_fetcher import fetch_weather_data

router = APIRouter()

@router.get("/weather/fetch/{city}")
def fetch_weather(city: str):
    return fetch_weather_data(city)