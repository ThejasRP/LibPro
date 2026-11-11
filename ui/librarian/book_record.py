import ttkbootstrap as ttk
from tkinter import StringVar, messagebox
from backend.account import get_user
from backend.bookrecord import borrow_book, get_record, return_book
from backend.inventory import get_book_inv
from ui.scanner import open_barcode_scanner

def open_borrow_book(app, refresh):
    popup = ttk.Toplevel(app)
    popup.geometry("560x440")
    popup.title("Borrow Book Transaction")

    form = ttk.Frame(popup, padding=25)
    form.pack(fill="both", expand=True)

    ttk.Label(form, text="📖 Issue / Borrow Book", font=("Helvetica", 16, "bold"), bootstyle="info").pack(pady=(0, 15))

    email_var, sku_var, days_var = StringVar(), StringVar(), StringVar(value="14")

    r1 = ttk.Frame(form)
    r1.pack(fill="x", pady=5)
    ttk.Label(r1, text="Member Email ID", font=("Helvetica", 9, "bold"), width=22).pack(side="left")
    ttk.Entry(r1, textvariable=email_var, font=("Helvetica", 10)).pack(side="left", fill="x", expand=True)

    r2 = ttk.Frame(form)
    r2.pack(fill="x", pady=5)
    ttk.Label(r2, text="Book SKU Number", font=("Helvetica", 9, "bold"), width=22).pack(side="left")
    ttk.Entry(r2, textvariable=sku_var, font=("Helvetica", 10)).pack(side="left", fill="x", expand=True, padx=(0, 5))
    ttk.Button(r2, text="📷 Scan", command=lambda: open_barcode_scanner(popup, lambda code: sku_var.set(code), "Scan Book SKU"), bootstyle="info-outline").pack(side="right")

    r3 = ttk.Frame(form)
    r3.pack(fill="x", pady=5)
    ttk.Label(r3, text="Borrow Duration (Days)", font=("Helvetica", 9, "bold"), width=22).pack(side="left")
    ttk.Entry(r3, textvariable=days_var, font=("Helvetica", 10)).pack(side="left", fill="x", expand=True)

    def submit():
        email = email_var.get().strip()
        sku = sku_var.get().strip()
        days = days_var.get().strip()

        if not email or not sku or not days:
            messagebox.showerror("Error", "All fields are required.")
            return

        user_data = get_user("Members", email=email)
        if not user_data or not isinstance(user_data, (list, tuple)):
            messagebox.showerror("Error", f"Member account with email '{email}' was not found.")
            return
        member_name = user_data[2]

        inv_items = get_book_inv(sku=sku)
        if not inv_items or not isinstance(inv_items, list):
            messagebox.showerror("Error", f"Inventory item with SKU '{sku}' not found.")
            return

        inv_record = inv_items[0]
        book_status = inv_record[2]
        isbn = inv_record[1]

        if book_status == "Borrowed":
            messagebox.showerror("Error", f"Book '{sku}' is already borrowed.")
            return
        if book_status in ("Lost", "Damaged"):
            messagebox.showerror("Error", f"Cannot borrow book '{sku}' because status is {book_status}.")
            return

        res = borrow_book(email, sku, member_name, isbn, days)
        if "successfully" in res.lower():
            messagebox.showinfo("Success", f"Book issued successfully to {member_name}!\nDue in {days} days.")
            popup.destroy()
            refresh()
        else:
            messagebox.showerror("Borrowing Error", res)

    btn_row = ttk.Frame(form)
    btn_row.pack(fill="x", pady=(20, 0))
    ttk.Button(btn_row, text="Confirm & Issue Book", command=submit, bootstyle="primary").pack(side="left", padx=5, expand=True, fill="x")
    ttk.Button(btn_row, text="Cancel", command=popup.destroy, bootstyle="secondary-outline").pack(side="left", padx=5)

def open_return_book(app, refresh):
    popup = ttk.Toplevel(app)
    popup.geometry("500x260")
    popup.title("Return Book")

    form = ttk.Frame(popup, padding=25)
    form.pack(fill="both", expand=True)

    ttk.Label(form, text="📥 Return Book to Library", font=("Helvetica", 16, "bold"), bootstyle="info").pack(pady=(0, 15))

    sku_var = StringVar()
    row = ttk.Frame(form)
    row.pack(fill="x", pady=10)
    ttk.Label(row, text="Book SKU Number", font=("Helvetica", 9, "bold"), width=18).pack(side="left")
    sku_entry = ttk.Entry(row, textvariable=sku_var, font=("Helvetica", 10))
    sku_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
    ttk.Button(row, text="📷 Scan", command=lambda: open_barcode_scanner(popup, lambda code: [sku_var.set(code), submit()], "Scan Return SKU"), bootstyle="info-outline").pack(side="right")

    def submit(event=None):
        sku = sku_var.get().strip()
        if not sku:
            messagebox.showerror("Error", "SKU number is required.")
            return

        res = return_book(sku)
        if "successfully" in res.lower():
            messagebox.showinfo("Book Returned", res)
            popup.destroy()
            refresh()
        else:
            messagebox.showerror("Return Error", res)

    sku_entry.bind("<Return>", submit)

    btn_row = ttk.Frame(form)
    btn_row.pack(fill="x", pady=(20, 0))
    ttk.Button(btn_row, text="Process Return", command=submit, bootstyle="success").pack(side="left", padx=5, expand=True, fill="x")
    ttk.Button(btn_row, text="Cancel", command=popup.destroy, bootstyle="secondary-outline").pack(side="left", padx=5)

