from datetime import datetime, timedelta
from typing import Dict, List
import math

class SolunarService:
    def __init__(self):
        pass
    
    def calculate_solunar(self, date: datetime, latitude: float, longitude: float) -> Dict:
        """
        Kiszámolja a Solunar adatokat a megadott dátumra és helyre.
        
        A Solunar táblázat 4 etetési időablakot mutat napi:
        - 2 major (fő) időszak
        - 2 minor (mellék) időszak
        
        Ezek a hold fázis és a hold állása alapján kerülnek kiszámításra.
        """
        moon_data = self._get_moon_data(date)
        
        # Hold kelte és nyugdása
        moonrise, moonset = self._calculate_moon_times(date, latitude, longitude)
        
        # Etetési időablakok kiszámítása
        major_periods = self._calculate_major_periods(moonrise, moonset)
        minor_periods = self._calculate_minor_periods(moonrise, moonset)
        
        # Etetési intenzitás (0-100)
        intensity = self._calculate_intensity(moon_data['phase'], date)
        
        return {
            'date': date.strftime('%Y-%m-%d'),
            'moonrise': moonrise.strftime('%H:%M') if moonrise else None,
            'moonset': moonset.strftime('%H:%M') if moonset else None,
            'moon_phase': moon_data['phase'],
            'moon_illumination': moon_data['illumination'],
            'major_periods': major_periods,
            'minor_periods': minor_periods,
            'intensity': intensity,
            'rating': self._get_rating(intensity)
        }
    
    def _get_moon_data(self, date: datetime) -> Dict:
        """
        Hold fázis és megvilágítás kiszámítása.
        """
        # Egyszerűsített hold fázis számítás
        # 0 = Újhold, 0.5 = Telihold, 1.0 = Újhold
        days_since_new_moon = (date - datetime(2000, 1, 6)).days % 29.53
        phase = days_since_new_moon / 29.53
        
        # Megvilágítás (0-100%)
        illumination = (1 - math.cos(phase * 2 * math.pi)) / 2 * 100
        
        phase_name = self._get_phase_name(phase)
        
        return {
            'phase': phase_name,
            'illumination': round(illumination, 1)
        }
    
    def _get_phase_name(self, phase: float) -> str:
        """
        Hold fázis nevének meghatározása.
        """
        if phase < 0.03 or phase > 0.97:
            return 'Újhold'
        elif phase < 0.22:
            return 'Növőhold'
        elif phase < 0.28:
            return 'Első negyed'
        elif phase < 0.47:
            return 'Növőhold'
        elif phase < 0.53:
            return 'Telihold'
        elif phase < 0.72:
            return 'Csökkenőhold'
        elif phase < 0.78:
            return 'Utolsó negyed'
        else:
            return 'Csökkenőhold'
    
    def _calculate_moon_times(self, date: datetime, latitude: float, longitude: float) -> tuple:
        """
        Hold kelte és nyugdása kiszámítása.
        Egyszerűsített számítás a longitud alapján.
        """
        # Egyszerűsített hold kelte/nyugdás számítás
        # A valóságban bonyolultabb számítás szükséges
        base_hour = 6 + (longitude / 15)  # Kb. 6 óra + longitud korrekció
        
        moonrise = date.replace(hour=int(base_hour), minute=0)
        moonset = date.replace(hour=int((base_hour + 12) % 24), minute=0)
        
        return moonrise, moonset
    
    def _calculate_major_periods(self, moonrise: datetime, moonset: datetime) -> List[Dict]:
        """
        Major (fő) etetési időszakok kiszámítása.
        Ezek kb. 2 órával hold kelte/nyugdás előtt és után vannak.
        """
        periods = []
        
        if moonrise:
            periods.append({
                'start': (moonrise - timedelta(hours=2)).strftime('%H:%M'),
                'end': (moonrise + timedelta(hours=2)).strftime('%H:%M'),
                'type': 'major'
            })
        
        if moonset:
            periods.append({
                'start': (moonset - timedelta(hours=2)).strftime('%H:%M'),
                'end': (moonset + timedelta(hours=2)).strftime('%H:%M'),
                'type': 'major'
            })
        
        return periods
    
    def _calculate_minor_periods(self, moonrise: datetime, moonset: datetime) -> List[Dict]:
        """
        Minor (mellék) etetési időszakok kiszámítása.
        Ezek kb. 6 órával a major időszakok után vannak.
        """
        periods = []
        
        if moonrise:
            periods.append({
                'start': (moonrise + timedelta(hours=6)).strftime('%H:%M'),
                'end': (moonrise + timedelta(hours=8)).strftime('%H:%M'),
                'type': 'minor'
            })
        
        if moonset:
            periods.append({
                'start': (moonset + timedelta(hours=6)).strftime('%H:%M'),
                'end': (moonset + timedelta(hours=8)).strftime('%H:%M'),
                'type': 'minor'
            })
        
        return periods
    
    def _calculate_intensity(self, phase_name: str, date: datetime) -> int:
        """
        Etetési intenzitás kiszámítása (0-100).
        A hold fázisától és a naptól függ.
        """
        # Telihold és újhold környékén magasabb az intenzitás
        if phase_name in ['Telihold', 'Újhold']:
            base_intensity = 80
        elif phase_name in ['Első negyed', 'Utolsó negyed']:
            base_intensity = 60
        else:
            base_intensity = 40
        
        # Napi változás (napközben alacsonyabb)
        hour = date.hour
        if 6 <= hour <= 18:
            intensity = base_intensity - 20
        else:
            intensity = base_intensity + 10
        
        return max(0, min(100, intensity))
    
    def _get_rating(self, intensity: int) -> str:
        """
        Értékelés az intenzitás alapján.
        """
        if intensity >= 80:
            return 'Kiváló'
        elif intensity >= 60:
            return 'Jó'
        elif intensity >= 40:
            return 'Közepes'
        else:
            return 'Gyenge'
