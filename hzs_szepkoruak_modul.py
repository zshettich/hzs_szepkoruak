import tkinter as tk
from tkinter import messagebox, ttk
import pyodbc
import re
from datetime import datetime
import getpass


class HZSSzepkoruakOsztaly:
    def __init__(self, root):
        self.root = root
        self.conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=172.16.11.60;"
            "DATABASE=szepkor2025t;"
            "UID=szepkor;"
            "PWD=Szep0625kor?;"
        )
        self.db_name = self.hzs_extract_db_name()
        self.szepkoruak = []
        self.all_values = []
        self.label_widgets = {}
        self.rb_var = tk.StringVar(value="10:00")

        self.hzs_setup_window()
        self.hzs_create_widgets()
        self.hzs_load_data()
        self.hzs_update_counts()

    def hzs_extract_db_name(self):
        db_name_match = re.search(r"DATABASE=([^;]+);", self.conn_str, re.IGNORECASE)
        return db_name_match.group(1) if db_name_match else "Ismeretlen"

    def hzs_setup_window(self):
        self.root.title("Szépkorúak regisztrációja előadásra - 2025")
        self.root.update_idletasks()
        self.root.minsize(600, self.root.winfo_height())
        self.root.configure(bg="#f0f0f0")

    def hzs_create_widgets(self):
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.hzs_create_header(main_frame)

        left_frame = tk.Frame(main_frame, bg="#f0f0f0")
        left_frame.grid(row=2, column=0, sticky="n", padx=5)

        right_frame = tk.Frame(main_frame, bg="#f0f0f0")
        right_frame.grid(row=2, column=1, sticky="n", padx=5)

        details_frame = tk.Frame(right_frame, bg="#f0f0f0", borderwidth=1, relief="solid")
        details_frame.pack(padx=5, pady=5)

        reg_details_frame = tk.Frame(right_frame, bg="#f0f0f0", borderwidth=1, relief="solid")
        reg_details_frame.pack(pady=5)

        self.hzs_create_search_section(left_frame)
        self.hzs_create_treeview(left_frame)
        self.hzs_create_status_section(left_frame)
        self.hzs_create_time_selection(left_frame)
        self.hzs_create_register_button(left_frame)
        self.hzs_create_details_and_reg_sections(details_frame, reg_details_frame)
        self.hzs_create_count_labels(right_frame)

        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

        self.hzs_bind_events()

    def hzs_create_header(self, parent_frame):
        tk.Label(
            parent_frame,
            text="SZÉPKORÚAK REGISZTRÁCIÓJA ELŐADÁSRA - 2025",
            fg="red",
            font=("Arial", 14, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=(0, 5))

        tk.Label(
            parent_frame,
            text=f"Használt adatbázis: {self.db_name}",
            fg="blue",
            font=("Arial", 14, "bold")
        ).grid(row=1, column=0, columnspan=2, pady=(0, 10))

    def hzs_create_search_section(self, parent_frame):
        search_frame = tk.Frame(parent_frame, bg="#f0f0f0")
        search_frame.pack(pady=5, anchor="w")

        tk.Label(search_frame, text="Keresés:", font=("Arial", 14, "bold")).pack(pady=5, anchor="w")

        self.entry_search = tk.Entry(
            search_frame,
            width=60,
            font=("Arial", 12)
        )
        self.entry_search.pack(pady=10)
        self.entry_search.focus_set()

    def hzs_create_treeview(self, parent_frame):
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 12))
        style.configure("Treeview.Heading", font=("Arial", 14, "bold"))

        self.tree = ttk.Treeview(
            parent_frame,
            columns=("name", "id"),
            show="",
            height=10,
        )
        self.tree.heading("name", text="Név és cím")
        self.tree.heading("id", text="ID")

        self.tree.column("name", width=60)
        self.tree.column("id", width=0, stretch=False)

        self.tree.pack(pady=5, fill=tk.BOTH, expand=True)

    def hzs_create_details_and_reg_sections(self, details_frame, reg_details_frame):
        first_group_fields = [
            "Név", "Születési dátum", "Irányítószám", "Település",
            "Közterület név", "Közterület jelleg", "Házszám", "Lépcsőház",
            "Emelet", "Ajtó", "Email", "Telefon"
        ]
        second_group_fields = [
            "Regisztráció dátuma", "Regisztráló felhasználó", "Regisztrált előadás"
        ]

        for field in first_group_fields + second_group_fields:
            frame = tk.Frame(details_frame if field in first_group_fields else reg_details_frame,
                             bg="#f0f0f0")
            frame.pack(anchor="w")

            lbl_name = tk.Label(
                frame,
                text=field + ": ",
                width=20,
                anchor="w",
                font=("Arial", 12)
            )
            lbl_name.pack(side="left")

            lbl_value = tk.Label(
                frame,
                text="",
                width=30,
                anchor="w",
                font=("Arial", 12)
            )
            lbl_value.pack(side="left")

            self.label_widgets[field] = lbl_value

    def hzs_create_status_section(self, parent_frame):
        self.status_label = tk.Label(
            parent_frame,
            text="",
            font=("Arial", 12)
        )
        self.status_label.pack(pady=5)

    def hzs_create_time_selection(self, parent_frame):
        rb_frame = tk.Frame(parent_frame, bg="#f0f0f0")
        rb_frame.pack(pady=5, anchor="w")

        tk.Label(rb_frame, text="Választott előadás:", font=("Arial", 14, "bold")).pack(anchor="w", pady=5)

        rb_morning = tk.Radiobutton(
            rb_frame, text="Délelőtt 10:00",
            font=("Arial", 14, "bold"),
            variable=self.rb_var,
            value="10:00"
        )
        rb_morning.pack(side="left", padx=5)

        rb_afternoon = tk.Radiobutton(
            rb_frame, text="Délután 14:00",
            font=("Arial", 14, "bold"),
            variable=self.rb_var,
            value="14:00"
        )
        rb_afternoon.pack(side="left", padx=5)

    def hzs_create_count_labels(self, parent_frame):
        count_frame = tk.Frame(parent_frame, bg="#f0f0f0")
        count_frame.pack(pady=5, anchor="w")

        tk.Label(count_frame, text="Regisztráltak:", font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 5))

        self.de_registered_count_label = tk.Label(count_frame, text="", font=("Arial", 14, "bold"), fg="blue")
        self.de_registered_count_label.pack(anchor="w")

        self.du_registered_count_label = tk.Label(count_frame, text="", font=("Arial", 14, "bold"), fg="blue")
        self.du_registered_count_label.pack(anchor="w")

        self.registered_count_label = tk.Label(count_frame, text="", font=("Arial", 14, "bold"), fg="blue")
        self.registered_count_label.pack(anchor="w")

    def hzs_create_register_button(self, parent_frame):
        self.btn_reg = tk.Button(
            parent_frame,
            text="Regisztráció",
            command=self.hzs_on_registration,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 14, "bold"),
            width=15,
            height=2
        )
        self.btn_reg.pack(pady=10)

    def hzs_bind_events(self):
        self.entry_search.bind("<KeyRelease>", self.hzs_update_listbox)
        self.tree.bind("<<TreeviewSelect>>", self.hzs_on_select)
        self.entry_search.bind("<Return>", lambda e: self.hzs_select_first_item())

    def hzs_select_first_item(self):
        items = self.tree.get_children()
        if items:
            self.tree.selection_set(items[0])
            self.hzs_on_select()

    def hzs_load_data(self):
        try:
            self.szepkoruak = self.hzs_get_szepkoruak()
            self.all_values = [f"{r.teljesNev} - {r.kozteruletNev} {r.hazszam}" for r in self.szepkoruak]
            for i in self.tree.get_children():
                self.tree.delete(i)
            for r in self.szepkoruak:
                display_text = f"{r.teljesNev} - {r.kozteruletNev} {r.hazszam}"
                self.tree.insert("", tk.END, values=(display_text, r.id))
        except Exception as e:
            messagebox.showerror("Hiba", f"Adatok betöltése sikertelen: {str(e)}")

    def hzs_update_listbox(self, event=None):
        typed = self.entry_search.get().lower()
        for i in self.tree.get_children():
            self.tree.delete(i)
        for r in self.szepkoruak:
            item_text = f"{r.teljesNev} - {r.kozteruletNev} {r.hazszam} {r.id}"
            display_text = f"{r.teljesNev} - {r.kozteruletNev} {r.hazszam}"
            if item_text.lower().startswith(typed):
                self.tree.insert("", tk.END, values=(display_text, r.id))

    def hzs_on_select(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return
        selected_item = self.tree.item(selected[0])["values"]
        selected_text, selected_id = selected_item[0], selected_item[1]

        self.entry_search.delete(0, tk.END)
        self.entry_search.insert(0, selected_text)

        try:
            row = self.hzs_get_szepkoru_details(selected_id)
            if row:
                self.hzs_display_details(row, row.regisztralt)
        except Exception as e:
            messagebox.showerror("Hiba", str(e))

    def hzs_display_details(self, row, reg_status):
        self.label_widgets["Név"].config(text=row.teljesNev)
        szul_date = row.szuletesiIdo
        if szul_date:
            szul_date_str = szul_date.strftime("%Y-%m-%d")
            birth_year = int(szul_date_str[:4])
            age = 2025 - birth_year
            if (szul_date.month, szul_date.day) > (12, 31):
                age -= 1
            self.label_widgets["Születési dátum"].config(text=f"{szul_date_str} ({age} éves)")
        else:
            self.label_widgets["Születési dátum"].config(text="")

        self.label_widgets["Irányítószám"].config(text=row.iranyitoszam)
        self.label_widgets["Település"].config(text=row.telepules)
        self.label_widgets["Közterület név"].config(text=row.kozteruletNev)
        self.label_widgets["Közterület jelleg"].config(text=row.kozteruletJelleg)
        self.label_widgets["Házszám"].config(text=row.hazszam)
        self.label_widgets["Lépcsőház"].config(text=row.lepcsohaz)
        self.label_widgets["Emelet"].config(text=row.szint)
        self.label_widgets["Ajtó"].config(text=row.ajto)
        self.label_widgets["Email"].config(text=row.email if hasattr(row, "email") else "")
        self.label_widgets["Telefon"].config(text=row.telefonszam if hasattr(row, "telefonszam") else "")
        self.label_widgets["Regisztráció dátuma"].config(
            text=row.regisztracioDatuma.strftime("%Y-%m-%d %H:%M:%S") if row.regisztracioDatuma else ""
        )
        self.label_widgets["Regisztráló felhasználó"].config(
            text=row.regisztraloFelhasznalo if row.regisztraloFelhasznalo else ""
        )
        self.label_widgets["Regisztrált előadás"].config(
            text=row.eloadas if hasattr(row, "eloadas") and row.eloadas else ""
        )

        if reg_status:
            self.status_label.config(text="Már regisztrált!", fg="red", font=("Arial", 14, "bold"))
        else:
            self.status_label.config(text="Nem regisztrált", fg="green", font=("Arial", 14, "bold"))

    def hzs_on_registration(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Hiba", "Válassz egy személyt!")
            return
        selected_item = self.tree.item(selected[0])["values"]
        selected_text, selected_id = selected_item[0], selected_item[1]
        eloadas_val = self.rb_var.get()
        try:
            self.hzs_register_person(selected_id, "Telefon", eloadas_val, None, None)
            messagebox.showinfo("Siker", f"Regisztráció sikeres!\n{selected_text}")
            self.hzs_reset_to_initial_state()
        except Exception as e:
            messagebox.showerror("Hiba", str(e))

    def hzs_reset_to_initial_state(self):
        self.hzs_load_data()
        self.entry_search.delete(0, tk.END)
        self.entry_search.focus_set()
        self.tree.selection_remove(self.tree.selection())
        for field in self.label_widgets:
            self.label_widgets[field].config(text="")
        self.status_label.config(text="")
        self.hzs_update_counts()

    def hzs_update_counts(self):
        try:
            total_count = self.hzs_get_registered_count()
            self.registered_count_label.config(
                text=f"Összesen: {total_count} / 1100 (maradt {1100 - total_count} hely)")
            morning_count, afternoon_count = self.hzs_get_registered_count_by_time()
            self.de_registered_count_label.config(
                text=f"Délelőttre: {morning_count} / 550 (maradt {550 - morning_count} hely)")
            self.du_registered_count_label.config(
                text=f"Délutánra: {afternoon_count} / 550 (maradt {550 - afternoon_count} hely)")
        except Exception as e:
            messagebox.showerror("Hiba", f"Számok frissítése sikertelen: {str(e)}")

    def hzs_get_szepkoruak(self):
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Regisztraciok ORDER BY teljesNev ASC")
            rows = cursor.fetchall()
            conn.close()
            return rows
        except Exception as e:
            raise Exception(f"Hiba az adatok lekérdezésekor: {str(e)}")

    def hzs_get_szepkoru_details(self, szepkoru_id):
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Regisztraciok WHERE id=?", (szepkoru_id,))
            row = cursor.fetchone()
            conn.close()
            return row
        except Exception as e:
            raise Exception(f"Hiba a részletek lekérdezésekor: {str(e)}")

    def hzs_register_person(self, selected_id, tipus, eloadas, email, telefon):
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()
            felhasznalo = getpass.getuser()

            if tipus == "E-mail" and email:
                sql = """UPDATE Regisztraciok
                         SET regisztralt=1,
                             regisztracioDatuma=?,
                             regisztraloFelhasznalo=?,
                             regisztracioTipusa=?,
                             eloadas=?,
                             email=?
                         WHERE id = ?"""
                params = (datetime.now(), felhasznalo, tipus, eloadas, email, selected_id)
            else:
                sql = """UPDATE Regisztraciok
                         SET regisztralt=1,
                             regisztracioDatuma=?,
                             regisztraloFelhasznalo=?,
                             regisztracioTipusa=?,
                             eloadas=?,
                             telefonszam=?
                         WHERE id = ?"""
                params = (datetime.now(), felhasznalo, tipus, eloadas, telefon, selected_id)

            cursor.execute(sql, params)
            conn.commit()
            conn.close()
        except Exception as e:
            raise Exception(f"Hiba a regisztráció során: {str(e)}")

    def hzs_get_registered_count(self):
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Regisztraciok WHERE regisztralt=1")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            raise Exception(f"Hiba a regisztráltak számának lekérdezésekor: {str(e)}")

    def hzs_get_registered_count_by_time(self):
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM Regisztraciok WHERE regisztralt = 1 AND eloadas = '10:00'")
            count_morning = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM Regisztraciok WHERE regisztralt = 1 AND eloadas = '14:00'")
            count_afternoon = cursor.fetchone()[0]

            conn.close()
            return count_morning, count_afternoon
        except Exception as e:
            raise Exception(f"Hiba az időszakok szerinti számok lekérdezésekor: {str(e)}")