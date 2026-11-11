import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox
from backend.books import add_book_det, delete_book_det, get_book_det, update_book_det
from backend.constants import GENRE_DETAILS
from ui.scanner import open_barcode_scanner

column_widths = {
    "ISBN": 130,
    "Title": 220,
    "Author": 160,
    "Publication": 150,
    "Genre": 120,
    "Language": 90,
    "Description": 320,
}

def open_add_book_popup(app, refresh_callback):
    popup = ttk.Toplevel(app)
    popup.title("Add New Book")
    popup.geometry("660x540")

    container = ttk.Frame(popup, padding=25)
    container.pack(fill="both", expand=True)

    ttk.Label(container, text="📚 Add New Book to Library", font=("Helvetica", 16, "bold"), bootstyle="info").pack(pady=(0, 15))

    form = ttk.Frame(container)
    form.pack(fill="x", expand=True)

    isbn_var = ttk.StringVar()
    title_var = ttk.StringVar()
    author_var = ttk.StringVar()
    pub_var = ttk.StringVar()
    genre_var = ttk.StringVar(value=sorted(list(GENRE_DETAILS))[0])
    lang_var = ttk.StringVar(value="English")
    desc_var = ttk.StringVar()

    isbn_row = ttk.Frame(form)
    isbn_row.pack(fill="x", pady=4)
    ttk.Label(isbn_row, text="ISBN (10 or 13 digits)", font=("Helvetica", 9, "bold"), width=22).pack(side="left")
    ttk.Entry(isbn_row, textvariable=isbn_var, font=("Helvetica", 10)).pack(side="left", fill="x", expand=True, padx=(0, 5))
    ttk.Button(isbn_row, text="📷 Scan Barcode", command=lambda: open_barcode_scanner(popup, lambda code: isbn_var.set(code), "Scan Book ISBN"), bootstyle="info-outline").pack(side="right")

    fields = [
        ("Book Title", title_var),
        ("Author", author_var),
        ("Publisher", pub_var),
        ("Language", lang_var),
    ]

    for label, var in fields:
        row = ttk.Frame(form)
        row.pack(fill="x", pady=4)
        ttk.Label(row, text=label, font=("Helvetica", 9, "bold"), width=22).pack(side="left")
        ttk.Entry(row, textvariable=var, font=("Helvetica", 10)).pack(side="left", fill="x", expand=True)

    genre_row = ttk.Frame(form)
    genre_row.pack(fill="x", pady=4)
    ttk.Label(genre_row, text="Genre", font=("Helvetica", 9, "bold"), width=22).pack(side="left")
    ttk.Combobox(genre_row, textvariable=genre_var, values=sorted(list(GENRE_DETAILS)), state="readonly").pack(side="left", fill="x", expand=True)

    desc_row = ttk.Frame(form)
    desc_row.pack(fill="x", pady=4)
    ttk.Label(desc_row, text="Description", font=("Helvetica", 9, "bold"), width=22).pack(side="left")
    ttk.Entry(desc_row, textvariable=desc_var, font=("Helvetica", 10)).pack(side="left", fill="x", expand=True)

    def add():
        isbn = isbn_var.get().strip()
        title = title_var.get().strip()
        author = author_var.get().strip()
        publication = pub_var.get().strip()
        genre = genre_var.get().strip()
        language = lang_var.get().strip()
        description = desc_var.get().strip()

        if not all([isbn, title, author, publication, genre, language]):
            messagebox.showerror("Error", "All fields except description are required.")
            return

        result = add_book_det(isbn, title, author, publication, genre, language, description)
        if "successfully" in result.lower():
            messagebox.showinfo("Success", result)
            popup.destroy()
            refresh_callback()
        else:
            messagebox.showerror("Error", result)

    btn_row = ttk.Frame(container)
    btn_row.pack(fill="x", pady=(20, 0))
    ttk.Button(btn_row, text="Add Book", command=add, bootstyle="primary").pack(side="left", padx=5, expand=True, fill="x")
    ttk.Button(btn_row, text="Cancel", command=popup.destroy, bootstyle="secondary-outline").pack(side="left", padx=5)

