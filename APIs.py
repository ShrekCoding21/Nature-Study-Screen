import requests
import json

def get_coordinates(city_name):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": city_name,
        "format": "json",
        "limit": 1
    }
    headers = {"User-Agent": "YourAppName/1.0 (your_email@example.com)"}

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  # Check for HTTP errors

        if not response.text.strip():
            raise ValueError("Empty response from API. Try again later.")
        
        data = response.json()
        if data:
            location = data[0]
            return float(location['lat']), float(location['lon'])
        else:
            raise ValueError("City not found. Please check the input.")
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Request Error: {e}")

# Fetch weather data

def fetch_weather_data(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "hourly": "is_day",
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch",
        "timezone": "America/New_York",
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data

# Process the weather data
def process_weather(data):
    # Extract current weather
    current = data["current_weather"]
    weather_code = current.get("weathercode")
    temperature = current.get("temperature")
    windspeed = current.get("windspeed")
    
    return {
        "weather_code": weather_code,
        "temperature": temperature,
        "windspeed": windspeed,
    }