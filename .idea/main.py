import tkinter as tk
from tkinter import messagebox
import sys
from hzs_szepkoruak_modul import HZSSzepkoruakOsztaly

def main():
    try:
        root = tk.Tk()
        app = HZSSzepkoruakOsztaly(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Kritikus hiba", f"Alkalmazás indítása sikertelen:\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()