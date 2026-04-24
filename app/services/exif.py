from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from datetime import datetime
from typing import Dict, Optional, Tuple
import os

class ExifService:
    def __init__(self):
        pass
    
    def extract_exif_data(self, image_path: str) -> Optional[Dict]:
        """
        EXIF adatok kinyerése képből (GPS, dátum, idő).
        """
        try:
            if not os.path.exists(image_path):
                return None
            
            image = Image.open(image_path)
            exif_data = image._getexif()
            
            if not exif_data:
                return None
            
            # EXIF adatok konvertálása olvasható formátumba
            exif_dict = {}
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                exif_dict[tag] = value
            
            # GPS adatok kinyerése
            gps_data = self._extract_gps_data(exif_dict)
            
            # Dátum és idő kinyerése
            date_time = self._extract_datetime(exif_dict)
            
            return {
                'gps': gps_data,
                'datetime': date_time,
                'raw_exif': exif_dict
            }
            
        except Exception as e:
            print(f"EXIF extraction error: {e}")
            return None
    
    def _extract_gps_data(self, exif_dict: Dict) -> Optional[Dict]:
        """
        GPS koordináták kinyerése EXIF adatokból.
        """
        gps_info = exif_dict.get('GPSInfo')
        
        if not gps_info:
            return None
        
        try:
            # GPS koordináták konvertálása
            gps_data = {}
            
            for key in gps_info.keys():
                name = GPSTAGS.get(key, key)
                gps_data[name] = gps_info[key]
            
            # Szélesség és hosszúság konvertálása
            lat = self._convert_to_degrees(gps_data.get('GPSLatitude'))
            lon = self._convert_to_degrees(gps_data.get('GPSLongitude'))
            
            if lat is None or lon is None:
                return None
            
            # Irányjelzők figyelembe vétele
            lat_ref = gps_data.get('GPSLatitudeRef')
            lon_ref = gps_data.get('GPSLongitudeRef')
            
            if lat_ref == 'S':
                lat = -lat
            if lon_ref == 'W':
                lon = -lon
            
            return {
                'latitude': lat,
                'longitude': lon
            }
            
        except Exception as e:
            print(f"GPS extraction error: {e}")
            return None
    
    def _convert_to_degrees(self, value) -> Optional[float]:
        """
        GPS koordináta konvertálása fokokra.
        """
        if value is None:
            return None
        
        try:
            degrees = float(value[0])
            minutes = float(value[1])
            seconds = float(value[2])
            
            return degrees + (minutes / 60.0) + (seconds / 3600.0)
            
        except (IndexError, TypeError, ValueError):
            return None
    
    def _extract_datetime(self, exif_dict: Dict) -> Optional[datetime]:
        """
        Dátum és idő kinyerése EXIF adatokból.
        """
        # Különböző dátum mezők próbálása
        date_fields = ['DateTimeOriginal', 'DateTime', 'DateTimeDigitized']
        
        for field in date_fields:
            date_str = exif_dict.get(field)
            if date_str:
                try:
                    # EXIF dátum formátum: YYYY:MM:DD HH:MM:SS
                    return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                except (ValueError, TypeError):
                    continue
        
        return None
    
    def extract_exif_from_file(self, file_content: bytes) -> Optional[Dict]:
        """
        EXIF adatok kinyerése közvetlenül a fájl tartalmából (feltöltés esetén).
        """
        try:
            import io
            image = Image.open(io.BytesIO(file_content))
            exif_data = image._getexif()
            
            if not exif_data:
                return None
            
            # EXIF adatok konvertálása
            exif_dict = {}
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                exif_dict[tag] = value
            
            # GPS adatok kinyerése
            gps_data = self._extract_gps_data(exif_dict)
            
            # Dátum és idő kinyerése
            date_time = self._extract_datetime(exif_dict)
            
            return {
                'gps': gps_data,
                'datetime': date_time
            }
            
        except Exception as e:
            print(f"EXIF extraction from file error: {e}")
            return None