def open_update_book_popup(app, isbn, refresh_callback):
    if not isbn:
        return

    book_rows = get_book_det(str(isbn))
    if not book_rows:
        messagebox.showerror("Error", "Book not found in database.")
        return
    book_data = book_rows[0]

    popup = ttk.Toplevel(app)
    popup.title(f"Update Book - {isbn}")
    popup.geometry("620x520")

    container = ttk.Frame(popup, padding=25)
    container.pack(fill="both", expand=True)

    ttk.Label(container, text=f"✏️ Update Book (ISBN: {isbn})", font=("Helvetica", 16, "bold"), bootstyle="info").pack(pady=(0, 15))

    form = ttk.Frame(container)
    form.pack(fill="x", expand=True)

    title_var = ttk.StringVar(value=book_data[2] or "")
    desc_var = ttk.StringVar(value=book_data[3] or "")
    author_var = ttk.StringVar(value=book_data[4] or "")
    pub_var = ttk.StringVar(value=book_data[5] or "")
    genre_var = ttk.StringVar(value=book_data[6] or "")
    lang_var = ttk.StringVar(value=book_data[7] or "English")

    fields = [
        ("Book Title", title_var),
        ("Author", author_var),
        ("Publisher", pub_var),
        ("Language", lang_var),
    ]

    for label, var in fields:
        row = ttk.Frame(form)
        row.pack(fill="x", pady=4)
        ttk.Label(row, text=label, font=("Helvetica", 9, "bold"), width=22).pack(side="left")
        ttk.Entry(row, textvariable=var, font=("Helvetica", 10)).pack(side="left", fill="x", expand=True)

    genre_row = ttk.Frame(form)
    genre_row.pack(fill="x", pady=4)
    ttk.Label(genre_row, text="Genre", font=("Helvetica", 9, "bold"), width=22).pack(side="left")
    ttk.Combobox(genre_row, textvariable=genre_var, values=sorted(list(GENRE_DETAILS)), state="readonly").pack(side="left", fill="x", expand=True)

    desc_row = ttk.Frame(form)
    desc_row.pack(fill="x", pady=4)
    ttk.Label(desc_row, text="Description", font=("Helvetica", 9, "bold"), width=22).pack(side="left")
    ttk.Entry(desc_row, textvariable=desc_var, font=("Helvetica", 10)).pack(side="left", fill="x", expand=True)

    def update():
        title = title_var.get().strip()
        desc = desc_var.get().strip()
        author = author_var.get().strip()
        pub = pub_var.get().strip()
        genre = genre_var.get().strip()
        lang = lang_var.get().strip()

        result = update_book_det(isbn, title=title, description=desc, author=author, publication=pub, genre=genre, language=lang)
        if "success" in result.lower():
            messagebox.showinfo("Success", result)
            popup.destroy()
            refresh_callback()
        else:
            messagebox.showerror("Error", result)

    btn_row = ttk.Frame(container)
    btn_row.pack(fill="x", pady=(20, 0))
    ttk.Button(btn_row, text="Save Changes", command=update, bootstyle="success").pack(side="left", padx=5, expand=True, fill="x")
    ttk.Button(btn_row, text="Cancel", command=popup.destroy, bootstyle="secondary-outline").pack(side="left", padx=5)

def open_delete_book_popup(app, isbn, refresh_callback):
    if not isbn:
        return
    confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete book with ISBN {isbn}?\nThis will also remove all associated inventory items.")
    if confirm:
        result = delete_book_det(isbn)
        if "success" in result.lower():
            messagebox.showinfo("Success", result)
            refresh_callback()
        else:
            messagebox.showerror("Error", result)

