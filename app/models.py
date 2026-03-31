from sqlalchemy import Column, Integer, String, Float
from app.database import Base


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


# ⭐ Favorites table (YOUR FEATURE)
class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    city_id = Column(Integer)