import requests
from datetime import datetime, timedelta
from typing import Dict, Optional

class HistoricalWeatherService:
    def __init__(self):
        self.base_url = "https://archive-api.open-meteo.com/v1/archive"
    
    def get_historical_weather(self, latitude: float, longitude: float, date: datetime) -> Optional[Dict]:
        """
        Történelmi időjárás adatok lekérése a megadott dátumra és helyre.
        
        Open-Meteo Archive API használata történelmi adatokhoz.
        """
        try:
            # Dátum formázása
            date_str = date.strftime('%Y-%m-%d')
            next_day = (date + timedelta(days=1)).strftime('%Y-%m-%d')
            
            # API paraméterek
            params = {
                'latitude': latitude,
                'longitude': longitude,
                'start_date': date_str,
                'end_date': next_day,
                'hourly': 'temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,surface_pressure',
                'timezone': 'auto'
            }
            
            # API hívás
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('hourly'):
                return None
            
            # Napi átlagok számítása
            hourly_data = data['hourly']
            
            # Hőmérséklet átlag
            temperatures = [t for t in hourly_data.get('temperature_2m', []) if t is not None]
            avg_temp = sum(temperatures) / len(temperatures) if temperatures else None
            
            # Páratartalom átlag
            humidity = [h for h in hourly_data.get('relative_humidity_2m', []) if h is not None]
            avg_humidity = sum(humidity) / len(humidity) if humidity else None
            
            # Szélsebesség átlag
            wind_speeds = [w for w in hourly_data.get('wind_speed_10m', []) if w is not None]
            avg_wind_speed = sum(wind_speeds) / len(wind_speeds) if wind_speeds else None
            
            # Szélirány (leggyakoribb)
            wind_directions = [w for w in hourly_data.get('wind_direction_10m', []) if w is not None]
            avg_wind_direction = sum(wind_directions) / len(wind_directions) if wind_directions else None
            
            # Légnyomás átlag
            pressures = [p for p in hourly_data.get('surface_pressure', []) if p is not None]
            avg_pressure = sum(pressures) / len(pressures) if pressures else None
            
            return {
                'temperature': round(avg_temp, 1) if avg_temp else None,
                'humidity': round(avg_humidity) if avg_humidity else None,
                'wind_speed': round(avg_wind_speed, 1) if avg_wind_speed else None,
                'wind_direction': self._get_wind_direction(avg_wind_direction) if avg_wind_direction else None,
                'pressure': round(avg_pressure) if avg_pressure else None,
                'date': date_str
            }
            
        except Exception as e:
            print(f"Historical weather error: {e}")
            return None
    
    def _get_wind_direction(self, degrees: float) -> str:
        """
        Szélirány nevének meghatározása fokok alapján.
        """
        if degrees is None:
            return '-'
        
        directions = ['É', 'ÉÉK', 'K', 'DK', 'D', 'DD', 'NY', 'KNY', 'É']
        index = round(degrees / 45) % 8
        return directions[index]
