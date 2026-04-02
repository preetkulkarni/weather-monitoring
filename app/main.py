from fastapi import FastAPI

from app.database import engine, Base
from app.routes import weather, favourites, auth
from app.services.weather_fetcher import start_scheduler


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Weather Monitoring API",
    description="Backend system that fetches weather data, stores history, and tracks favorites."
)


app.include_router(weather.router)
app.include_router(favourites.router)
app.include_router(auth.router)


@app.get("/")
def root_endpoint():
    return {"message": "Weather Monitoring Backend Running"}


# ✅ FIXED: prevent multiple scheduler instances
scheduler_started = False

@app.on_event("startup")
def startup_event():
    global scheduler_started
    if not scheduler_started:
        start_scheduler()
        scheduler_started = True