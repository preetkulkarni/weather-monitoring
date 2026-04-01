# Weather Monitoring Backend
## Project Overview
The Weather Monitoring Backend is a robust FastAPI-based system designed to fetch, store, and analyze weather data. It provides real-time weather updates, historical data tracking, and user-specific features like favorite cities, all while maintaining an automated background process for data collection.

## Project Structure
```
weather_monitoring/
│── app/
│   │── main.py            
│   │── database.py        
│   │── models.py          
│   │── schemas.py         
│   │── crud.py           
│   │── routes/
│   │   │── auth.py        
│   │   │── weather.py     
│   │   │── favorites.py  
│   │── services/
│   │   │── weather_fetcher.py
│── tests/
│   │── test_weather.py   
│   │── test_favorites.py 
│── requirements.txt       
│── Dockerfile           
│── README.md             
```

## Key Features
- **User Authentication**: Secure registration and login system.

- **Real-time Fetching**: Integration with Open-Meteo / OpenWeatherMap APIs.

- **Data Persistence**: Historical weather records stored in SQLite.

- **Comparisons**: Compare weather data for specific cities across different dates.

- **Favorites**: Personalized list of cities for quick access.

- **Automation**: Scheduled daily background jobs to fetch and log weather data.

- **Error Handling**: Robust logging of API calls and failure management.

# Database Schema
The project utilizes SQLite with the following tables:

`users` : Stores user credentials and profile info.

`cities` : Metadata for tracked cities.

`weather_records` : Historical temperature, humidity, and condition data.

`favorites` : Mapping between users and their preferred cities.

`api_logs` : Tracks external API requests and response statuses.

## API Endpoints

### Authentication
`POST /register` - Create a new user account.

`POST /login` - Authenticate and receive access tokens.

### Weather Operations
`GET /weather/fetch/{city}` - Get current weather for a city (triggers API call).

`GET /weather/history/{city}` - Retrieve stored historical data for a city.

`GET /weather/date/{city}` - Get weather data for a specific date.

`GET /weather/compare` - Compare weather metrics between two different dates.

### Favorites
`POST /favorites/{city}` - Add a city to your favorites.

`GET /favorites/{user_id}` - Retrieve all favorite cities for a specific user.

## Setup and Installation
### Local Setup
1. Clone the repository.

2. Install dependencies:
`pip install -r requirements.txt`

3. Run the application:
`uvicorn app.main:app --reload`

### Docker Deployment
1. Build the image:
`docker build -t weather-backend .`

2. Run the container:
`docker run -p 8000:8000 weather-backend`

## Tech Stack
**Framework**: FastAPI

**Database**: SQLite (SQLAlchemy ORM)

**Language**: Python 3.x

**External API**: Open-Meteo / OpenWeatherMap

**Testing**: Pytest

**Containerization**: Docker