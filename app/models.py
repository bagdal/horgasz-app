from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Halfaj(Base):
    __tablename__ = "halfajok"
    
    id = Column(Integer, primary_key=True, index=True)
    nev = Column(String(100), nullable=False, unique=True)
    latin_nev = Column(String(100))
    leiras = Column(Text)
    aktiv = Column(Boolean, default=True)
    
    horgaszati_naplok = relationship("HorgaszatiNaplo", back_populates="halfaj")

class HorgaszatiNaplo(Base):
    __tablename__ = "horgaszati_naplok"
    
    id = Column(Integer, primary_key=True, index=True)
    datum = Column(DateTime, default=datetime.utcnow)
    helyszin = Column(String(200))
    szelsebesseg = Column(Float)  # km/h
    selirany = Column(String(50))  # É, D, K, NY, stb.
    legnyomas = Column(Float)  # hPa
    homerseklet = Column(Float)  # Celsius
    paratartalom = Column(Float)  # %
    hold_fazis = Column(String(50))
    
    # Halfaj adatok
    halfaj_id = Column(Integer, ForeignKey("halfajok.id"))
    halfaj = relationship("Halfaj", back_populates="horgaszati_naplok")
    suly = Column(Float)  # kg
    hossz = Column(Float)  # cm
    
    # Felszerelés és csali
    csali = Column(String(200))
    etetoanyag = Column(String(200))
    pva_hasznalata = Column(Boolean, default=False)
    pva_tartalom = Column(String(200))  # Mi volt a PVA-ban
    
    # Helymeghatározás
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Fénykép
    fenym_kep_utvonala = Column(String(500))
    
    # Megjegyzés
    megjegyzes = Column(Text)
    
    def __repr__(self):
        return f"<HorgaszatiNaplo {self.datum} - {self.helyszin}>"
