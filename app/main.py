from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from sqlalchemy.orm import Session
from datetime import datetime
import os
import uuid
from typing import Optional

from app.database import get_db, init_db
from app.models import HorgaszatiNaplo, Halfaj
from app.services.weather import WeatherService
from app.services.moon import MoonPhaseService
from app.services.location import LocationService
from app.services.analysis import AnalysisService

app = FastAPI(title="Horgász Alkalmazás")

# Statikus fájlok
os.makedirs("static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Szolgáltatások
weather_service = WeatherService()
moon_service = MoonPhaseService()
location_service = LocationService()
analysis_service = AnalysisService()

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/", response_class=HTMLResponse)
async def root():
    return FileResponse("templates/index.html")

@app.get("/api/halfajok")
def get_halfajok(db: Session = Depends(get_db)):
    return db.query(Halfaj).filter(Halfaj.aktiv == True).all()

@app.get("/api/naplok")
def get_naplok(db: Session = Depends(get_db)):
    return db.query(HorgaszatiNaplo).order_by(HorgaszatiNaplo.datum.desc()).all()

@app.post("/api/naplo")
async def create_naplo(
    datum: str = Form(...),
    helyszin: str = Form(...),
    halfaj_id: int = Form(...),
    suly: Optional[float] = Form(None),
    hossz: Optional[float] = Form(None),
    csali: Optional[str] = Form(None),
    etetoanyag: Optional[str] = Form(None),
    pva_hasznalata: bool = Form(False),
    pva_tartalom: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    megjegyzes: Optional[str] = Form(None),
    fenym_kep: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    try:
        # Időjárás lekérése a helyszín alapján
        weather_data = None
        if latitude and longitude:
            weather_data = weather_service.get_weather(latitude, longitude)
        
        # Hold fázis számítása
        moon_phase = moon_service.get_moon_phase(datetime.utcnow())
        
        # Fénykép mentése
        kep_utvonala = None
        if fenym_kep:
            file_extension = fenym_kep.filename.split(".")[-1]
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            file_path = f"static/uploads/{unique_filename}"
            with open(file_path, "wb") as buffer:
                buffer.write(await fenym_kep.read())
            kep_utvonala = file_path
        
        # Napló létrehozása
        naplo = HorgaszatiNaplo(
            datum=datetime.strptime(datum, "%Y-%m-%d"),
            helyszin=helyszin,
            halfaj_id=halfaj_id,
            suly=suly,
            hossz=hossz,
            csali=csali,
            etetoanyag=etetoanyag,
            pva_hasznalata=pva_hasznalata,
            pva_tartalom=pva_tartalom,
            latitude=latitude,
            longitude=longitude,
            fenym_kep_utvonala=kep_utvonala,
            megjegyzes=megjegyzes,
            szelsebesseg=weather_data.get("wind_speed") if weather_data else None,
            selirany=weather_data.get("wind_direction") if weather_data else None,
            legnyomas=weather_data.get("pressure") if weather_data else None,
            homerseklet=weather_data.get("temperature") if weather_data else None,
            paratartalom=weather_data.get("humidity") if weather_data else None,
            hold_fazis=moon_phase
        )
        
        db.add(naplo)
        db.commit()
        db.refresh(naplo)
        
        return naplo
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/analizis")
def get_analizis(db: Session = Depends(get_db)):
    return analysis_service.generate_analysis(db)

@app.get("/api/javaslatok")
def get_javaslatok(
    latitude: float,
    longitude: float,
    db: Session = Depends(get_db)
):
    return analysis_service.generate_recommendations(latitude, longitude, db)

@app.get("/api/weather")
def get_weather(latitude: float, longitude: float):
    return weather_service.get_weather(latitude, longitude)

@app.get("/api/moon")
def get_moon():
    return {"moon_phase": moon_service.get_moon_phase(datetime.utcnow())}

@app.get("/api/reverse-geocode")
def reverse_geocode(latitude: float, longitude: float):
    """Helyszín lekérése GPS koordináták alapján"""
    return location_service.reverse_geocode(latitude, longitude)

@app.get("/api/statistics/monthly")
def get_monthly_statistics(db: Session = Depends(get_db)):
    """Havi statisztikák"""
    from sqlalchemy import func
    naplok = db.query(
        func.strftime('%Y-%m', HorgaszatiNaplo.datum).label('honap'),
        func.count(HorgaszatiNaplo.id).label('darab'),
        func.sum(HorgaszatiNaplo.suly).label('ossz_suly')
    ).group_by(func.strftime('%Y-%m', HorgaszatiNaplo.datum)).order_by(func.strftime('%Y-%m', HorgaszatiNaplo.datum)).all()
    
    return [
        {"honap": n.honap, "darab": n.darab, "ossz_suly": float(n.ossz_suly) if n.ossz_suly else 0}
        for n in naplok
    ]

@app.get("/api/statistics/fish-species")
def get_fish_species_statistics(db: Session = Depends(get_db)):
    """Halfaj szerinti statisztikák"""
    from sqlalchemy import func
    stat = db.query(
        Halfaj.nev,
        func.count(HorgaszatiNaplo.id).label('darab'),
        func.avg(HorgaszatiNaplo.suly).label('atlag_suly'),
        func.max(HorgaszatiNaplo.suly).label('max_suly')
    ).join(Halfaj, HorgaszatiNaplo.halfaj_id == Halfaj.id).group_by(Halfaj.nev).all()
    
    return [
        {"halfaj": s.nev, "darab": s.darab, "atlag_suly": float(s.atlag_suly) if s.atlag_suly else 0, "max_suly": float(s.max_suly) if s.max_suly else 0}
        for s in stat
    ]

@app.get("/api/statistics/locations")
def get_location_statistics(db: Session = Depends(get_db)):
    """Helyszín szerinti statisztikák"""
    from sqlalchemy import func
    stat = db.query(
        HorgaszatiNaplo.helyszin,
        func.count(HorgaszatiNaplo.id).label('darab'),
        func.sum(HorgaszatiNaplo.suly).label('ossz_suly')
    ).group_by(HorgaszatiNaplo.helyszin).order_by(func.count(HorgaszatiNaplo.id).desc()).all()
    
    return [
        {"helyszin": s.helyszin, "darab": s.darab, "ossz_suly": float(s.ossz_suly) if s.ossz_suly else 0}
        for s in stat
    ]

@app.get("/api/statistics/moon-phase")
def get_moon_phase_statistics(db: Session = Depends(get_db)):
    """Holdfázis szerinti statisztikák"""
    from sqlalchemy import func
    stat = db.query(
        HorgaszatiNaplo.hold_fazis,
        func.count(HorgaszatiNaplo.id).label('darab'),
        func.avg(HorgaszatiNaplo.suly).label('atlag_suly')
    ).group_by(HorgaszatiNaplo.hold_fazis).all()
    
    return [
        {"hold_fazis": s.hold_fazis, "darab": s.darab, "atlag_suly": float(s.atlag_suly) if s.atlag_suly else 0}
        for s in stat
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
