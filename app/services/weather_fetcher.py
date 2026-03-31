import requests
import time
import logging
from requests.exceptions import RequestException, Timeout
from sqlalchemy.exc import SQLAlchemyError
from apscheduler.schedulers.background import BackgroundScheduler

from app.database import SessionLocal
from app.models import City, WeatherRecord, APILog

logger = logging.getLogger(__name__)

BASE_URL = "https://api.open-meteo.com/v1/forecast"


class WeatherFetchError(Exception):
    pass


def fetch_weather_data(city: str):
    db = SessionLocal()

    try:
        # 🔹 Step 1: Get latitude & longitude
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}"
        geo_response = requests.get(geo_url, timeout=10).json()

        if "results" not in geo_response:
            return {"error": "City not found"}

        lat = geo_response["results"][0]["latitude"]
        lon = geo_response["results"][0]["longitude"]

        # 🔹 Step 2: Find or create city
        city_obj = db.query(City).filter(City.name == city).first()

        if not city_obj:
            city_obj = City(name=city, lat=lat, lon=lon)
            db.add(city_obj)
            db.commit()
            db.refresh(city_obj)

        # 🔹 Step 3: Call weather API
        start_time = time.perf_counter()
        status_code = 500

        try:
            response = requests.get(
                BASE_URL,
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
                },
                timeout=5,
            )

            status_code = response.status_code
            response.raise_for_status()

            data = response.json()
            current = data.get("current")

            if not current:
                raise ValueError("Missing weather data")

            # 🔹 Extract data
            temperature = current.get("temperature_2m", 0.0)
            humidity = current.get("relative_humidity_2m", 0.0)
            wind_speed = current.get("wind_speed_10m", 0.0)
            condition_code = current.get("weather_code", 0)

            
            weather = WeatherRecord(
                city_id=city_obj.id,
                temperature=temperature,
                humidity=humidity,
                wind_speed=wind_speed,
                condition_code=condition_code
            )
            db.add(weather)
            db.commit()

            return {
                "city": city,
                "temperature": temperature,
                "humidity": humidity,
                "wind_speed": wind_speed
            }

        except Timeout:
            raise WeatherFetchError("API timeout")

        except RequestException as e:
            raise WeatherFetchError(f"API request failed: {str(e)}")

        finally:
            
            try:
                response_time = (time.perf_counter() - start_time) * 1000

                api_log = APILog(
                    endpoint=BASE_URL,
                    status_code=status_code,
                    response_time_ms=response_time,
                )
                db.add(api_log)
                db.commit()

            except SQLAlchemyError:
                db.rollback()

    except Exception as e:
        logger.error(str(e))
        return {"error": "Failed to fetch weather"}

    finally:
        db.close()



def start_scheduler():
    scheduler = BackgroundScheduler()

    def auto_fetch():
        print("🔄 Updating weather for all cities...")

        cities = ["Bangalore", "Delhi", "Chennai"]
        success_count = 0

        for city in cities:
            try:
                fetch_weather_data(city)
                success_count += 1
            except Exception as e:
                print(f"Error for {city}: {e}")

        if success_count == len(cities):
            print("Update done for all cities")
        else:
            print(f"Updated {success_count}/{len(cities)} cities")

    scheduler.add_job(auto_fetch, 'interval', minutes=1)
    scheduler.start()