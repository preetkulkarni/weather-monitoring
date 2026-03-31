from fastapi import APIRouter
from datetime import datetime
from app.database import SessionLocal
from app.models import Weather
from app.services.weather_fetcher import fetch_weather_data

router = APIRouter()

# ✅ Existing API
@router.get("/weather/fetch/{city}")
def fetch_weather(city: str):
    return fetch_weather_data(city)


# ✅ NEW API (ADD THIS)
@router.get("/weather/date/{city}")
def get_weather_by_date(city: str, date: str):
    db = SessionLocal()

    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()

        results = db.query(Weather).filter(
            Weather.city == city
        ).all()

        filtered = [
            w for w in results
            if w.timestamp.date() == target_date
        ]

        return filtered

    except:
        return {"error": "Invalid date format. Use YYYY-MM-DD"}

    finally:
        db.close()