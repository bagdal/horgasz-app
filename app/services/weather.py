import requests
import os

class WeatherService:
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY", "")
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    def get_weather(self, lat: float, lon: float):
        """Időjárás adatok lekérése a megadott koordinátákhoz"""
        if not self.api_key:
            # Demo adatok visszaadása, ha nincs API kulcs
            return self._get_demo_weather()
        
        try:
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric",
                "lang": "hu"
            }
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            return {
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "wind_speed": data["wind"]["speed"] * 3.6,  # m/s -> km/h
                "wind_direction": self._get_wind_direction(data["wind"]["deg"]),
                "description": data["weather"][0]["description"],
                "feels_like": data["main"]["feels_like"]
            }
        except Exception as e:
            print(f"Hiba az időjárás lekérésekor: {e}")
            return self._get_demo_weather()
    
    def _get_wind_direction(self, degrees: float) -> str:
        """Szélirány konvertálása fokból iránypontba"""
        directions = ["É", "ÉK", "K", "DK", "D", "DNY", "NY", "ÉNY"]
        index = round(degrees / 45) % 8
        return directions[index]
    
    def _get_demo_weather(self):
        """Demo időjárás adatok"""
        return {
            "temperature": 20.0,
            "humidity": 65,
            "pressure": 1013,
            "wind_speed": 10.0,
            "wind_direction": "K",
            "description": "Részben felhős",
            "feels_like": 19.0
        }
