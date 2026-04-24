import google.generativeai as genai
import os
from typing import Optional, Dict, List
from PIL import Image
import io

class AIService:
    def __init__(self):
        # API kulcs környezeti változóból vagy alapértelmezett
        self.api_key = os.getenv('GEMINI_API_KEY', '')
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro-vision')
        else:
            self.model = None
    
    def identify_fish_from_image(self, image_path: str) -> Optional[Dict]:
        """
        Halfaj felismerése képből Gemini Vision használatával.
        """
        if not self.model:
            return None
        
        try:
            # Kép betöltése
            image = Image.open(image_path)
            
            # Prompt a halfaj felismeréshez
            prompt = """
            Felismerd a képen látható halfajt. Válaszold meg a következő kérdéseket:
            1. Milyen halfaj ez?
            2. Becsüld meg a hal súlyát (kg-ban)
            3. Becsüld meg a hal hosszát (cm-ben)
            
            Válaszold JSON formátumban a következő struktúrával:
            {
                "halfaj": "halfaj neve",
                "suly": súly kg-ban (szám),
                "hossz": hossz cm-ben (szám),
                "bizonyossag": "magas/közepes/alacsony"
            }
            """
            
            response = self.model.generate_content([prompt, image])
            text = response.text
            
            # Egyszerűsített parszolás
            return self._parse_fish_response(text)
            
        except Exception as e:
            print(f"AI halfaj felismerési hiba: {e}")
            return None
    
    def analyze_fishing_data(self, data: Dict) -> Optional[Dict]:
        """
        Horgászati adatok elemzése és tippek generálása.
        """
        if not self.model:
            return None
        
        try:
            # Prompt az elemzéshez
            prompt = f"""
            Elemezd a következő horgászati adatokat és adj tippeket:
            
            Adatok:
            - Helyszín: {data.get('helyszin', 'Nincs megadva')}
            - Dátum: {data.get('datum', 'Nincs megadva')}
            - Időjárás: {data.get('homerseklet', 'Nincs')}°C, {data.get('szelsebesseg', 'Nincs')} km/h szél, {data.get('paratartalom', 'Nincs')}% páratartalom
            - Hold fázis: {data.get('hold_fazis', 'Nincs')}
            - Halfaj: {data.get('halfaj', 'Nincs')}
            - Súly: {data.get('suly', 'Nincs')} kg
            - Csali: {data.get('csali', 'Nincs')}
            - Etetőanyag: {data.get('etetoanyag', 'Nincs')}
            
            Adj 3-5 horgászati tippet a feltételek alapján. Válaszold JSON formátumban:
            {{
                "tippek": ["tipp1", "tipp2", "tipp3"],
                "ertekeles": "rövid értékelés",
                "javaslat": "milyen csali/etetőanyag ajánlott"
            }}
            """
            
            response = self.model.generate_content(prompt)
            text = response.text
            
            return self._parse_analysis_response(text)
            
        except Exception as e:
            print(f"AI elemzési hiba: {e}")
            return None
    
    def _parse_fish_response(self, text: str) -> Dict:
        """
        Halfaj felismerési válasz parszolása.
        """
        try:
            # Egyszerűsített parszolás - kulcsszavak keresése
            result = {
                "halfaj": "Ismeretlen",
                "suly": None,
                "hossz": None,
                "bizonyossag": "alacsony"
            }
            
            lines = text.lower().split('\n')
            for line in lines:
                if 'halfaj' in line or 'fish' in line:
                    result["halfaj"] = line.split(':')[-1].strip().strip('"').strip("'") if ':' in line else result["halfaj"]
                elif 'súly' in line or 'weight' in line or 'suly' in line:
                    try:
                        result["suly"] = float(''.join(c for c in line if c.isdigit() or c == '.'))
                    except:
                        pass
                elif 'hossz' in line or 'length' in line:
                    try:
                        result["hossz"] = float(''.join(c for c in line if c.isdigit() or c == '.'))
                    except:
                        pass
                elif 'magas' in line or 'high' in line:
                    result["bizonyossag"] = "magas"
                elif 'közepes' in line or 'medium' in line:
                    result["bizonyossag"] = "közepes"
            
            return result
            
        except Exception as e:
            print(f"Parszolási hiba: {e}")
            return {"halfaj": "Ismeretlen", "suly": None, "hossz": None, "bizonyossag": "alacsony"}
    
    def _parse_analysis_response(self, text: str) -> Dict:
        """
        Elemzési válasz parszolása.
        """
        try:
            result = {
                "tippek": [],
                "ertekeles": "",
                "javaslat": ""
            }
            
            lines = text.split('\n')
            for line in lines:
                if 'tipp' in line.lower() or 'tip' in line.lower():
                    if ':' in line:
                        tipp = line.split(':')[-1].strip().strip('"').strip("'")
                        if tipp:
                            result["tippek"].append(tipp)
                elif 'értékelés' in line.lower() or 'ertekeles' in line.lower():
                    if ':' in line:
                        result["ertekeles"] = line.split(':')[-1].strip().strip('"').strip("'")
                elif 'javaslat' in line.lower():
                    if ':' in line:
                        result["javaslat"] = line.split(':')[-1].strip().strip('"').strip("'")
            
            # Ha nincsenek tippek, generálunk alapértelmezettet
            if not result["tippek"]:
                result["tippek"] = ["Válts csali típust", "Próbáld ki más etetőanyagot", "Figyeld a hold fázist"]
            
            return result
            
        except Exception as e:
            print(f"Parszolási hiba: {e}")
            return {
                "tippek": ["Válts csali típust", "Próbáld ki más etetőanyagot", "Figyeld a hold fázist"],
                "ertekeles": "Nem sikerült az elemzés",
                "javaslat": ""
            }
