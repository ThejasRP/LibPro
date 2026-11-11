import tkinter as tk
import ttkbootstrap as ttk
from tkinter import StringVar, messagebox
from backend.inventory import add_book_inv, get_book_inv, update_book_inv
from ui.scanner import open_barcode_scanner

def show_category(app, category):
    if category not in ["Unshelved", "Lost", "Missing", "Damaged", "Borrowed", "Shelved"]:
        messagebox.showerror("Error", "Invalid category chosen.")
        return

    books = get_book_inv(status=category)
    if not isinstance(books, list):
        books = []

    popup = ttk.Toplevel(app)
    popup.title(f"{category} Books ({len(books)})")
    popup.geometry("680x420")

    container = ttk.Frame(popup, padding=20)
    container.pack(fill="both", expand=True)

    ttk.Label(container, text=f"📦 {category} Inventory Items ({len(books)})", font=("Helvetica", 16, "bold"), bootstyle="info").pack(pady=(0, 15))

    tree_frame = ttk.Frame(container)
    tree_frame.pack(fill="both", expand=True)

    cols = ("SKU", "ISBN", "Status", "Bay", "Shelf", "Row", "Column", "Added On")
    tree = ttk.Treeview(tree_frame, columns=cols, show="headings", bootstyle="secondary")

    widths = {"SKU": 100, "ISBN": 130, "Status": 90, "Bay": 50, "Shelf": 50, "Row": 50, "Column": 50, "Added On": 120}
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=widths.get(col, 80), anchor="center")

    v_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview, bootstyle="round")
    tree.configure(yscrollcommand=v_scroll.set)

    tree.pack(side="left", fill="both", expand=True)
    v_scroll.pack(side="right", fill="y")

    if books:
        for b in books:
            tree.insert("", "end", values=(b[0], b[1], b[2], b[3], b[4], b[5], b[6], str(b[7])[:19] if b[7] else ""))
    else:
        tree.insert("", "end", values=("-", "-", f"No {category.lower()} books found", "-", "-", "-", "-", "-"))

    ttk.Button(container, text="Close", command=popup.destroy, bootstyle="secondary-outline").pack(pady=(15, 0))

def open_shelve_popup(app, update_view):
    popup = ttk.Toplevel(app)
    popup.title("Add New Book to Inventory & Shelve")
    popup.geometry("560x480")

    container = ttk.Frame(popup, padding=25)
    container.pack(fill="both", expand=True)

    ttk.Label(container, text="🗄️ Shelve New Inventory Item", font=("Helvetica", 16, "bold"), bootstyle="info").pack(pady=(0, 15))

    sku_var = StringVar()
    isbn_var = StringVar()
    bay_var = StringVar(value="1")
    shelf_var = StringVar(value="1")
    row_var = StringVar(value="1")
    col_var = StringVar(value="1")

    r_sku = ttk.Frame(container)
    r_sku.pack(fill="x", pady=4)
    ttk.Label(r_sku, text="SKU Number", font=("Helvetica", 9, "bold"), width=18).pack(side="left")
    ttk.Entry(r_sku, textvariable=sku_var, font=("Helvetica", 10)).pack(side="left", fill="x", expand=True, padx=(0, 5))
    ttk.Button(r_sku, text="📷 Scan SKU", command=lambda: open_barcode_scanner(popup, lambda code: sku_var.set(code), "Scan Item SKU"), bootstyle="info-outline").pack(side="right")

    r_isbn = ttk.Frame(container)
    r_isbn.pack(fill="x", pady=4)
    ttk.Label(r_isbn, text="ISBN", font=("Helvetica", 9, "bold"), width=18).pack(side="left")
    ttk.Entry(r_isbn, textvariable=isbn_var, font=("Helvetica", 10)).pack(side="left", fill="x", expand=True, padx=(0, 5))
    ttk.Button(r_isbn, text="📷 Scan ISBN", command=lambda: open_barcode_scanner(popup, lambda code: isbn_var.set(code), "Scan Book ISBN"), bootstyle="info-outline").pack(side="right")

    fields = [
        ("Bay Number", bay_var),
        ("Shelf Number", shelf_var),
        ("Row Number", row_var),
        ("Column Number", col_var)
    ]

    for label, var in fields:
        r = ttk.Frame(container)
        r.pack(fill="x", pady=4)
        ttk.Label(r, text=label, font=("Helvetica", 9, "bold"), width=18).pack(side="left")
        ttk.Entry(r, textvariable=var, font=("Helvetica", 10)).pack(side="left", fill="x", expand=True)

    def submit():
        sku = sku_var.get().strip()
        isbn = isbn_var.get().strip()
        if not sku or not isbn:
            messagebox.showerror("Error", "SKU and ISBN cannot be empty.")
            return

        try:
            bay = int(bay_var.get().strip() or 0)
            shelf = int(shelf_var.get().strip() or 0)
            row = int(row_var.get().strip() or 0)
            col = int(col_var.get().strip() or 0)
        except ValueError:
            messagebox.showerror("Error", "Bay, Shelf, Row, and Column must be integer numbers.")
            return

        res = add_book_inv(sku, isbn, "Shelved", bay, shelf, row, col)
        if "successfully" in res.lower():
            messagebox.showinfo("Success", res)
            popup.destroy()
            update_view()
        else:
            messagebox.showerror("Error", res)

    btn_row = ttk.Frame(container)
    btn_row.pack(fill="x", pady=(20, 0))
    ttk.Button(btn_row, text="Add to Shelf", command=submit, bootstyle="primary").pack(side="left", padx=5, expand=True, fill="x")
    ttk.Button(btn_row, text="Cancel", command=popup.destroy, bootstyle="secondary-outline").pack(side="left", padx=5)

