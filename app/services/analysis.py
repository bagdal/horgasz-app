from sqlalchemy.orm import Session
from app.models import HorgaszatiNaplo, Halfaj
from datetime import datetime, timedelta
import pandas as pd

class AnalysisService:
    def generate_analysis(self, db: Session):
        """Átfogó elemzés generálása a horgászati naplóból"""
        naplok = db.query(HorgaszatiNaplo).all()
        
        if not naplok:
            return {"uzenet": "Nincs elég adat az elemzéshez"}
        
        # Halfajonkénti statisztikák
        halfaj_stats = self._analyze_by_species(db)
        
        # Időjárás alapú elemzés
        weather_stats = self._analyze_by_weather(naplok)
        
        # Hold fázis alapú elemzés
        moon_stats = self._analyze_by_moon_phase(naplok)
        
        # Helyszín alapú elemzés
        location_stats = self._analyze_by_location(naplok)
        
        # Csali és etetőanyag elemzés
        bait_stats = self._analyze_by_bait(naplok)
        
        return {
            "halfaj_statisztika": halfaj_stats,
            "idobar_statisztika": weather_stats,
            "hold_fazis_statisztika": moon_stats,
            "helyszin_statisztika": location_stats,
            "csali_statisztika": bait_stats,
            "osszes_fogas": len(naplok),
            "atlagos_suly": self._calculate_average_weight(naplok)
        }
    
    def _analyze_by_species(self, db: Session):
        """Halfajonkénti elemzés"""
        results = []
        halfajok = db.query(Halfaj).filter(Halfaj.aktiv == True).all()
        
        for halfaj in halfajok:
            naplok = db.query(HorgaszatiNaplo).filter(
                HorgaszatiNaplo.halfaj_id == halfaj.id
            ).all()
            
            if naplok:
                sulyok = [n.suly for n in naplok if n.suly]
                results.append({
                    "halfaj": halfaj.nev,
                    "fogas_szam": len(naplok),
                    "atlagos_suly": sum(sulyok) / len(sulyok) if sulyok else 0,
                    "legnagyobb_suly": max(sulyok) if sulyok else 0,
                    "legkisebb_suly": min(sulyok) if sulyok else 0
                })
        
        return results
    
    def _analyze_by_weather(self, naplok):
        """Időjárás alapú elemzés"""
        results = {
            "szelsebesseg": {},
            "homerseklet": {},
            "legnyomas": {}
        }
        
        for naplo in naplok:
            if naplo.szelsebesseg:
                wind_range = self._get_wind_range(naplo.szelsebesseg)
                results["szelsebesseg"][wind_range] = results["szelsebesseg"].get(wind_range, 0) + 1
            
            if naplo.homerseklet:
                temp_range = self._get_temp_range(naplo.homerseklet)
                results["homerseklet"][temp_range] = results["homerseklet"].get(temp_range, 0) + 1
            
            if naplo.legnyomas:
                pressure_range = self._get_pressure_range(naplo.legnyomas)
                results["legnyomas"][pressure_range] = results["legnyomas"].get(pressure_range, 0) + 1
        
        return results
    
    def _analyze_by_moon_phase(self, naplok):
        """Hold fázis alapú elemzés"""
        results = {}
        
        for naplo in naplok:
            if naplo.hold_fazis:
                results[naplo.hold_fazis] = results.get(naplo.hold_fazis, 0) + 1
        
        return results
    
    def _analyze_by_location(self, naplok):
        """Helyszín alapú elemzés"""
        results = {}
        
        for naplo in naplok:
            if naplo.helyszin:
                results[naplo.helyszin] = results.get(naplo.helyszin, 0) + 1
        
        return dict(sorted(results.items(), key=lambda x: x[1], reverse=True)[:10])
    
    def _analyze_by_bait(self, naplok):
        """Csali és etetőanyag elemzés"""
        csali_stats = {}
        etetoanyag_stats = {}
        pva_stats = {"igen": 0, "nem": 0}
        
        for naplo in naplok:
            if naplo.csali:
                csali_stats[naplo.csali] = csali_stats.get(naplo.csali, 0) + 1
            if naplo.etetoanyag:
                etetoanyag_stats[naplo.etetoanyag] = etetoanyag_stats.get(naplo.etetoanyag, 0) + 1
            if naplo.pva_hasznalata:
                pva_stats["igen"] += 1
            else:
                pva_stats["nem"] += 1
        
        return {
            "csali": dict(sorted(csali_stats.items(), key=lambda x: x[1], reverse=True)[:10]),
            "etetoanyag": dict(sorted(etetoanyag_stats.items(), key=lambda x: x[1], reverse=True)[:10]),
            "pva": pva_stats
        }
    
    def _calculate_average_weight(self, naplok):
        """Átlagos súly számítása"""
        sulyok = [n.suly for n in naplok if n.suly]
        return sum(sulyok) / len(sulyok) if sulyok else 0
    
    def _get_wind_range(self, speed: float) -> str:
        """Szélsebesség kategória"""
        if speed < 5:
            return "Csendes (0-5 km/h)"
        elif speed < 15:
            return "Gyenge (5-15 km/h)"
        elif speed < 30:
            return "Közepes (15-30 km/h)"
        else:
            return "Erős (30+ km/h)"
    
    def _get_temp_range(self, temp: float) -> str:
        """Hőmérséklet kategória"""
        if temp < 10:
            return "Hideg (<10°C)"
        elif temp < 20:
            return "Hűvös (10-20°C)"
        elif temp < 30:
            return "Meleg (20-30°C)"
        else:
            return "Forró (30+°C)"
    
    def _get_pressure_range(self, pressure: float) -> str:
        """Légnyomás kategória"""
        if pressure < 1000:
            return "Alacsony (<1000 hPa)"
        elif pressure < 1020:
            return "Normál (1000-1020 hPa)"
        else:
            return "Magas (>1020 hPa)"
    
    def generate_recommendations(self, latitude: float, longitude: float, db: Session):
        """Javaslatok generálása az aktuális feltételek alapján"""
        from app.services.weather import WeatherService
        from app.services.moon import MoonPhaseService
        
        weather_service = WeatherService()
        moon_service = MoonPhaseService()
        
        # Aktuális feltételek
        weather = weather_service.get_weather(latitude, longitude)
        moon_phase = moon_service.get_moon_phase(datetime.utcnow())
        
        # Történelmi adatok alapján
        naplok = db.query(HorgaszatiNaplo).all()
        
        recommendations = []
        
        # Időjárás alapú javaslatok
        if weather:
            if weather["temperature"] < 10:
                recommendations.append("Hideg időben használj lassabb csali prezentációt és mélyebb vizeket keress.")
            elif weather["temperature"] > 25:
                recommendations.append("Meleg időben a halak a mélyebb, hűvösebb vizeket keresik.")
            
            if weather["wind_speed"] > 20:
                recommendations.append("Erős szélben használj nehezebb ólmokat és a széllel szemben horgássz.")
            
            if weather["pressure"] < 1000:
                recommendations.append("Alacsony légnyomás esetén a halak kevésbé aktívak, használj vonzóbb csaliokat.")
        
        # Hold fázis alapú javaslatok
        if moon_phase == "Telihold":
            recommendations.append("Telihold idején a halak éjszaka aktívabbak lehetnek.")
        elif moon_phase == "Újhold":
            recommendations.append("Újhold idején a halak nappal lehetnek aktívabbak.")
        
        # Történelmi adatok alapján
        if naplok:
            best_bait = self._get_best_bait(naplok)
            if best_bait:
                recommendations.append(f"A legjobb csali a múltból: {best_bait}")
        
        return {
            "aktualis_feltetelek": {
                "idobar": weather,
                "hold_fazis": moon_phase
            },
            "javaslatok": recommendations
        }
    
    def _get_best_bait(self, naplok):
        """Legjobb csali meghatározása a múltbeli adatokból"""
        csali_stats = {}
        for naplo in naplok:
            if naplo.csali and naplo.suly:
                if naplo.csali not in csali_stats:
                    csali_stats[naplo.csali] = {"count": 0, "total_weight": 0}
                csali_stats[naplo.csali]["count"] += 1
                csali_stats[naplo.csali]["total_weight"] += naplo.suly
        
        if csali_stats:
            best = max(csali_stats.items(), key=lambda x: x[1]["total_weight"] / x[1]["count"])
            return best[0]
        return None