def books_record(app, admin_email):
    container = ttk.Frame(app, padding=15)
    container.pack(fill="both", expand=True)

    top_bar = ttk.Frame(container)
    top_bar.pack(fill="x", pady=(0, 10))

    ttk.Label(top_bar, text="📋 Borrowing Transactions & Records", font=("Helvetica", 18, "bold"), bootstyle="info").pack(side="left")

    filter_frame = ttk.Frame(top_bar)
    filter_frame.pack(side="right")

    status_var = StringVar(value="All")
    status_combo = ttk.Combobox(filter_frame, textvariable=status_var, values=["All", "Borrowed", "Returned", "Lost"], width=10, state="readonly")
    status_combo.pack(side="left", padx=5)

    search_var = StringVar()
    search_entry = ttk.Entry(filter_frame, textvariable=search_var, font=("Helvetica", 10), width=18)
    search_entry.pack(side="left", padx=5)

    table_frame = ttk.Frame(container)
    table_frame.pack(fill="both", expand=True)

    columns = ("Record #", "SKU", "Status", "ISBN", "Borrower", "Email", "Days", "Due On", "Returned On", "Fine (₹)", "Points")
    table = ttk.Treeview(table_frame, columns=columns, show="headings", bootstyle="secondary")

    widths = {
        "Record #": 75,
        "SKU": 100,
        "Status": 90,
        "ISBN": 120,
        "Borrower": 150,
        "Email": 180,
        "Days": 65,
        "Due On": 100,
        "Returned On": 100,
        "Fine (₹)": 80,
        "Points": 65
    }

    for col in columns:
        table.heading(col, text=col)
        table.column(col, width=widths.get(col, 100), anchor="center")

    v_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview, bootstyle="round")
    h_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=table.xview, bootstyle="round")
    table.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

    table.pack(side="left", fill="both", expand=True)
    v_scroll.pack(side="right", fill="y")
    h_scroll.pack(side="bottom", fill="x")

    def populate(status_filter="All", query=None):
        table.delete(*table.get_children())
        filter_status = None if status_filter == "All" else status_filter
        records = get_record(status=filter_status)
        if not records:
            return

        q = query.lower().strip() if query else ""
        for r in records:
            rec_num = str(r[0])
            sku = str(r[1])
            status = str(r[2])
            isbn = str(r[3])
            email = str(r[4])
            borrower = str(r[5])
            points = str(r[6] or 0)
            days = str(r[7] or 0)
            fine = f"₹{float(r[9]):.2f}" if r[9] is not None else "₹0.00"
            due = str(r[10]) if r[10] else ""
            returned = str(r[11]) if r[11] else "Not yet returned"

            if q:
                match = (q in sku.lower() or q in email.lower() or q in borrower.lower() or q in isbn.lower())
                if not match:
                    continue

            table.insert("", "end", values=(rec_num, sku, status, isbn, borrower, email, days, due, returned, fine, points))

    def on_filter_change(event=None):
        populate(status_var.get(), search_var.get())

    def on_scan():
        open_barcode_scanner(app, lambda code: [search_var.set(code), populate(status_var.get(), code)], "Scan Barcode to Filter Records")

    status_combo.bind("<<ComboboxSelected>>", on_filter_change)
    search_entry.bind("<KeyRelease>", on_filter_change)
    ttk.Button(filter_frame, text="🔍 Search", command=on_filter_change, bootstyle="secondary-outline").pack(side="left", padx=2)
    ttk.Button(filter_frame, text="📷 Scan Barcode", command=on_scan, bootstyle="info-outline").pack(side="left", padx=2)

    btn_frame = ttk.Frame(container)
    btn_frame.pack(fill="x", pady=(10, 0))

    ttk.Button(btn_frame, text="📖 Issue / Borrow Book", command=lambda: open_borrow_book(app, on_filter_change), bootstyle="primary").pack(side="left", padx=5)
    ttk.Button(btn_frame, text="📥 Return Book", command=lambda: open_return_book(app, on_filter_change), bootstyle="success").pack(side="left", padx=5)
    ttk.Button(btn_frame, text="🔄 Refresh", command=lambda: [status_var.set("All"), search_var.set(""), populate()], bootstyle="secondary-outline").pack(side="right", padx=5)

    populate()
