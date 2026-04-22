from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import os

class LocationService:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="horgasz_app")
    
    def geocode_address(self, address: str):
        """Cím koordinátáinak lekérése"""
        try:
            location = self.geolocator.geocode(address)
            if location:
                return {
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "address": location.address
                }
            return None
        except Exception as e:
            print(f"Hiba a címkeresésben: {e}")
            return None
    
    def reverse_geocode(self, lat: float, lon: float):
        """Cím lekérése koordinátákból"""
        try:
            location = self.geolocator.reverse(f"{lat}, {lon}")
            if location:
                return {
                    "address": location.address,
                    "city": self._extract_city(location.address),
                    "country": self._extract_country(location.address)
                }
            return None
        except Exception as e:
            print(f"Hiba a fordított címkeresésben: {e}")
            return None
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Távolság számítása két pont között (km)"""
        point1 = (lat1, lon1)
        point2 = (lat2, lon2)
        return geodesic(point1, point2).kilometers
    
    def _extract_city(self, address: str) -> str:
        """Városnév kinyerése a címből"""
        parts = address.split(",")
        for part in reversed(parts):
            if "city" in part.lower() or "város" in part.lower():
                return part.strip()
        return ""
    
    def _extract_country(self, address: str) -> str:
        """Országnév kinyerése a címből"""
        parts = address.split(",")
        if parts:
            return parts[-1].strip()
        return ""
