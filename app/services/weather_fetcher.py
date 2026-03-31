import requests
from app.database import SessionLocal
from app.models import Weather
from apscheduler.schedulers.background import BackgroundScheduler


# 🌦️ Fetch weather from API + store in DB
def fetch_weather_data(city: str):
    try:
        # Step 1: Get latitude & longitude
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}"
        geo_response = requests.get(geo_url, timeout=10).json()

        if "results" not in geo_response:
            return {"error": "City not found"}

        lat = geo_response["results"][0]["latitude"]
        lon = geo_response["results"][0]["longitude"]

        # Step 2: Get weather data
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        weather_response = requests.get(weather_url, timeout=10).json()

        temperature = weather_response["current_weather"]["temperature"]

        # Step 3: Store in DB
        db = SessionLocal()
        weather = Weather(city=city, temperature=temperature)
        db.add(weather)
        db.commit()
        db.close()

        return {
            "city": city,
            "temperature": temperature
        }

    except Exception:
        return {"error": "Failed to fetch weather"}


# ⏱️ Scheduler (Auto-fetch weather)
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
                print(f"❌ Error for {city}: {e}")

        # Final summary message
        if success_count == len(cities):
            print("✅ Update done for all cities")
        else:
            print(f"⚠️ Updated {success_count}/{len(cities)} cities")

    # Run every 1 minute (for testing)
    scheduler.add_job(auto_fetch, 'interval', minutes=1)
    scheduler.start()