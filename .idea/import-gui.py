import configparser
from datetime import datetime
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import pyodbc

# Segédfüggvény a születési dátum ellenőrzéséhez
from hzs_segito_fuggvenyek import validalas_szuletesi_datum


def clean_val(val):
    if pd.isna(val):
        return ""
    s = str(val).strip()
    return "" if s.lower() == "nan" else s


def clean_hazszam(val):
    s = clean_val(val)
    if not s:
        return ""
    if "-" in s:
        parts = s.split("-")
        return f"{parts[0].lstrip('0') or '0'}-{parts[1].lstrip('0') or '0'}"
    if "/" in s:
        parts = s.split("/")
        p1 = parts[0].lstrip("0") or "0"
        p2 = parts[1].lstrip("0") or parts[1]
        return f"{p1}/{p2}"
    res = s.lstrip("0")
    return res if res else "0"


def clean_date(val):
    s = clean_val(val).split(".")[0]
    if len(s) == 8 and s.isdigit():
        return f"{s[:4]}-{s[4:6]}-{s[6:]}"
    return None


class ImportAblak:

    def __init__(self, root):
        self.root = root
        self.root.title("Szépkorúak - Adatbázis importáló")
        self.root.geometry("880x620")
        self.root.configure(bg="#f0f0f0")

        self.loaded_df = None
        self.hzs_load_config()
        self.hzs_create_widgets()
        self.hzs_frissit_db_statusz()

        # Ha létezik az alapértelmezett CSV, próbáljuk meg előtölteni
        if os.path.exists(self.csv_path):
            self.hzs_betolt_csv_elonezet(self.csv_path)

    def hzs_load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), "config.ini")
        if not os.path.exists(config_path):
            config_path = "config.ini"

        config = configparser.ConfigParser()
        if os.path.exists(config_path):
            config.read(config_path, encoding="utf-8")
            db = config["DATABASE"]
            self.conn_str = (
                f"DRIVER={db.get('driver', '{ODBC Driver 17 for SQL Server}')};"
                f"SERVER={db.get('server')};"
                f"DATABASE={db.get('database')};"
                f"UID={db.get('uid')};"
                f"PWD={db.get('pwd')};"
            )
            self.db_name = db.get("database", "szepkor2026t")
            import_cfg = config["IMPORT"] if "IMPORT" in config else {}
            self.csv_path = import_cfg.get("forras_csv", "Nyugdíjas_2026_adatok.csv")
            self.kodolas = import_cfg.get("kodolas", "cp1250")
        else:
            self.conn_str = ""
            self.db_name = "Ismeretlen"
            self.csv_path = "Nyugdíjas_2026_adatok.csv"
            self.kodolas = "cp1250"

    def hzs_create_widgets(self):
        # Fejléc
        tk.Label(
            self.root,
            text="ADATOK IMPORTÁLÁSA ADATBÁZISBA",
            fg="#0b63b6",
            bg="#f0f0f0",
            font=("Arial", 16, "bold"),
        ).pack(pady=(12, 2))

        tk.Label(
            self.root,
            text=f"Cél adatbázis: {self.db_name}",
            fg="#0078d7",
            bg="#f0f0f0",
            font=("Arial", 12, "bold"),
        ).pack(pady=(0, 10))

        # 1. Fájlkiválasztás keret
        file_frame = tk.LabelFrame(
            self.root,
            text=" Forrás CSV kiválasztása ",
            bg="#f0f0f0",
            font=("Arial", 10, "bold"),
        )
        file_frame.pack(fill="x", padx=15, pady=5)

        sub_file = tk.Frame(file_frame, bg="#f0f0f0")
        sub_file.pack(fill="x", padx=10, pady=8)

        self.entry_filepath = tk.Entry(sub_file, font=("Arial", 10))
        self.entry_filepath.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_filepath.insert(0, os.path.abspath(self.csv_path))

        btn_browse = tk.Button(
            sub_file,
            text="Tallózás...",
            bg="#0288d1",
            fg="white",
            font=("Arial", 9, "bold"),
            command=self.hzs_tallozas,
        )
        btn_browse.pack(side="left", padx=(0, 5))

        btn_reload = tk.Button(
            sub_file,
            text="Betöltés / Frissítés",
            bg="#455a64",
            fg="white",
            font=("Arial", 9, "bold"),
            command=lambda: self.hzs_betolt_csv_elonezet(self.entry_filepath.get()),
        )
        btn_reload.pack(side="left")

        # 2. Információs / Állapot sáv
        info_frame = tk.Frame(self.root, bg="#f0f0f0")
        info_frame.pack(fill="x", padx=15, pady=4)

        self.lbl_csv_info = tk.Label(
            info_frame,
            text="CSV: nincs betöltve",
            font=("Arial", 10, "bold"),
            fg="#2e7d32",
            bg="#f0f0f0",
        )
        self.lbl_csv_info.pack(side="left")

        self.lbl_db_info = tk.Label(
            info_frame,
            text="Tábla állapota: Lekérdezés...",
            font=("Arial", 10, "bold"),
            fg="#d97706",
            bg="#f0f0f0",
        )
        self.lbl_db_info.pack(side="right")

        # 3. Előnézet táblázat
        tree_group = tk.LabelFrame(
            self.root,
            text=" CSV Adatok előnézete (első 15 sor feldolgozva) ",
            bg="#f0f0f0",
            font=("Arial", 10, "bold"),
        )
        tree_group.pack(fill="both", expand=True, padx=15, pady=6)

        cols = ("nev", "szuletes", "irsz", "telepules", "cim", "lepcsohaz", "szint", "ajto")
        self.tree = ttk.Treeview(tree_group, columns=cols, show="headings", height=8)

        headers = {
            "nev": "Név",
            "szuletes": "Születési idő",
            "irsz": "Irsz",
            "telepules": "Település",
            "cim": "Közterület és házszám",
            "lepcsohaz": "Lépcsőház/Épület",
            "szint": "Szint",
            "ajto": "Ajtó",
        }
        widths = {
            "nev": 160,
            "szuletes": 95,
            "irsz": 60,
            "telepules": 90,
            "cim": 180,
            "lepcsohaz": 110,
            "szint": 50,
            "ajto": 50,
        }

        for c, h in headers.items():
            self.tree.heading(c, text=h)
            self.tree.column(c, width=widths[c], anchor="w")

        vsb = ttk.Scrollbar(tree_group, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_group, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=hsb.set, yscrollcommand=vsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_group.grid_rowconfigure(0, weight=1)
        tree_group.grid_columnconfigure(0, weight=1)

        # 4. Beállítások és Műveleti gombok
        action_frame = tk.Frame(self.root, bg="#f0f0f0")
        action_frame.pack(fill="x", padx=15, pady=8)

        self.var_truncate = tk.BooleanVar(value=True)
        self.chk_truncate = tk.Checkbutton(
            action_frame,
            text="Tábla ürítése (törlése) importálás előtt [Ajánlott]",
            variable=self.var_truncate,
            font=("Arial", 10, "bold"),
            fg="#c62828",
            bg="#f0f0f0",
        )
        self.chk_truncate.pack(side="left")

        btn_exit = tk.Button(
            action_frame,
            text="Kilépés",
            bg="#616161",
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.root.destroy,
            padx=15,
            pady=4,
        )
        btn_exit.pack(side="right")

        self.btn_import = tk.Button(
            action_frame,
            text=" Importálás indítása",
            bg="#2e7d32",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=6,
            command=self.hzs_indit_import,
        )
        self.btn_import.pack(side="right", padx=10)

        # Státuszsor
        self.status_bar = tk.Label(
            self.root,
            text="Kész",
            bd=1,
            relief="sunken",
            anchor="w",
            bg="#e0e0e0",
            padx=5,
            pady=3,
        )
        self.status_bar.pack(side="bottom", fill="x")

    def hzs_tallozas(self):
        filename = filedialog.askopenfilename(
            title="Válassz CSV állományt",
            filetypes=[("CSV fájlok", "*.csv"), ("Minden fájl", "*.*")],
        )
        if filename:
            self.entry_filepath.delete(0, tk.END)
            self.entry_filepath.insert(0, filename)
            self.hzs_betolt_csv_elonezet(filename)

    def hzs_frissit_db_statusz(self):
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Regisztraciok")
            db_count = cursor.fetchone()[0]
            conn.close()
            self.lbl_db_info.config(text=f"Adatbázisban jelenleg: {db_count} sor")
        except Exception as e:
            self.lbl_db_info.config(text="Adatbázis: Nem érhető el")

    def hzs_betolt_csv_elonezet(self, filepath):
        if not os.path.exists(filepath):
            self.lbl_csv_info.config(text="CSV: A megadott fájl nem létezik!")
            return

        try:
            try:
                self.loaded_df = pd.read_csv(filepath, encoding=self.kodolas, dtype=str)
            except Exception:
                self.loaded_df = pd.read_csv(filepath, encoding="utf-8", dtype=str)

            total_rows = len(self.loaded_df)
            self.lbl_csv_info.config(text=f"CSV: {total_rows} sor beolvasva ({os.path.basename(filepath)})")

            for item in self.tree.get_children():
                self.tree.delete(item)

            for _, r in self.loaded_df.head(15).iterrows():
                dr = clean_val(r.get("Viselt név DR jelző "))
                nev = clean_val(r.get("Viselt név - teljes"))
                teljes_nev = f"{dr} {nev}".strip() if dr else nev

                ep = clean_val(r.get("LH:Épület"))
                lh = clean_val(r.get("LH:Lépcsőház"))
                lph = f"{ep} ép. {lh} lph." if ep and lh else (f"{ep} ép." if ep else lh)

                kozterulet = f"{clean_val(r.get('LH:Közterület név'))} {clean_val(r.get('LH:Közterület jelleg'))} {clean_hazszam(r.get('LH:Hsz/Hrsz'))}".strip()

                self.tree.insert(
                    "",
                    tk.END,
                    values=(
                        teljes_nev,
                        clean_date(r.get("Születési idő ")),
                        clean_val(r.get("LH:PIR ")),
                        clean_val(r.get("LH:Település ")),
                        kozterulet,
                        lph,
                        clean_val(r.get("LH:Szint")),
                        clean_val(r.get("LH:Ajtó")),
                    ),
                )
            self.status_bar.config(text="CSV előnézet betöltve")
        except Exception as e:
            messagebox.showerror("Hiba", f"Nem sikerült beolvasni a CSV-t:\n{e}")

    def hzs_indit_import(self):
        filepath = self.entry_filepath.get().strip()
        if not os.path.exists(filepath):
            messagebox.showwarning("Figyelem", "A kiválasztott CSV fájl nem létezik!")
            return

        if self.loaded_df is None:
            self.hzs_betolt_csv_elonezet(filepath)

        truncate = self.var_truncate.get()
        confirm_msg = (
            f"Biztosan elindítod az importálást?\n\n"
            f"Fájl: {os.path.basename(filepath)}\n"
            f"Sorok száma: {len(self.loaded_df)}\n"
            f"Tábla ürítése: {'IGEN (Minden korábbi adat törlődik)' if truncate else 'NEM (Hozzáírás)'}"
        )
        if not messagebox.askyesno("Megerősítés", confirm_msg):
            return

        try:
            self.status_bar.config(text="Importálás folyamatban...")
            self.root.update_idletasks()

            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()

            if truncate:
                cursor.execute("DELETE FROM Regisztraciok")
                conn.commit()

            insert_sql = """
                INSERT INTO Regisztraciok (
                    teljesNev, iranyitoszam, telepules, kozteruletNev,
                    kozteruletJelleg, hazszam, lepcsohaz, szint, ajto,
                    szuletesiIdo, regisztralt
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            """

            records = []
            hibas_datum_db = 0
            for idx, r in self.loaded_df.iterrows():
                dr = clean_val(r.get("Viselt név DR jelző "))
                nev = clean_val(r.get("Viselt név - teljes"))
                teljes_nev = f"{dr} {nev}".strip() if dr else nev

                ep = clean_val(r.get("LH:Épület"))
                lh = clean_val(r.get("LH:Lépcsőház"))
                lph_ertek = f"{ep} ép. {lh} lph." if ep and lh else (f"{ep} ép." if ep else lh)

                raw_szul = r.get("Születési idő ")
                szul_datum = clean_date(raw_szul)
                if szul_datum and not validalas_szuletesi_datum(szul_datum):
                    szul_datum = None
                    hibas_datum_db += 1

                records.append((
                    teljes_nev,
                    clean_val(r.get("LH:PIR ")),
                    clean_val(r.get("LH:Település ")),
                    clean_val(r.get("LH:Közterület név")),
                    clean_val(r.get("LH:Közterület jelleg")),
                    clean_hazszam(r.get("LH:Hsz/Hrsz")),
                    lph_ertek,
                    clean_val(r.get("LH:Szint")),
                    clean_val(r.get("LH:Ajtó")),
                    szul_datum,
                ))

            cursor.fast_executemany = True
            cursor.executemany(insert_sql, records)
            conn.commit()
            conn.close()

            self.hzs_frissit_db_statusz()
            self.status_bar.config(text="Importálás sikeresen befejeződött!")

            siker_szoveg = f"Sikeres importálás!\n{len(records)} sor bekerült az adatbázisba."
            if hibas_datum_db > 0:
                siker_szoveg += f"\n(Figyelem: {hibas_datum_db} sornál a születési dátum érvénytelen volt, ott üres maradt.)"
            messagebox.showinfo("Siker", siker_szoveg)

        except Exception as e:
            self.status_bar.config(text="Hiba történt az importálás során")
            messagebox.showerror("Hiba", f"Hiba az importálás során:\n{e}")


def main():
    root = tk.Tk()
    app = ImportAblak(root)
    root.mainloop()


if __name__ == "__main__":
    main()