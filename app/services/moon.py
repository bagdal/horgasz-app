from datetime import datetime
from astral import moon
import math

class MoonPhaseService:
    def get_moon_phase(self, date: datetime) -> str:
        """Hold fázis számítása a megadott dátumhoz"""
        try:
            phase = moon.phase(date)
            return self._phase_to_name(phase)
        except:
            return "Ismeretlen"
    
    def _phase_to_name(self, phase: float) -> str:
        """Hold fázis konvertálása névre"""
        # 0 = Újhold, 0.5 = Telihold, 0.25 = Növekvő holdnegyed, 0.75 = Csökkenő holdnegyed
        if phase < 0.05 or phase > 0.95:
            return "Újhold"
        elif 0.45 <= phase <= 0.55:
            return "Telihold"
        elif 0.20 <= phase < 0.30:
            return "Növekvő holdnegyed"
        elif 0.70 <= phase < 0.80:
            return "Csökkenő holdnegyed"
        elif phase < 0.5:
            return "Növekvő hold"
        else:
            return "Csökkenő hold"
    
    def get_moon_illumination(self, date: datetime) -> float:
        """Hold megvilágítottság százalékban"""
        phase = moon.phase(date)
        return (1 - math.cos(phase * 2 * math.pi)) / 2 * 100
