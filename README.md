# Horgász Alkalmazás

Modern, Python alapú online horgászati naplóvezető alkalmazás időjárással, térképpel és elemzéssel.

## Funkciók

- **Fénykép feltöltés**: Horgászati fogások fotózása és feltöltése
- **Helymeghatározás**: GPS koordináták rögzítése és OpenStreetMap integráció
- **Időjárás**: Valós idejű időjárás adatok a tartózkodási hely szerint (szélsebesség, szélirány, légnyomás, hőmérséklet, páratartalom)
- **Halfaj kiválasztás**: 12+ halfaj támogatása részletes leírással
- **Részletes adatok**: Súly, hossz, csali, etetőanyag, PVA használat rögzítése
- **Hold fázis**: Hold fázis számítása és hatásainak elemzése
- **Elemzés**: Átfogó statisztikák és táblázatok a horgászati adatokból
- **Javaslatok**: Automatikus javaslatok az aktuális feltételek alapján
- **Modern UI**: Reszponzív, felhasználóbarát felület Bootstrap-pal és Leaflet-tel

## Telepítés

### Követelmények

- Python 3.8 vagy újabb
- pip (Python csomagkezelő)

### Lépések

1. **Klónozás vagy letöltés**:
   ```bash
   cd "c:/Horgasz app"
   ```

2. **Függőségek telepítése**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Környezeti változók beállítása** (opcionális):
   ```bash
   copy .env.example .env
   ```
   Szerkessze a `.env` fájlt, és adja hozzá az OpenWeatherMap API kulcsát (opcionális, demo mód működik nélküle).

4. **Adatbázis inicializálása**:
   ```bash
   python -m app.init_db
   ```

5. **Alkalmazás indítása**:
   ```bash
   python -m app.main
   ```
   Vagy uvicornnal:
   ```bash
   uvicorn app.main:app --reload
   ```

6. **Böngésző megnyitása**:
   Nyissa meg a http://localhost:8000 címet a böngészőjében.

## Használat

### Horgászati Napló

1. Kattintson a "Napló" fülre
2. Töltse ki az űrlapot:
   - Dátum
   - Helyszín
   - Halfaj kiválasztása
   - Súly és hossz megadása
   - Csali és etetőanyag
   - PVA használat
   - Koordináták (vagy kattintson a "Helymeghatározás" gombra)
   - Fénykép feltöltése (opcionális)
   - Megjegyzés
3. Kattintson a "Mentés" gombra

### Elemzés

1. Kattintson az "Elemzés" fülre
2. Tekintse meg a statisztikákat:
   - Halfajonkénti fogások
   - Időjárás alapú elemzés
   - Csali statisztika
   - Hold fázis statisztika
   - Helyszín statisztika

### Javaslatok

1. Kattintson a "Javaslatok" fülre
2. Kattintson a "Javaslatok lekérése" gombra
3. Az alkalmazás javaslatokat ad az aktuális időjárás és hold fázis alapján

### Térkép

1. Kattintson a "Térkép" fülre
2. Tekintse meg a horgászati helyszíneket a térképen
3. A marker-ekre kattintva részleteket láthat

## API Végpontok

### GET `/api/halfajok`
Visszaadja az összes aktív halfajt.

### GET `/api/naplok`
Visszaadja az összes horgászati naplót.

### POST `/api/naplo`
Új horgászati napló létrehozása.

### GET `/api/analizis`
Átfogó elemzés generálása.

### GET `/api/javaslatok?latitude={lat}&longitude={lon}`
Javaslatok generálása a megadott koordinátákhoz.

### GET `/api/weather?latitude={lat}&longitude={lon}`
Időjárás adatok lekérése.

### GET `/api/moon`
Hold fázis lekérése.

## Technológiák

- **Backend**: FastAPI (Python)
- **Adatbázis**: SQLite (SQLAlchemy ORM)
- **Frontend**: Bootstrap 5, Leaflet (OpenStreetMap)
- **Időjárás**: OpenWeatherMap API
- **Hold fázis**: Astral könyvtár
- **Helymeghatározás**: Geopy
- **Elemzés**: Pandas, NumPy

## Adatbázis Modell

### Halfaj
- id
- nev
- latin_nev
- leiras
- aktiv

### HorgaszatiNaplo
- id
- datum
- helyszin
- szelsebesseg
- selirany
- legnyomas
- homerseklet
- paratartalom
- hold_fazis
- halfaj_id
- suly
- hossz
- csali
- etetoanyag
- pva_hasznalata
- latitude
- longitude
- fenym_kep_utvonala
- megjegyzes

## Demo Mód

Az alkalmazás demo módban működik OpenWeatherMap API kulcs nélkül is. Ebben az esetben demo időjárás adatok kerülnek visszaadásra.

## Licenc

Ez a projekt oktatási és személyes használatra készült.

## Fejlesztő

Cascade AI Assistant

## Támogatás

Probléma esetén kérem, ellenőrizze:
- Python verzió (3.8+)
- Függőségek telepítése
- Adatbázis inicializálása
- Port 8000 elérhetősége
