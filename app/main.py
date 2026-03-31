from fastapi import FastAPI
from app.database import engine, Base
from app.routes import weather, favourites
from app.services.weather_fetcher import start_scheduler

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()


# Include routes
app.include_router(weather.router)
app.include_router(favourites.router)


# Root API
@app.get("/")
def home():
    return {"message": "Weather Monitoring Backend Running"}


# Start scheduler when app starts
@app.on_event("startup")
def startup_event():
    start_scheduler()