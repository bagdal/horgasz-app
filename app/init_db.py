from app.database import SessionLocal, init_db
from app.models import Halfaj

def init_halfajok():
    """Halfajok inicializálása az adatbázisban"""
    db = SessionLocal()
    
    try:
        # Ellenőrizzük, hogy vannak-e már halfajok
        existing = db.query(Halfaj).count()
        if existing > 0:
            print("Halfajok már léteznek az adatbázisban.")
            return
        
        # Halfajok hozzáadása
        halfajok = [
            Halfaj(
                nev="Ponty",
                latin_nev="Cyprinus carpio",
                leiras="A leggyakoribb halfaj Magyarországon. Meleg vizet kedvel, tavasztól őszig aktív."
            ),
            Halfaj(
                nev="Amur",
                latin_nev="Ctenopharyngodon idella",
                leiras="Növényevő halfaj, gyors úszó, erős harcos."
            ),
            Halfaj(
                nev="Csuka",
                latin_nev="Esox lucius",
                leiras="Ragadozó halfaj, tavasszal és ősszel a legaktívabb."
            ),
            Halfaj(
                nev="Süllő",
                latin_nev="Sander lucioperca",
                leiras="Értékes halfaj, éjszaka aktív, finom csali szükséges."
            ),
            Halfaj(
                nev="Harcsa",
                latin_nev="Silurus glanis",
                leiras="A legnagyobb édesvízi halfajunk, éjszaka aktív."
            ),
            Halfaj(
                nev="Kárász",
                latin_nev="Carassius carassius",
                leiras="Közönséges halfaj, könnyen fogható."
            ),
            Halfaj(
                nev="Compó",
                latin_nev="Tinca tinca",
                leiras="Alacsony oxigéntűrő halfaj, állóvizekben gyakori."
            ),
            Halfaj(
                nev="Balin",
                latin_nev="Aspius aspius",
                leiras="Gyors úszó ragadozó, folyóvizekben gyakori."
            ),
            Halfaj(
                nev="Márna",
                latin_nev="Barbus barbus",
                leiras="Folyóvizek halfaja, erős harcos."
            ),
            Halfaj(
                nev="Dévér",
                latin_nev="Abramis brama",
                leiras="Táplálékhal, gyakori a tavakban."
            ),
            Halfaj(
                nev="Keszeg",
                latin_nev="Blicca bjoerkna",
                leiras="Közönséges halfaj, könnyen fogható."
            ),
            Halfaj(
                nev="Domolykó",
                latin_nev="Squalius cephalus",
                leiras="Folyóvizek halfaja, aktív ragadozó."
            )
        ]
        
        db.add_all(halfajok)
        db.commit()
        print(f"{len(halfajok)} halfaj sikeresen hozzáadva az adatbázishoz.")
        
    except Exception as e:
        print(f"Hiba a halfajok inicializálásakor: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    init_halfajok()