def open_update_popup(app, update_view):
    popup = ttk.Toplevel(app)
    popup.title("Update Book Position / Status")
    popup.geometry("560x490")

    container = ttk.Frame(popup, padding=25)
    container.pack(fill="both", expand=True)

    ttk.Label(container, text="🔄 Update Book Position or Status", font=("Helvetica", 16, "bold"), bootstyle="info").pack(pady=(0, 15))

    sku_var = StringVar()
    status_var = StringVar(value="Shelved")
    bay_var = StringVar()
    shelf_var = StringVar()
    row_var = StringVar()
    col_var = StringVar()

    r1 = ttk.Frame(container)
    r1.pack(fill="x", pady=4)
    ttk.Label(r1, text="SKU Number", font=("Helvetica", 9, "bold"), width=18).pack(side="left")
    ttk.Entry(r1, textvariable=sku_var, font=("Helvetica", 10)).pack(side="left", fill="x", expand=True, padx=(0, 5))
    ttk.Button(r1, text="📷 Scan SKU", command=lambda: open_barcode_scanner(popup, lambda code: sku_var.set(code), "Scan Item SKU"), bootstyle="info-outline").pack(side="right")

    r2 = ttk.Frame(container)
    r2.pack(fill="x", pady=4)
    ttk.Label(r2, text="Status", font=("Helvetica", 9, "bold"), width=18).pack(side="left")
    ttk.Combobox(r2, textvariable=status_var, values=["Shelved", "Unshelved", "Missing", "Damaged", "Lost"], state="readonly").pack(side="left", fill="x", expand=True)

    for label, var in [("Bay Number", bay_var), ("Shelf Number", shelf_var), ("Row Number", row_var), ("Column Number", col_var)]:
        r = ttk.Frame(container)
        r.pack(fill="x", pady=4)
        ttk.Label(r, text=label, font=("Helvetica", 9, "bold"), width=18).pack(side="left")
        ttk.Entry(r, textvariable=var, font=("Helvetica", 10)).pack(side="left", fill="x", expand=True)

    def submit():
        sku = sku_var.get().strip()
        status = status_var.get().strip()
        if not sku:
            messagebox.showerror("Error", "SKU cannot be empty.")
            return

        erase = (status != "Shelved")
        bay = bay_var.get().strip()
        shelf = shelf_var.get().strip()
        row = row_var.get().strip()
        col = col_var.get().strip()

        try:
            b_val = int(bay) if (bay and not erase) else (0 if erase else None)
            s_val = int(shelf) if (shelf and not erase) else (0 if erase else None)
            r_val = int(row) if (row and not erase) else (0 if erase else None)
            c_val = int(col) if (col and not erase) else (0 if erase else None)
        except ValueError:
            messagebox.showerror("Error", "Bay, Shelf, Row, and Column must be integer numbers.")
            return

        res = update_book_inv(sku, status=status, bay=b_val, shelf=s_val, row=r_val, column=c_val, eraseBInfo=erase)
        if "successfully" in res.lower():
            messagebox.showinfo("Success", res)
            popup.destroy()
            update_view()
        else:
            messagebox.showerror("Error", res)

    btn_row = ttk.Frame(container)
    btn_row.pack(fill="x", pady=(20, 0))
    ttk.Button(btn_row, text="Update Record", command=submit, bootstyle="success").pack(side="left", padx=5, expand=True, fill="x")
    ttk.Button(btn_row, text="Cancel", command=popup.destroy, bootstyle="secondary-outline").pack(side="left", padx=5)

