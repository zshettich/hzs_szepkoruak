import configparser
from datetime import datetime
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import pyodbc


class ExportAblak:

    def __init__(self, root):
        self.root = root
        self.root.title("Szépkorúak - Regisztráltak exportálása")
        self.root.geometry("880x580")
        self.root.configure(bg="#f0f0f0")

        self.hzs_load_config()
        self.hzs_create_widgets()
        self.hzs_frissites()

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
        else:
            self.conn_str = ""
            self.db_name = "Ismeretlen"

    def hzs_create_widgets(self):
        # Fejléc címek
        tk.Label(
            self.root,
            text="REGISZTRÁLTAK EXPORTÁLÁSA",
            fg="#0b63b6",
            bg="#f0f0f0",
            font=("Arial", 16, "bold"),
        ).pack(pady=(12, 2))

        tk.Label(
            self.root,
            text=f"Adatbázis: {self.db_name}",
            fg="#0078d7",
            bg="#f0f0f0",
            font=("Arial", 12, "bold"),
        ).pack(pady=(0, 10))

        # Statisztikák keret
        stat_group = tk.LabelFrame(
            self.root,
            text=" Statisztikák ",
            bg="#f0f0f0",
            font=("Arial", 10, "bold"),
        )
        stat_group.pack(fill="x", padx=15, pady=5)

        stat_grid = tk.Frame(stat_group, bg="#f0f0f0")
        stat_grid.pack(fill="x", padx=10, pady=8)

        self.lbl_osszes = tk.Label(
            stat_grid,
            text=" Összes regisztrált: 0",
            fg="#2e7d32",
            bg="#f0f0f0",
            font=("Arial", 11, "bold"),
        )
        self.lbl_osszes.grid(row=0, column=0, sticky="w", padx=(0, 50))

        self.lbl_du = tk.Label(
            stat_grid,
            text=" Délután (14:00): 0",
            bg="#f0f0f0",
            font=("Arial", 10),
        )
        self.lbl_du.grid(row=0, column=1, sticky="w")

        self.lbl_de = tk.Label(
            stat_grid,
            text=" Délelőtt (10:00): 0",
            bg="#f0f0f0",
            font=("Arial", 10),
        )
        self.lbl_de.grid(row=1, column=0, sticky="w", pady=(5, 0))

        self.lbl_nem_reg = tk.Label(
            stat_grid,
            text=" Még nem regisztrált: 0",
            fg="#d97706",
            bg="#f0f0f0",
            font=("Arial", 10),
        )
        self.lbl_nem_reg.grid(
            row=1, column=1, sticky="w", pady=(5, 0)
        )

        # Adatok előnézete keret
        tree_group = tk.LabelFrame(
            self.root,
            text=" Adatok előnézete (első 15 sor) ",
            bg="#f0f0f0",
            font=("Arial", 10, "bold"),
        )
        tree_group.pack(fill="both", expand=True, padx=15, pady=8)

        cols = (
            "nev",
            "szuletes",
            "telepules",
            "cim",
            "email",
            "telefon",
            "reg_datum",
            "felhasznalo",
            "eloadas",
        )
        self.tree = ttk.Treeview(
            tree_group, columns=cols, show="headings", height=8
        )

        headers = {
            "nev": "Név",
            "szuletes": "Születés",
            "telepules": "Település",
            "cim": "Cím",
            "email": "Email",
            "telefon": "Telefon",
            "reg_datum": "Regisztrált",
            "felhasznalo": "Felhasználó",
            "eloadas": "Előadás",
        }
        widths = {
            "nev": 140,
            "szuletes": 85,
            "telepules": 85,
            "cim": 140,
            "email": 80,
            "telefon": 80,
            "reg_datum": 90,
            "felhasznalo": 85,
            "eloadas": 65,
        }

        for c, h in headers.items():
            self.tree.heading(c, text=h)
            self.tree.column(c, width=widths[c], anchor="w")

        # Gördítősávok
        vsb = ttk.Scrollbar(
            tree_group, orient="vertical", command=self.tree.yview
        )
        hsb = ttk.Scrollbar(
            tree_group, orient="horizontal", command=self.tree.xview
        )
        self.tree.configure(xscrollcommand=hsb.set, yscrollcommand=vsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_group.grid_rowconfigure(0, weight=1)
        tree_group.grid_columnconfigure(0, weight=1)

        # Gombok
        btn_frame = tk.Frame(self.root, bg="#f0f0f0")
        btn_frame.pack(fill="x", padx=15, pady=5)

        btn_all = tk.Button(
            btn_frame,
            text=" Minden regisztrált exportálása",
            bg="#2e7d32",
            fg="white",
            font=("Arial", 11, "bold"),
            relief="flat",
            padx=10,
            pady=8,
            command=lambda: self.hzs_exportal("minden"),
        )
        btn_all.pack(side="left", fill="x", expand=True, padx=(0, 6))

        btn_de = tk.Button(
            btn_frame,
            text=" Délelőttiek exportálása",
            bg="#e67e00",
            fg="white",
            font=("Arial", 11, "bold"),
            relief="flat",
            padx=10,
            pady=8,
            command=lambda: self.hzs_exportal("10:00"),
        )
        btn_de.pack(side="left", fill="x", expand=True, padx=6)

        btn_du = tk.Button(
            btn_frame,
            text=" Délutániak exportálása",
            bg="#7b1fa2",
            fg="white",
            font=("Arial", 11, "bold"),
            relief="flat",
            padx=10,
            pady=8,
            command=lambda: self.hzs_exportal("14:00"),
        )
        btn_du.pack(side="left", fill="x", expand=True, padx=(6, 0))

        # Alsó sáv (Frissítés, Kilépés, Státusz)
        bottom_frame = tk.Frame(self.root, bg="#f0f0f0")
        bottom_frame.pack(fill="x", padx=15, pady=(5, 2))

        btn_refresh = tk.Button(
            bottom_frame,
            text=" Frissítés",
            bg="#0288d1",
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.hzs_frissites,
            padx=15,
            pady=4,
        )
        btn_refresh.pack(side="left")

        btn_exit = tk.Button(
            bottom_frame,
            text=" Kilépés",
            bg="#616161",
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.root.destroy,
            padx=15,
            pady=4,
        )
        btn_exit.pack(side="right")

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

    def hzs_frissites(self):
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()

            # Számlálók
            cursor.execute(
                "SELECT COUNT(*) FROM Regisztraciok WHERE regisztralt=1"
            )
            osszes_reg = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM Regisztraciok WHERE regisztralt=1 AND"
                " eloadas='10:00'"
            )
            de_reg = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM Regisztraciok WHERE regisztralt=1 AND"
                " eloadas='14:00'"
            )
            du_reg = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM Regisztraciok WHERE regisztralt=0 OR"
                " regisztralt IS NULL"
            )
            nem_reg = cursor.fetchone()[0]

            self.lbl_osszes.config(text=f" Összes regisztrált: {osszes_reg}")
            self.lbl_de.config(text=f" Délelőtt (10:00): {de_reg}")
            self.lbl_du.config(text=f" Délután (14:00): {du_reg}")
            self.lbl_nem_reg.config(text=f" Még nem regisztrált: {nem_reg}")

            # Első 15 regisztrált sor előnézete
            cursor.execute(
                """SELECT TOP 15 
                       teljesNev, szuletesiIdo, telepules, 
                       kozteruletNev, kozteruletJelleg, hazszam, 
                       email, telefonszam, regisztracioDatuma, 
                       regisztraloFelhasznalo, eloadas 
                   FROM Regisztraciok 
                   WHERE regisztralt=1 
                   ORDER BY regisztracioDatuma DESC"""
            )
            rows = cursor.fetchall()
            conn.close()

            for i in self.tree.get_children():
                self.tree.delete(i)

            for r in rows:
                cim = (
                    f"{r[3] or ''} {r[4] or ''} {r[5] or ''}"
                    if r[4]
                    else f"{r[3] or ''} {r[5] or ''}"
                )
                reg_d = r[8].strftime("%m-%d %H:%M") if r[8] else ""
                szul_d = str(r[1])[:10] if r[1] else ""

                self.tree.insert(
                    "",
                    tk.END,
                    values=(
                        r[0] or "",
                        szul_d,
                        r[2] or "",
                        cim.strip(),
                        r[6] or "",
                        r[7] or "",
                        reg_d,
                        r[9] or "",
                        r[10] or "",
                    ),
                )

            self.status_bar.config(text="Kész - Adatok betöltve")
        except Exception as e:
            self.status_bar.config(text=f"Hiba: {e}")
            messagebox.showerror(
                "Hiba", f"Nem sikerült betölteni az adatokat:\n{e}"
            )

    def hzs_exportal(self, szuro):
        now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        if szuro == "minden":
            default_filename = f"minden_regisztralt_{now_str}.xlsx"
            where_clause = "WHERE regisztralt=1"
        elif szuro == "10:00":
            default_filename = f"delelotti_regisztraltak_{now_str}.xlsx"
            where_clause = "WHERE regisztralt=1 AND eloadas='10:00'"
        else:
            default_filename = f"delutani_regisztraltak_{now_str}.xlsx"
            where_clause = "WHERE regisztralt=1 AND eloadas='14:00'"

        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel munkafüzet", "*.xlsx")],
            initialfile=default_filename,
            title="Excel mentése",
        )

        if not filepath:
            return

        try:
            self.status_bar.config(text="Exportálás folyamatban...")
            self.root.update_idletasks()

            conn = pyodbc.connect(self.conn_str)
            # A mellékelt Excel fájlok pontos oszlopelrendezése
            query = f"""
                SELECT 
                    id AS [ID],
                    teljesNev AS [Teljes név],
                    szuletesiIdo AS [Születési idő],
                    iranyitoszam AS [Irányítószám],
                    telepules AS [Település],
                    kozteruletNev AS [Közterület név],
                    kozteruletJelleg AS [Közterület jelleg],
                    hazszam AS [Házszám],
                    lepcsohaz AS [Lépcsőház],
                    szint AS [Szint],
                    ajto AS [Ajtó],
                    email AS [Email],
                    telefonszam AS [Telefonszám],
                    regisztracioDatuma AS [Regisztráció dátuma],
                    regisztraloFelhasznalo AS [Regisztráló felhasználó],
                    regisztracioTipusa AS [Regisztráció típusa],
                    eloadas AS [Előadás]
                FROM Regisztraciok 
                {where_clause}
                ORDER BY teljesNev ASC
            """
            df = pd.read_sql(query, conn)
            conn.close()

            # Excel kiírás a mintával megegyező 'Regisztráltak' munkalapnévvel
            with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name="Regisztráltak", index=False)

            self.status_bar.config(
                text=f"Sikeres exportálás: {os.path.basename(filepath)}"
            )
            messagebox.showinfo(
                "Siker",
                f"Sikeres exportálás!\nFájl: {filepath}\nÖsszesen:"
                f" {len(df)} rekord.",
            )
        except Exception as e:
            self.status_bar.config(text="Exportálási hiba történt")
            messagebox.showerror("Hiba", f"Hiba az exportálás során:\n{e}")


def main():
    root = tk.Tk()
    app = ExportAblak(root)
    root.mainloop()


if __name__ == "__main__":
    main()