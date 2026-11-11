import ttkbootstrap as ttk
from tkinter import messagebox
from ttkbootstrap.constants import *
from backend.account import get_user
from backend.bookrecord import get_record, overdue_books
from backend.inventory import get_book_inv
from backend.utils import update_time
from ui.common import create_card

def dashboard_content(app, email, db):
    if not app or db not in ["Librarian", "Members"]:
        messagebox.showerror("Error", "Application instance not found or invalid role.")
        return

    userDet = get_user(db, email=email)
    user_name = userDet[2] if (userDet and isinstance(userDet, (list, tuple)) and len(userDet) > 2) else email

    header_frame = ttk.Frame(app)
    header_frame.pack(fill="x", padx=20, pady=(15, 5))

    ttk.Label(header_frame, text=f"Welcome back, {user_name} 👋", font=("Helvetica", 20, "bold"), bootstyle="info").pack(anchor="w")
    time_label = ttk.Label(header_frame, font=("Helvetica", 10), bootstyle="secondary")
    time_label.pack(anchor="w", pady=(2, 0))
    update_time(time_label)

    summary_frame = ttk.Frame(app)
    summary_frame.pack(fill="x", padx=15, pady=15)

    content_frame = ttk.Frame(app)
    content_frame.pack(fill="both", expand=True, padx=20, pady=5)

    if db == "Librarian":
        borrowed_count = get_record(status="Borrowed", count=True)
        overdue_count = overdue_books(count=True)
        members_count = get_user(db="Members", count=True)
        shelved_count = get_book_inv(status="Shelved", count=True)

        create_card(summary_frame, "Currently Borrowed", borrowed_count)
        create_card(summary_frame, "Overdue Books", overdue_count)
        create_card(summary_frame, "Active Members", members_count)
        create_card(summary_frame, "Shelved in Bay", shelved_count)

        left_frame = ttk.Labelframe(content_frame, text="⚠️ Overdue Books", padding=10, bootstyle="warning")
        left_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=8, pady=8)

        overdue_cols = ("SKU", "Borrower", "Days Overdue", "Due Date", "Fine (₹)")
        overdue_tree = ttk.Treeview(left_frame, columns=overdue_cols, show="headings", bootstyle="warning")
        for col in overdue_cols:
            overdue_tree.heading(col, text=col)
            overdue_tree.column(col, anchor="center", stretch=True, width=110)

        overdue_scroll = ttk.Scrollbar(left_frame, orient="vertical", command=overdue_tree.yview)
        overdue_tree.configure(yscrollcommand=overdue_scroll.set)
        overdue_tree.pack(side="left", fill=BOTH, expand=True)
        overdue_scroll.pack(side="right", fill="y")

        overdue_list = overdue_books()
        if overdue_list:
            for rec in overdue_list:
                overdue_tree.insert("", "end", values=rec)
        else:
            overdue_tree.insert("", "end", values=("No overdue items", "-", "-", "-", "-"))

        right_frame = ttk.Labelframe(content_frame, text="📋 Recent Transactions", padding=10, bootstyle="info")
        right_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=8, pady=8)

        tx_cols = ("Record #", "SKU", "Status", "Member Name", "Due / Returned")
        tx_tree = ttk.Treeview(right_frame, columns=tx_cols, show="headings", bootstyle="info")
        for col in tx_cols:
            tx_tree.heading(col, text=col)
            tx_tree.column(col, anchor="center", stretch=True, width=110)

        tx_scroll = ttk.Scrollbar(right_frame, orient="vertical", command=tx_tree.yview)
        tx_tree.configure(yscrollcommand=tx_scroll.set)
        tx_tree.pack(side="left", fill=BOTH, expand=True)
        tx_scroll.pack(side="right", fill="y")

        all_records = get_record()
        if all_records:
            for rec in all_records[:25]:
                dt_info = str(rec[11]) if rec[11] else f"Due: {rec[10]}"
                tx_tree.insert("", "end", values=(rec[0], rec[1], rec[2], rec[5], dt_info))
        else:
            tx_tree.insert("", "end", values=("No records", "-", "-", "-", "-"))

    elif db == "Members":
        my_overdue = overdue_books(email=email, count=True)
        my_borrowed = get_record(email=email, status="Borrowed", count=True)
        points_val = userDet[6] if (userDet and isinstance(userDet, (list, tuple)) and len(userDet) > 6) else 0
        total_available = get_book_inv(status="Shelved", count=True)

        create_card(summary_frame, "My Overdue Books", my_overdue)
        create_card(summary_frame, "Currently Borrowed", my_borrowed)
        create_card(summary_frame, "ProPoints Balance", points_val)
        create_card(summary_frame, "Books in Library", total_available)

        left_frame = ttk.Labelframe(content_frame, text="⚠️ My Overdue Items", padding=10, bootstyle="warning")
        left_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=8, pady=8)

        m_overdue_cols = ("SKU", "Days Late", "Due Date", "Fine (₹)")
        m_overdue_tree = ttk.Treeview(left_frame, columns=m_overdue_cols, show="headings", bootstyle="warning")
        for col in m_overdue_cols:
            m_overdue_tree.heading(col, text=col)
            m_overdue_tree.column(col, anchor="center", stretch=True, width=120)

        m_scroll = ttk.Scrollbar(left_frame, orient="vertical", command=m_overdue_tree.yview)
        m_overdue_tree.configure(yscrollcommand=m_scroll.set)
        m_overdue_tree.pack(side="left", fill=BOTH, expand=True)
        m_scroll.pack(side="right", fill="y")

        user_overdue_items = overdue_books(email=email)
        if user_overdue_items:
            for rec in user_overdue_items:
                m_overdue_tree.insert("", "end", values=(rec[0], rec[2], str(rec[3]), f"₹{rec[4]}"))
        else:
            m_overdue_tree.insert("", "end", values=("No overdue books 🎉", "-", "-", "-"))

        right_frame = ttk.Labelframe(content_frame, text="📖 Currently Borrowed Books", padding=10, bootstyle="info")
        right_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=8, pady=8)

        b_cols = ("SKU", "ISBN", "Days Borrowed", "Due On")
        b_tree = ttk.Treeview(right_frame, columns=b_cols, show="headings", bootstyle="info")
        for col in b_cols:
            b_tree.heading(col, text=col)
            b_tree.column(col, anchor="center", stretch=True, width=120)

        b_scroll = ttk.Scrollbar(right_frame, orient="vertical", command=b_tree.yview)
        b_tree.configure(yscrollcommand=b_scroll.set)
        b_tree.pack(side="left", fill=BOTH, expand=True)
        b_scroll.pack(side="right", fill="y")

        borrowed_records = get_record(email=email, status="Borrowed")
        if borrowed_records:
            for rec in borrowed_records:
                b_tree.insert("", "end", values=(rec[1], rec[3], rec[7], str(rec[10])))
        else:
            b_tree.insert("", "end", values=("No active borrowings", "-", "-", "-"))
