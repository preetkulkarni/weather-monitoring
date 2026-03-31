import time
import logging
import requests
from requests.exceptions import RequestException, Timeout
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..models import APILog
from ..schemas import WeatherData

logger = logging.getLogger(__name__)

BASE_URL = "https://api.open-meteo.com/v1/forecast"

class WeatherFetchError(Exception):
    """Custom exception for weather API failures."""
    pass

def fetch_weather_from_api(
    city_name: str,
    lat: float,
    lon: float,
    db: Session
) -> WeatherData:
    """
    Fetch current weather data from Open-Meteo API and log request.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
    }

    start_time = time.perf_counter()
    status_code = 500
    response_time_ms = 0.0

    try:
        response = requests.get(BASE_URL, params=params, timeout=5)
        response_time_ms = (time.perf_counter() - start_time) * 1000
        status_code = response.status_code

        response.raise_for_status()
        data = response.json()

        current = data.get("current")
        if not current:
            raise ValueError("Missing 'current' data in API response")

        result = WeatherData(
            city_name=city_name,
            temperature=current.get("temperature_2m", 0.0),
            humidity=current.get("relative_humidity_2m", 0.0),
            wind_speed=current.get("wind_speed_10m", 0.0),
            condition_code=current.get("weather_code", 0)
        )
        return result

    except Timeout:
        logger.error(f"Timeout fetching weather for {city_name}")
        raise WeatherFetchError("Weather API timeout")

    except RequestException as e:
        logger.error(f"Request failed for {city_name}: {str(e)}")
        raise WeatherFetchError(f"Weather API request failed: {str(e)}")

    except (ValueError, KeyError, TypeError) as e:
        logger.error(f"Invalid response format for {city_name}: {str(e)}")
        raise WeatherFetchError(f"Invalid API response structure: {str(e)}")

    finally:
        try:
            if not response_time_ms:
                response_time_ms = (time.perf_counter() - start_time) * 1000

            api_log = APILog(
                endpoint=BASE_URL,
                status_code=status_code,
                response_time_ms=response_time_ms,
            )
            db.add(api_log)
            db.commit()

        except SQLAlchemyError as db_err:
            db.rollback()
            logger.error(f"Failed to save API log to database: {str(db_err)}")

