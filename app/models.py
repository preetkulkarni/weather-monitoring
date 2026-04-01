from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func
from app.database import Base
import time

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")


class City(Base):
    __tablename__ = "cities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    country = Column(String(100))
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    
    weather_records = relationship("WeatherRecord", back_populates="city", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="city", cascade="all, delete-orphan")


class WeatherRecord(Base):
    __tablename__ = "weather_records"
    
    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False, index=True)
    temperature = Column(Float)
    humidity = Column(Float)
    wind_speed = Column(Float)
    condition_code = Column(Integer)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    city = relationship("City", back_populates="weather_records")


class Favorite(Base):
    __tablename__ = "favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False, index=True)
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="favorites")
    city = relationship("City", back_populates="favorites")


class APILog(Base):
    __tablename__ = "api_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String(255), nullable=False)
    status_code = Column(Integer, nullable=False)
    response_time_ms = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

def log_api_call(db: Session, endpoint: str, status_code: int, start_time: float):
    """
    Helper to persist API logs to the database.
    """
    duration = (time.perf_counter() - start_time) * 1000  # Convert to ms
    api_log = APILog(
        endpoint=endpoint,
        status_code=status_code,
        response_time_ms=duration
    )
    db.add(api_log)
    db.commit()