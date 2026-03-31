from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database import Base
from datetime import datetime

# 👤 Users table (basic placeholder)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)


# 🌦️ Weather table
class Weather(Base):
    __tablename__ = "weather"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String)
    temperature = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

# ⭐ Favorites table (YOUR FEATURE)
class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    city_id = Column(Integer)