def books_manage(app):
    container = ttk.Frame(app, padding=15)
    container.pack(fill="both", expand=True)

    top_bar = ttk.Frame(container)
    top_bar.pack(fill="x", pady=(0, 10))

    ttk.Label(top_bar, text="📚 Library Books Catalog", font=("Helvetica", 18, "bold"), bootstyle="info").pack(side="left")

    search_frame = ttk.Frame(top_bar)
    search_frame.pack(side="right")

    search_var = ttk.StringVar()
    search_entry = ttk.Entry(search_frame, textvariable=search_var, font=("Helvetica", 10), width=22)
    search_entry.pack(side="left", padx=(0, 5))

    tree_frame = ttk.Frame(container)
    tree_frame.pack(fill="both", expand=True)

    columns = ("ISBN", "Title", "Author", "Publication", "Genre", "Language", "Description")
    table = ttk.Treeview(tree_frame, columns=columns, show="headings", bootstyle="secondary")

    for col in columns:
        table.heading(col, text=col)
        table.column(col, width=column_widths[col], anchor="center" if col in ("ISBN", "Genre", "Language") else "w")

    v_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=table.yview, bootstyle="round")
    h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=table.xview, bootstyle="round")
    table.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

    table.pack(side="left", fill="both", expand=True)
    v_scroll.pack(side="right", fill="y")
    h_scroll.pack(side="bottom", fill="x")

    def refresh_table(query=None):
        table.delete(*table.get_children())
        books = get_book_det()
        if not books:
            return

        q = query.lower().strip() if query else ""
        for row in books:
            isbn = str(row[1])
            title = str(row[2])
            desc = str(row[3] or "")
            author = str(row[4])
            pub = str(row[5])
            genre = str(row[6])
            lang = str(row[7])

            if q:
                match = (q in isbn.lower() or q in title.lower() or q in author.lower() or q in genre.lower() or q in pub.lower())
                if not match:
                    continue

            table.insert("", "end", values=(isbn, title, author, pub, genre, lang, desc))

    def on_search(event=None):
        refresh_table(search_var.get())

    def on_scan():
        open_barcode_scanner(app, lambda code: [search_var.set(code), refresh_table(code)], "Scan Barcode to Search")

    search_entry.bind("<KeyRelease>", on_search)
    ttk.Button(search_frame, text="🔍 Search", command=on_search, bootstyle="secondary-outline").pack(side="left", padx=2)
    ttk.Button(search_frame, text="📷 Scan Barcode", command=on_scan, bootstyle="info-outline").pack(side="left", padx=2)

    def get_selected_isbn():
        selected = table.selection()
        if not selected:
            messagebox.showerror("Selection Required", "Please click on a book in the table first.")
            return None
        isbn_val = str(table.item(selected[0])["values"][0]).strip()
        if len(isbn_val) == 9 and isbn_val.isdigit():
            isbn_val = isbn_val.zfill(10)
        elif len(isbn_val) == 12 and isbn_val.isdigit():
            isbn_val = isbn_val.zfill(13)
        return isbn_val

    button_frame = ttk.Frame(container)
    button_frame.pack(fill="x", pady=(10, 0))

    ttk.Button(button_frame, text="➕ Add Book", command=lambda: open_add_book_popup(app, refresh_table), bootstyle="primary").pack(side="left", padx=5)
    ttk.Button(button_frame, text="✏️ Update Book", command=lambda: open_update_book_popup(app, get_selected_isbn(), refresh_table), bootstyle="info").pack(side="left", padx=5)
    ttk.Button(button_frame, text="🗑️ Delete Book", command=lambda: open_delete_book_popup(app, get_selected_isbn(), refresh_table), bootstyle="danger-outline").pack(side="left", padx=5)
    ttk.Button(button_frame, text="🔄 Refresh", command=lambda: [search_var.set(""), refresh_table()], bootstyle="secondary-outline").pack(side="right", padx=5)

    refresh_table()
