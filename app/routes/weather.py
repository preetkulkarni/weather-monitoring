from fastapi import APIRouter
from datetime import datetime
from app.database import SessionLocal
from app.models import WeatherRecord, City
from app.services.weather_fetcher import fetch_weather_data

router = APIRouter()



@router.get("/weather/fetch/{city}")
def fetch_weather(city: str):
    return fetch_weather_data(city)



@router.get("/weather/date/{city}")
def get_weather_by_date(city: str, date: str):
    db = SessionLocal()

    try:
        
        target_date = datetime.strptime(date, "%Y-%m-%d").date()

       
        city_obj = db.query(City).filter(City.name == city).first()

        if not city_obj:
            return {"error": "City not found"}

       
        results = db.query(WeatherRecord).filter(
            WeatherRecord.city_id == city_obj.id
        ).all()

        
        filtered = [
            {
                "city": city,
                "temperature": w.temperature,
                "humidity": w.humidity,
                "wind_speed": w.wind_speed,
                "recorded_at": w.recorded_at
            }
            for w in results
            if w.recorded_at.date() == target_date
        ]

        return filtered

    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD"}

    finally:
        db.close()