import re
from datetime import datetime


def validalas_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validalas_telefon(telefon):
    pattern = r'^(\+36|06)?[-\s]?[1-9][0-9]{7,8}$'
    return re.match(pattern, telefon) is not None


def format_datum(datum):
    if isinstance(datum, datetime):
        return datum.strftime("%Y-%m-%d %H:%M:%S")
    return str(datum) if datum else ""


def validalas_szuletesi_datum(datum_str):
    try:
        datum = datetime.strptime(datum_str, "%Y-%m-%d")
        return datum.year >= 1900 and datum <= datetime.now()
    except ValueError:
        return False


def kor_szamitas(szuletesi_datum):
    if isinstance(szuletesi_datum, datetime):
        ma = datetime.now()
        kor = ma.year - szuletesi_datum.year
        if ma.month < szuletesi_datum.month or (ma.month == szuletesi_datum.month and ma.day < szuletesi_datum.day):
            kor -= 1
        return kor
    return 0


def szoveg_tisztitas(szoveg):
    if not szoveg:
        return ""
    return szoveg.strip().replace("\n", " ").replace("\t", " ")


def datum_formatalo(datum, format_tipus="rövid"):
    if not datum:
        return ""

    if isinstance(datum, str):
        try:
            datum = datetime.strptime(datum, "%Y-%m-%d")
        except ValueError:
            return datum

    if format_tipus == "rövid":
        return datum.strftime("%Y-%m-%d")
    elif format_tipus == "hosszú":
        return datum.strftime("%Y. %B %d.")
    elif format_tipus == "teljes":
        return datum.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return datum.strftime("%Y-%m-%d")


def iranyitoszam_validalas(iranyitoszam):
    if not iranyitoszam:
        return False
    return len(str(iranyitoszam)) == 4 and str(iranyitoszam).isdigit()


def nev_formatalo(vezeteknev, keresztnev):
    if vezeteknev and keresztnev:
        return f"{vezeteknev.strip()} {keresztnev.strip()}"
    elif vezeteknev:
        return vezeteknev.strip()
    elif keresztnev:
        return keresztnev.strip()
    else:
        return ""