def bay_manager(app):
    container = ttk.Frame(app, padding=15)
    container.pack(fill="both", expand=True)

    top_bar = ttk.Frame(container)
    top_bar.pack(fill="x", pady=(0, 10))

    ttk.Label(top_bar, text="🗄️ Library Bay & Shelf Management", font=("Helvetica", 18, "bold"), bootstyle="info").pack(side="left")

    paned = ttk.PanedWindow(container, orient="horizontal")
    paned.pack(fill="both", expand=True)

    canvas_frame = ttk.Frame(paned)
    paned.add(canvas_frame, weight=4)

    outer_canvas = tk.Canvas(canvas_frame, highlightthickness=0, bg="#1e1e1e")
    outer_scroll_x = ttk.Scrollbar(canvas_frame, orient="horizontal", command=outer_canvas.xview, bootstyle="round")
    outer_canvas.configure(xscrollcommand=outer_scroll_x.set)

    outer_frame = ttk.Frame(outer_canvas)
    outer_win_id = outer_canvas.create_window((0, 0), window=outer_frame, anchor="nw")

    def on_outer_configure(event):
        outer_canvas.configure(scrollregion=outer_canvas.bbox("all"))

    outer_frame.bind("<Configure>", on_outer_configure)

    outer_canvas.pack(side="top", fill="both", expand=True)
    outer_scroll_x.pack(side="bottom", fill="x")

    right_panel = ttk.Frame(paned, padding=15, bootstyle="secondary")
    paned.add(right_panel, weight=1)

    ttk.Label(right_panel, text="Management Actions", font=("Helvetica", 12, "bold"), bootstyle="inverse-secondary").pack(anchor="w", pady=(0, 15))

    actions = [
        ("➕ Add Book to Bay", lambda: open_shelve_popup(app, update_shelf_view), "primary"),
        ("🔄 Update Book Location", lambda: open_update_popup(app, update_shelf_view), "info"),
        ("📦 View Unshelved Books", lambda: show_category(app, "Unshelved"), "secondary-outline"),
        ("❓ View Missing Books", lambda: show_category(app, "Missing"), "warning-outline"),
        ("❌ View Lost Books", lambda: show_category(app, "Lost"), "danger-outline"),
        ("⚠️ View Damaged Books", lambda: show_category(app, "Damaged"), "warning-outline"),
        ("📖 View Borrowed Books", lambda: show_category(app, "Borrowed"), "info-outline"),
    ]

    for text, cmd, style in actions:
        ttk.Button(right_panel, text=text, command=cmd, bootstyle=style).pack(fill="x", pady=5)

    def update_shelf_view():
        for widget in outer_frame.winfo_children():
            widget.destroy()

        books = get_book_inv(status="Shelved")
        if not isinstance(books, list) or not books:
            ttk.Label(outer_frame, text="No shelved books in inventory.\nUse 'Add Book to Bay' to place items onto shelves.", font=("Helvetica", 12), bootstyle="secondary").pack(padx=40, pady=40)
            return

        bay_map = {}
        for book in books:
            bay, shelf, row, col = book[3:7]
            if 0 in (bay, shelf, row, col):
                continue
            bay_map.setdefault(bay, []).append(book)

        if not bay_map:
            ttk.Label(outer_frame, text="All inventory items have 0 or unassigned bay numbers.\nUpdate book locations to see shelves here.", font=("Helvetica", 12), bootstyle="secondary").pack(padx=40, pady=40)
            return

        for bay_no in sorted(bay_map.keys()):
            bay_books = bay_map[bay_no]
            bay_card = ttk.Labelframe(outer_frame, text=f"🏛️ Bay {bay_no}", padding=12, bootstyle="info")
            bay_card.pack(side="left", padx=15, pady=10, fill="y")

            shelf_map = {}
            for book in bay_books:
                shelf_map.setdefault(book[4], []).append(book)

            for shelf_no in sorted(shelf_map.keys()):
                shelf_box = ttk.Labelframe(bay_card, text=f"Shelf {shelf_no}", padding=8, bootstyle="secondary")
                shelf_box.pack(fill="x", pady=6)

                grid_frame = ttk.Frame(shelf_box)
                grid_frame.pack(fill="both", expand=True)

                for book in shelf_map[shelf_no]:
                    r_num, c_num = book[5], book[6]
                    sku_num = book[0]
                    isbn_num = book[1]

                    slot_badge = ttk.Label(
                        grid_frame,
                        text=f"{sku_num}\n(R{r_num}:C{c_num})",
                        font=("Helvetica", 8, "bold"),
                        bootstyle="success-inverse",
                        padding=6,
                        justify="center"
                    )
                    slot_badge.pack(side="left", padx=3, pady=3)

    update_shelf_view()
