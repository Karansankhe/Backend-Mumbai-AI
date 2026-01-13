from typing import Dict
import requests
from datetime import datetime

class 
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.base_geo_url = "http://api.openweathermap.org/geo/1.0/direct"
        self.base_air_url = "http://api.openweathermap.org/data/2.5/air_pollution"
        self.base_weather_url = "http://api.openweathermap.org/data/2.5/weather"

    def _get_coordinates(self, city: str, state: str, country: str) -> tuple:
        if state and state.lower() != 'none':
            location_query = f"{city},{state},{country}"
        else:
            location_query = f"{city},{country}"
        geo_url = f"{self.base_geo_url}?q={location_query}&limit=1&appid={self.api_key}"
        response = requests.get(geo_url, timeout=10)
        response.raise_for_status()
        geo_data = response.json()
        if not geo_data:
            raise ValueError(f"No coordinates found for {location_query}")
        lat = geo_data[0]['lat']
        lon = geo_data[0]['lon']
        return lat, lon

    def _convert_aqi_scale(self, aqi: int) -> int:
        aqi_mapping = {1: 25, 2: 75, 3: 125, 4: 175, 5: 250}
        return aqi_mapping.get(aqi, 0)

    def fetch_aqi_data(self, city: str, state: str, country: str) -> Dict[str, float]:
        lat, lon = self._get_coordinates(city, state, country)
        air_url = f"{self.base_air_url}?lat={lat}&lon={lon}&appid={self.api_key}"
        air_response = requests.get(air_url, timeout=10)
        air_response.raise_for_status()
        air_data = air_response.json()
        weather_url = f"{self.base_weather_url}?lat={lat}&lon={lon}&appid={self.api_key}&units=metric"
        weather_response = requests.get(weather_url, timeout=10)
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        components = air_data['list'][0]['components']
        aqi_raw = air_data['list'][0]['main']['aqi']
        aqi_converted = self._convert_aqi_scale(aqi_raw)
        temperature = weather_data['main']['temp']
        humidity = weather_data['main']['humidity']
        wind_speed = weather_data['wind']['speed'] * 3.6
        timestamp = datetime.fromtimestamp(air_data['list'][0]['dt']).strftime('%Y-%m-%d %H:%M:%S')
        result = {
            'aqi': aqi_converted,
            'aqi_category': self._get_aqi_category(aqi_raw),
            'temperature': temperature,
            'humidity': humidity,
            'wind_speed': wind_speed,
            'pm25': components.get('pm2_5', 0),
            'pm10': components.get('pm10', 0),
            'co': components.get('co', 0),
            'no2': components.get('no2', 0),
            'o3': components.get('o3', 0),
            'so2': components.get('so2', 0),
            'timestamp': timestamp
        }
        return result

    def _get_aqi_category(self, aqi: int) -> str:
        categories = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
        return categories.get(aqi, "Unknown")

