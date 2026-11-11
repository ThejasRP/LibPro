import os
import sys
from tkinter import messagebox
import ttkbootstrap as ttk
from PIL import Image, ImageTk
from ui.login import login_screen
from ui.common import get_asset_path
from backend.sql import closeCon

def on_close():
    if messagebox.askyesno("Exit LibPro", "Are you sure you want to exit the application?"):
        try:
            closeCon()
        except Exception:
            pass
        app.destroy()
        sys.exit(0)

app = ttk.Window(themename="darkly")
app.geometry("1200x800")
app.minsize(950, 650)
try:
    app.state('zoomed')
except Exception:
    pass
app.title("LibPro | Library Management System")

# Set application window icon
icon_path = get_asset_path("ui", "images", "logo.png")
if os.path.exists(icon_path):
    try:
        icon_img = ImageTk.PhotoImage(Image.open(icon_path))
        app.iconphoto(False, icon_img)
    except Exception:
        pass

app.protocol("WM_DELETE_WINDOW", on_close)

login_screen(app)
app.mainloop()
