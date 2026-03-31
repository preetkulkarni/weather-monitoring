from fastapi import FastAPI
from .database import engine, Base
from .routes import auth

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Weather Monitoring API",
    description="Backend system that fetches weather data, stores history, and tracks favorites."
)

app.include_router(auth.router)

@app.get("/")
def root_endpoint() -> dict:
    """
    health check endpoint
    
    Returns:
        dict with welcome message
    """
    return {"message": "Welcome to the Weather Monitoring API!"}