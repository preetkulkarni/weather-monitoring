from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, date
from sqlalchemy import func
from app.database import SessionLocal
from app.models import WeatherRecord, City
from app.services.weather_fetcher import fetch_weather_data
from .auth import get_current_user

router = APIRouter()


@router.get("/weather/fetch/{city}")
def fetch_weather(city: str, current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        return fetch_weather_data(city)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/weather/date/{city}")
def get_weather_by_date(city: str, date: str):
    db = SessionLocal()
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()

        city_obj = db.query(City).filter(City.name == city).first()
        if not city_obj:
            raise HTTPException(status_code=404, detail="City not found")

        # 🔥 DB-level filtering (IMPORTANT improvement)
        results = db.query(WeatherRecord).filter(
            WeatherRecord.city_id == city_obj.id,
            func.date(WeatherRecord.recorded_at) == target_date
        ).all()

        if not results:
            return {"message": "No data found for this date"}

        return [
            {
                "city": city,
                "temperature": w.temperature,
                "humidity": w.humidity,
                "wind_speed": w.wind_speed,
                "recorded_at": w.recorded_at
            }
            for w in results
        ]

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()



@router.get("/weather/history/{city}")
def get_weather_history(city: str):
    db = SessionLocal()
    try:
        city_obj = db.query(City).filter(City.name == city).first()
        if not city_obj:
            raise HTTPException(status_code=404, detail="City not found")

        records = db.query(WeatherRecord)\
            .filter(WeatherRecord.city_id == city_obj.id)\
            .order_by(WeatherRecord.recorded_at.desc())\
            .all()

        return records

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()



@router.get("/weather/compare")
def compare_weather(city: str, date1: date, date2: date):
    db = SessionLocal()
    try:
        city_obj = db.query(City).filter(City.name == city).first()
        if not city_obj:
            raise HTTPException(status_code=404, detail="City not found")

        rec1 = db.query(WeatherRecord).filter(
            WeatherRecord.city_id == city_obj.id,
            func.date(WeatherRecord.recorded_at) == date1
        ).first()

        rec2 = db.query(WeatherRecord).filter(
            WeatherRecord.city_id == city_obj.id,
            func.date(WeatherRecord.recorded_at) == date2
        ).first()

        if not rec1 or not rec2:
            raise HTTPException(status_code=404, detail="Weather data not found for given dates")

        
        return {
            "date1": {
                "temperature": rec1.temperature,
                "humidity": rec1.humidity,
                "wind_speed": rec1.wind_speed,
                "recorded_at": rec1.recorded_at
            },
            "date2": {
                "temperature": rec2.temperature,
                "humidity": rec2.humidity,
                "wind_speed": rec2.wind_speed,
                "recorded_at": rec2.recorded_at
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()