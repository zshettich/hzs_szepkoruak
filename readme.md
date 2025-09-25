# Szépkorúak Regisztrációs Alkalmazás

## Hallgató
Név:Hettich Zsolt
Neptunkód: ZAJDU4

## Feladat leírása
Ez az alkalmazás a szépkorúak (65 év feletti idősek) regisztrációját szolgálja egy 2025-ös előadásra. Az előadást minden évben Szekszárd Város Önkormányzata szervezi, így a programot valós környezetben is használják.

Az alkalmazás lehetővé teszi az adatbázisban szereplő személyek keresését, adatainak megtekintését, valamint regisztrálását délelőtti vagy délutáni időpontokra. A program grafikus felhasználói felülettel rendelkezik, és SQL Server adatbázist használ.

Ezt a regisztrációs feladatot korábban egy régebbi szoftverrel és Excel-táblák segítségével végezték, ezért aktuálissá vált a rendszer fejlesztése.

2025 augusztusa óta dolgozom itt rendszergazdaként, és ez a projekt lehetőséget biztosított számomra a cégen belüli szakmai előrelépésre, valamint az elvárt projektfeladat megvalósítására. 

Korábban is foglalkoztam programozással, főként webes területen, azonban a Pythonnal most találkoztam először gyakorlati szinten.

## Modulok és a modulokban használt függvények

### Tanult modulok:
- **tkinter**: Grafikus felhasználói felület létrehozása
  - `Tk()`, `Frame()`, `Label()`, `Entry()`, `Button()`, `Radiobutton()`, `messagebox.showinfo()`, `messagebox.showerror()`, `messagebox.showwarning()`
  - `ttk.Treeview()`, `ttk.Style()`
- **pyodbc**: Adatbázis kapcsolat kezelése
  - `connect()`, `cursor()`, `execute()`, `fetchall()`, `fetchone()`, `commit()`, `close()`
- **datetime**: Dátum és idő kezelés
  - `datetime.now()`, `strftime()`
- **getpass**: Rendszer felhasználó lekérdezése
  - `getuser()`
- **re**: Reguláris kifejezések
  - `search()`, `match()`

### Bemutatandó modul:
**gk_segito_fuggvenyek.py**
- `validalas_email(email)` - Email cím validálása
- `validalas_telefon(telefon)` - Telefonszám validálása
- `format_datum(datum)` - Dátum formázása
- `validalas_szuletesi_datum(datum_str)` - Születési dátum érvényességének ellenőrzése
- `kor_szamitas(szuletesi_datum)` - Életkor számítása
- `szoveg_tisztitas(szoveg)` - Szöveg megtisztítása felesleges karakterektől
- `datum_formatalo(datum, format_tipus)` - Dátum különböző formátumokba alakítása
- `iranyitoszam_validalas(iranyitoszam)` - Irányítószám ellenőrzése
- `nev_formatalo(vezeteknev, keresztnev)` - Teljes név összeállítása

### Saját modul:
**gk_szepkoruak_modul.py** - Főmodul a GK monogrammal
- Tartalmazza a GKSzepkoruakOsztaly osztályt
- Összes GUI és adatbázis kezelő függvény GK előtaggal

## Osztály(ok)
**GKSzepkoruakOsztaly** - A főosztály, amely tartalmazza:
- GUI kezelés
- Adatbázis műveletek
- Eseménykezelés
- Regisztrációs logika

## Indításhoz szükséges modulok
- tkinter (általában beépített a Python-ba)
- pyodbc (telepíteni kell: `pip install pyodbc`)
- ODBC Driver 17 for SQL Server (külön telepítés szükséges)

## Indítás
```bash
python main.py
```

## Funkciók
- Személyek keresése név alapján
- Részletes személyi adatok megjelenítése
- Regisztráció délelőtti (10:00) vagy délutáni (14:00) időpontra
- Regisztráltak számának követése időpontok szerint
- Adatbázis kapcsolat kezelése