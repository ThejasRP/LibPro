import os
import sys
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

def get_asset_path(*paths):
    """Resolve asset paths reliably across development and PyInstaller bundles."""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base = sys._MEIPASS
    else:
        # Root directory of LibPro project
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(base, *paths)
    if os.path.exists(full_path):
        return full_path
    # Fallback to path relative to ui folder
    ui_relative = os.path.join(os.path.dirname(os.path.abspath(__file__)), *paths)
    if os.path.exists(ui_relative):
        return ui_relative
    return full_path

def create_card(parent, title, value):
    frame = ttk.Frame(parent, padding=15, bootstyle="secondary")
    frame.pack(side=LEFT, expand=True, fill=BOTH, padx=8, pady=5)
    ttk.Label(frame, text=str(value), font=("Helvetica", 22, "bold"), bootstyle="inverse-secondary").pack(anchor="center")
    ttk.Label(frame, text=title, font=("Helvetica", 11), bootstyle="inverse-secondary").pack(anchor="center", pady=(5, 0))
    return frame

def _bind_mousewheel(widget, canvas):
    def on_mousewheel(event):
        try:
            if canvas.winfo_exists():
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            pass

    def bind_tree(w):
        w.bind("<MouseWheel>", on_mousewheel, add="+")
        for child in w.winfo_children():
            bind_tree(child)

    widget.bind("<MouseWheel>", on_mousewheel, add="+")
    canvas.bind("<MouseWheel>", on_mousewheel, add="+")
    widget.bind("<Configure>", lambda e: bind_tree(widget), add="+")

def make_scrollable_frame(parent):
    container = ttk.Frame(parent)
    container.pack(fill="both", expand=True)

    canvas = ttk.Canvas(container, highlightthickness=0)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview, bootstyle="round")
    scrollable = ttk.Frame(canvas)

    window_id = canvas.create_window((0, 0), window=scrollable, anchor="nw")

    def on_canvas_configure(event):
        canvas.itemconfig(window_id, width=event.width)

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    canvas.bind("<Configure>", on_canvas_configure)
    scrollable.bind("<Configure>", on_frame_configure)
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    _bind_mousewheel(scrollable, canvas)

    return scrollable

def make_book_card(parent, book, on_click, status=None):
    isbn = str(book[1]) if len(book) > 1 else ""
    title_text = str(book[2]) if len(book) > 2 else "Untitled"
    desc_text = str(book[3]) if len(book) > 3 and book[3] else "No description available."
    if len(desc_text) > 85:
        desc_text = desc_text[:82] + "..."
    author_text = str(book[4]) if len(book) > 4 else "Unknown"
    genre_text = str(book[6]) if len(book) > 6 else ""

    card = ttk.Frame(parent, padding=12, bootstyle="secondary", cursor="hand2")

    top_row = ttk.Frame(card)
    top_row.pack(fill="x", side="top", pady=(0, 5))

    if genre_text:
        badge = ttk.Label(top_row, text=f" {genre_text} ", font=("Helvetica", 8, "bold"), bootstyle="info-inverse")
        badge.pack(side="left")

    if status:
        stat_style = "success-inverse" if status in ("Shelved", "Returned") else "warning-inverse" if status == "Borrowed" else "danger-inverse"
        stat_badge = ttk.Label(top_row, text=f" {status} ", font=("Helvetica", 8, "bold"), bootstyle=stat_style)
        stat_badge.pack(side="right")

    title_lbl = ttk.Label(
        card,
        text=title_text,
        font=("Helvetica", 12, "bold"),
        bootstyle="inverse-secondary",
        wraplength=220,
        justify="left",
        cursor="hand2"
    )
    title_lbl.pack(fill="x", pady=(2, 4), anchor="w")

    author_lbl = ttk.Label(
        card,
        text=f"by {author_text}",
        font=("Helvetica", 9, "italic"),
        bootstyle="inverse-secondary",
        wraplength=220,
        justify="left",
        cursor="hand2"
    )
    author_lbl.pack(fill="x", pady=(0, 6), anchor="w")

    desc_lbl = ttk.Label(
        card,
        text=desc_text,
        font=("Helvetica", 9),
        bootstyle="inverse-secondary",
        wraplength=220,
        justify="left",
        cursor="hand2"
    )
    desc_lbl.pack(fill="both", expand=True, pady=(0, 6), anchor="w")

    isbn_lbl = ttk.Label(
        card,
        text=f"ISBN: {isbn}",
        font=("Helvetica", 8),
        bootstyle="secondary-inverse",
        cursor="hand2"
    )
    isbn_lbl.pack(fill="x", side="bottom", anchor="w")

    def handle_click(e=None):
        try:
            on_click(isbn)
        except TypeError:
            try:
                on_click()
            except TypeError:
                on_click(e, isbn)

    def bind_click_recursive(w):
        w.bind("<Button-1>", handle_click)
        for child in w.winfo_children():
            bind_click_recursive(child)

    bind_click_recursive(card)

    return card
